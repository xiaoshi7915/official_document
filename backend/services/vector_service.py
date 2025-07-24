"""
向量数据库服务
使用ChromaDB进行向量存储和检索
"""
import os
import logging
from typing import Dict, List, Any, Optional
import chromadb
from chromadb.config import Settings
import numpy as np
from sentence_transformers import SentenceTransformer
import json

logger = logging.getLogger(__name__)

class VectorService:
    """向量数据库服务"""
    
    def __init__(self):
        """初始化向量服务"""
        try:
            # 初始化ChromaDB
            self.persist_directory = "./vector_db"
            if not os.path.exists(self.persist_directory):
                os.makedirs(self.persist_directory)
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 初始化嵌入模型
            model_path = "/opt/official_ai_writer/official_document/models/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            if os.path.exists(model_path):
                self.embedding_model = SentenceTransformer(model_path)
                logger.info(f"使用本地嵌入模型: {model_path}")
            else:
                # 如果本地模型不存在，使用在线模型
                self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("使用在线嵌入模型")
            
            # 获取或创建集合
            self.collection_name = "knowledge_chunks"
            try:
                self.collection = self.client.get_collection(self.collection_name)
                logger.info(f"获取现有集合: {self.collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "知识库文档块向量存储"}
                )
                logger.info(f"创建新集合: {self.collection_name}")
            
            logger.info("向量数据库服务初始化成功")
            
        except Exception as e:
            logger.error(f"向量数据库服务初始化失败: {e}")
            raise
    
    def add_documents_to_vector_db(self, chunks: List[Dict[str, Any]], file_id: str) -> List[str]:
        """
        将文档块添加到向量数据库
        
        Args:
            chunks: 文档块列表
            file_id: 文件ID
            
        Returns:
            向量ID列表
        """
        try:
            if not chunks:
                logger.warning("没有文档块需要添加")
                return []
            
            # 准备数据
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_id}_chunk_{i}"
                
                documents.append(chunk['content'])
                metadatas.append({
                    'file_id': file_id,
                    'chunk_index': i,
                    'chunk_size': chunk.get('size', len(chunk['content'])),
                    'start': chunk.get('start', 0),
                    'end': chunk.get('end', len(chunk['content']))
                })
                ids.append(chunk_id)
            
            # 添加到向量数据库
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"成功添加 {len(chunks)} 个文档块到向量数据库")
            return ids
            
        except Exception as e:
            logger.error(f"添加文档块到向量数据库失败: {e}")
            return []
    
    def search_similar_chunks(self, query: str, top_k: int = 5, file_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        搜索相似文档块
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            file_ids: 限制搜索的文件ID列表
            
        Returns:
            相似文档块列表
        """
        try:
            # 构建查询条件
            where = None
            if file_ids:
                where = {"file_id": {"$in": file_ids}}
            
            # 执行搜索
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where
            )
            
            # 格式化结果
            similar_chunks = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    similar_chunks.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0,
                        'id': results['ids'][0][i] if results['ids'] and results['ids'][0] else ''
                    })
            
            logger.info(f"搜索到 {len(similar_chunks)} 个相似文档块")
            return similar_chunks
            
        except Exception as e:
            logger.error(f"搜索相似文档块失败: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            count = self.collection.count()
            
            # 获取所有文档的元数据
            results = self.collection.get()
            
            # 统计文件数量
            file_ids = set()
            if results['metadatas']:
                for metadata in results['metadatas']:
                    if metadata and 'file_id' in metadata:
                        file_ids.add(metadata['file_id'])
            
            return {
                'total_chunks': count,
                'total_files': len(file_ids),
                'file_ids': list(file_ids)
            }
            
        except Exception as e:
            logger.error(f"获取集合统计信息失败: {e}")
            return {
                'total_chunks': 0,
                'total_files': 0,
                'file_ids': []
            }
    
    def delete_file_chunks(self, file_id: str) -> bool:
        """
        删除指定文件的所有文档块
        
        Args:
            file_id: 文件ID
            
        Returns:
            是否成功
        """
        try:
            # 删除指定文件ID的所有文档块
            self.collection.delete(
                where={"file_id": file_id}
            )
            
            logger.info(f"成功删除文件 {file_id} 的所有文档块")
            return True
            
        except Exception as e:
            logger.error(f"删除文件文档块失败: {e}")
            return False
    
    def get_file_chunks(self, file_id: str) -> List[Dict[str, Any]]:
        """
        获取指定文件的所有文档块
        
        Args:
            file_id: 文件ID
            
        Returns:
            文档块列表
        """
        try:
            results = self.collection.get(
                where={"file_id": file_id}
            )
            
            chunks = []
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    chunks.append({
                        'content': doc,
                        'metadata': results['metadatas'][i] if results['metadatas'] else {},
                        'id': results['ids'][i] if results['ids'] else ''
                    })
            
            # 按chunk_index排序
            chunks.sort(key=lambda x: x['metadata'].get('chunk_index', 0))
            
            logger.info(f"获取到文件 {file_id} 的 {len(chunks)} 个文档块")
            return chunks
            
        except Exception as e:
            logger.error(f"获取文件文档块失败: {e}")
            return []
    
    def update_chunk_metadata(self, chunk_id: str, metadata: Dict[str, Any]) -> bool:
        """
        更新文档块元数据
        
        Args:
            chunk_id: 文档块ID
            metadata: 新的元数据
            
        Returns:
            是否成功
        """
        try:
            # 获取现有文档块
            results = self.collection.get(ids=[chunk_id])
            
            if not results['documents']:
                logger.warning(f"文档块不存在: {chunk_id}")
                return False
            
            # 更新元数据
            self.collection.update(
                ids=[chunk_id],
                metadatas=[metadata]
            )
            
            logger.info(f"成功更新文档块元数据: {chunk_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新文档块元数据失败: {e}")
            return False
    
    def clear_collection(self) -> bool:
        """清空集合"""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "知识库文档块向量存储"}
            )
            
            logger.info("成功清空向量数据库集合")
            return True
            
        except Exception as e:
            logger.error(f"清空集合失败: {e}")
            return False 