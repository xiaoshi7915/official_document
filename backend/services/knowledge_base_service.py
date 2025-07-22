"""
知识库管理服务
整合文件上传、解析、向量化和检索功能
"""
import os
import hashlib
import tempfile
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import threading
import time

from services.minio_service import MinioService
from services.document_parser import DocumentParser
from services.vector_service import VectorService
from models.knowledge_base import KnowledgeBaseModel
from config_rag import MAX_FILE_SIZE

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    """知识库管理服务类"""
    
    def __init__(self):
        """初始化知识库服务"""
        try:
            # 初始化各个服务
            self.minio_service = MinioService()
            self.document_parser = DocumentParser()
            self.vector_service = VectorService()
            self.db_model = KnowledgeBaseModel()
            
            # 创建数据库表
            self.db_model.create_tables()
            
            # 处理队列
            self.processing_queue = {}
            self.processing_lock = threading.Lock()
            
            logger.info("知识库管理服务初始化成功")
            
        except Exception as e:
            logger.error(f"知识库管理服务初始化失败: {e}")
            raise
    
    def upload_and_process_file(self, file_data: bytes, file_name: str, content_type: str = None) -> Dict[str, Any]:
        """
        上传并处理文件
        
        Args:
            file_data: 文件数据
            file_name: 文件名
            content_type: 内容类型
            
        Returns:
            处理结果
        """
        try:
            # 1. 验证文件
            validation_result = self.document_parser.validate_file(file_data, file_name)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # 2. 上传文件到MinIO
            file_info = self.minio_service.upload_file_data(file_data, file_name, content_type)
            
            # 3. 计算内容哈希
            content_hash = hashlib.md5(file_data).hexdigest()
            
            # 4. 准备数据库记录
            db_file_info = {
                'file_name': file_info['file_name'],
                'original_name': file_info['original_name'],
                'file_type': validation_result['file_type'],
                'file_size': file_info['file_size'],
                'file_path': file_info['file_name'],  # MinIO中的路径
                'content_hash': content_hash,
                'upload_time': file_info['upload_time'],
                'metadata': validation_result['metadata']
            }
            
            # 5. 插入数据库记录
            file_id = self.db_model.insert_knowledge_file(db_file_info)
            
            # 6. 异步处理文档
            self._process_document_async(file_id, file_data, file_name, content_type)
            
            return {
                'success': True,
                'file_id': file_id,
                'file_name': file_info['file_name'],
                'original_name': file_info['original_name'],
                'status': 'processing',
                'message': '文件上传成功，正在处理中...'
            }
            
        except Exception as e:
            logger.error(f"文件上传处理失败: {e}")
            return {
                'success': False,
                'error': f"文件上传处理失败: {str(e)}"
            }
    
    def _process_document_async(self, file_id: int, file_data: bytes, file_name: str, content_type: str = None):
        """
        异步处理文档
        
        Args:
            file_id: 文件ID
            file_data: 文件数据
            file_name: 文件名
            content_type: 内容类型
        """
        def process_task():
            try:
                logger.info(f"开始处理文档，文件ID: {file_id}")
                
                # 1. 解析文档内容
                parse_result = self.document_parser.parse_document(file_data, file_name, content_type)
                
                if not parse_result['parse_success']:
                    self.db_model.update_file_status(file_id, 'failed', {
                        'error': parse_result['error_message']
                    })
                    return
                
                # 2. 文本分块
                chunks = self.vector_service.chunk_text(parse_result['content'], file_name)
                
                # 3. 添加到向量数据库
                vector_ids = self.vector_service.add_documents_to_vector_db(chunks, str(file_id))
                
                # 4. 保存文档块到数据库
                for i, chunk in enumerate(chunks):
                    chunk['vector_id'] = vector_ids[i] if i < len(vector_ids) else ''
                
                self.db_model.insert_document_chunks(file_id, chunks)
                
                # 5. 更新文件状态
                self.db_model.update_file_status(file_id, 'completed', {
                    'chunk_count': len(chunks),
                    'vector_count': len(vector_ids),
                    'content_length': parse_result['content_length']
                })
                
                logger.info(f"文档处理完成，文件ID: {file_id}")
                
            except Exception as e:
                logger.error(f"文档处理失败，文件ID: {file_id}, 错误: {e}")
                self.db_model.update_file_status(file_id, 'failed', {
                    'error': str(e)
                })
        
        # 启动异步处理线程
        thread = threading.Thread(target=process_task)
        thread.daemon = True
        thread.start()
    
    def search_knowledge_base(self, query: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        搜索知识库
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            搜索结果
        """
        try:
            start_time = time.time()
            
            # 1. 向量搜索
            similar_docs = self.vector_service.search_similar_documents(query, top_k)
            
            # 2. 记录检索日志
            response_time = int((time.time() - start_time) * 1000)
            self.db_model.insert_retrieval_log({
                'query_text': query,
                'retrieved_chunks': similar_docs,
                'document_type': 'knowledge_base',
                'response_time_ms': response_time
            })
            
            # 3. 构建搜索结果
            results = []
            for doc in similar_docs:
                result = {
                    'content': doc['document'],
                    'file_name': doc['metadata']['file_name'],
                    'similarity_score': doc['similarity_score'],
                    'rank': doc['rank'],
                    'metadata': doc['metadata']
                }
                results.append(result)
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'total_results': len(results),
                'response_time_ms': response_time
            }
            
        except Exception as e:
            logger.error(f"知识库搜索失败: {e}")
            return {
                'success': False,
                'error': f"知识库搜索失败: {str(e)}",
                'results': [],
                'total_results': 0
            }
    
    def get_knowledge_files(self, status: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """
        获取知识库文件列表
        
        Args:
            status: 状态过滤
            limit: 限制数量
            
        Returns:
            文件列表
        """
        try:
            files = self.db_model.get_knowledge_files(status, limit)
            
            return {
                'success': True,
                'files': files,
                'total_files': len(files)
            }
            
        except Exception as e:
            logger.error(f"获取知识库文件列表失败: {e}")
            return {
                'success': False,
                'error': f"获取知识库文件列表失败: {str(e)}",
                'files': [],
                'total_files': 0
            }
    
    def get_file_details(self, file_id: int) -> Dict[str, Any]:
        """
        获取文件详细信息
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件详细信息
        """
        try:
            # 获取文件信息
            file_info = self.db_model.get_file_by_id(file_id)
            if not file_info:
                return {
                    'success': False,
                    'error': '文件不存在'
                }
            
            # 获取文档块信息
            chunks = self.db_model.get_document_chunks(file_id)
            
            return {
                'success': True,
                'file_info': file_info,
                'chunks': chunks,
                'chunk_count': len(chunks)
            }
            
        except Exception as e:
            logger.error(f"获取文件详细信息失败: {e}")
            return {
                'success': False,
                'error': f"获取文件详细信息失败: {str(e)}"
            }
    
    def delete_knowledge_file(self, file_id: int) -> Dict[str, Any]:
        """
        删除知识库文件
        
        Args:
            file_id: 文件ID
            
        Returns:
            删除结果
        """
        try:
            # 获取文件信息
            file_info = self.db_model.get_file_by_id(file_id)
            if not file_info:
                return {
                    'success': False,
                    'error': '文件不存在'
                }
            
            # 1. 删除MinIO中的文件
            self.minio_service.delete_file(file_info['file_path'])
            
            # 2. 删除向量数据库中的向量
            self.vector_service.delete_document_vectors(str(file_id))
            
            # 3. 删除数据库记录
            success = self.db_model.delete_knowledge_file(file_id)
            
            if success:
                return {
                    'success': True,
                    'message': '文件删除成功'
                }
            else:
                return {
                    'success': False,
                    'error': '文件删除失败'
                }
                
        except Exception as e:
            logger.error(f"删除知识库文件失败: {e}")
            return {
                'success': False,
                'error': f"删除知识库文件失败: {str(e)}"
            }
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息
        """
        try:
            # 获取数据库统计
            db_stats = self.db_model.get_retrieval_stats()
            
            # 获取向量数据库统计
            vector_stats = self.vector_service.get_vector_db_stats()
            
            # 获取MinIO文件列表
            minio_files = self.minio_service.list_files()
            
            stats = {
                'total_files': len(minio_files),
                'total_vectors': vector_stats['total_vectors'],
                'total_queries': db_stats['total_queries'],
                'avg_response_time': db_stats['avg_response_time'],
                'embedding_model': vector_stats['embedding_model'],
                'document_type_stats': db_stats['document_type_stats']
            }
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"获取知识库统计信息失败: {e}")
            return {
                'success': False,
                'error': f"获取知识库统计信息失败: {str(e)}",
                'stats': {}
            }
    
    def regenerate_vectors(self, file_id: int) -> Dict[str, Any]:
        """
        重新生成向量
        
        Args:
            file_id: 文件ID
            
        Returns:
            处理结果
        """
        try:
            # 获取文件信息
            file_info = self.db_model.get_file_by_id(file_id)
            if not file_info:
                return {
                    'success': False,
                    'error': '文件不存在'
                }
            
            # 获取文件数据
            file_data = self.minio_service.get_file_data(file_info['file_path'])
            if not file_data:
                return {
                    'success': False,
                    'error': '无法获取文件数据'
                }
            
            # 重新处理文档
            self._process_document_async(file_id, file_data, file_info['original_name'])
            
            return {
                'success': True,
                'message': '向量重新生成任务已启动'
            }
            
        except Exception as e:
            logger.error(f"重新生成向量失败: {e}")
            return {
                'success': False,
                'error': f"重新生成向量失败: {str(e)}"
            }
    
    def batch_search(self, queries: List[str], top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        批量搜索
        
        Args:
            queries: 查询列表
            top_k: 每个查询返回结果数量
            
        Returns:
            批量搜索结果
        """
        try:
            start_time = time.time()
            
            # 批量搜索
            all_results = self.vector_service.batch_search(queries, top_k)
            
            response_time = int((time.time() - start_time) * 1000)
            
            # 构建结果
            results = []
            for i, query_results in enumerate(all_results):
                query_result = {
                    'query': queries[i],
                    'results': query_results,
                    'total_results': len(query_results)
                }
                results.append(query_result)
            
            return {
                'success': True,
                'queries': queries,
                'results': results,
                'response_time_ms': response_time
            }
            
        except Exception as e:
            logger.error(f"批量搜索失败: {e}")
            return {
                'success': False,
                'error': f"批量搜索失败: {str(e)}",
                'results': []
            } 