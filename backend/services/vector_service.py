"""
向量化服务类
实现文档向量化和检索功能
"""
import os
import json
import hashlib
from typing import List, Dict, Optional, Any, Tuple
import logging
import numpy as np
from datetime import datetime

# 向量化相关库
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

from config_rag import KNOWLEDGE_BASE_CONFIG, VECTOR_DB_CONFIG

logger = logging.getLogger(__name__)

class VectorService:
    """向量化服务类"""
    
    def __init__(self):
        """初始化向量化服务"""
        try:
            # 初始化向量模型
            self.embedding_model = SentenceTransformer(KNOWLEDGE_BASE_CONFIG['embedding_model'])
            logger.info(f"向量模型加载成功: {KNOWLEDGE_BASE_CONFIG['embedding_model']}")
            
            # 初始化向量数据库
            self._init_vector_db()
            
            # 配置参数
            self.chunk_size = KNOWLEDGE_BASE_CONFIG['chunk_size']
            self.chunk_overlap = KNOWLEDGE_BASE_CONFIG['chunk_overlap']
            self.top_k = KNOWLEDGE_BASE_CONFIG['top_k']
            self.similarity_threshold = KNOWLEDGE_BASE_CONFIG['similarity_threshold']
            
        except Exception as e:
            logger.error(f"向量化服务初始化失败: {e}")
            raise
    
    def _init_vector_db(self):
        """初始化向量数据库"""
        try:
            if VECTOR_DB_CONFIG['type'] == 'chroma':
                # 确保持久化目录存在
                persist_dir = VECTOR_DB_CONFIG['persist_directory']
                os.makedirs(persist_dir, exist_ok=True)
                
                # 初始化ChromaDB客户端
                self.vector_db = chromadb.PersistentClient(
                    path=persist_dir,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                
                # 获取或创建集合
                self.collection = self.vector_db.get_or_create_collection(
                    name=VECTOR_DB_CONFIG['collection_name'],
                    metadata={"hnsw:space": "cosine"}
                )
                
                logger.info(f"ChromaDB初始化成功，集合: {VECTOR_DB_CONFIG['collection_name']}")
            else:
                raise ValueError(f"不支持的向量数据库类型: {VECTOR_DB_CONFIG['type']}")
                
        except Exception as e:
            logger.error(f"向量数据库初始化失败: {e}")
            raise
    
    def chunk_text(self, text: str, file_name: str) -> List[Dict[str, Any]]:
        """
        文本分块
        
        Args:
            text: 文本内容
            file_name: 文件名
            
        Returns:
            文本块列表
        """
        try:
            chunks = []
            words = text.split()
            
            if len(words) <= self.chunk_size:
                # 文本较短，直接作为一个块
                chunk = {
                    'chunk_index': 0,
                    'chunk_text': text,
                    'chunk_size': len(words),
                    'file_name': file_name
                }
                chunks.append(chunk)
            else:
                # 文本较长，需要分块
                chunk_index = 0
                start = 0
                
                while start < len(words):
                    end = min(start + self.chunk_size, len(words))
                    chunk_words = words[start:end]
                    chunk_text = ' '.join(chunk_words)
                    
                    chunk = {
                        'chunk_index': chunk_index,
                        'chunk_text': chunk_text,
                        'chunk_size': len(chunk_words),
                        'file_name': file_name
                    }
                    chunks.append(chunk)
                    
                    # 计算下一个块的起始位置（考虑重叠）
                    start = end - self.chunk_overlap
                    chunk_index += 1
                    
                    # 避免无限循环
                    if start >= len(words) - self.chunk_overlap:
                        break
            
            logger.info(f"文本分块完成，文件: {file_name}, 块数: {len(chunks)}")
            return chunks
            
        except Exception as e:
            logger.error(f"文本分块失败: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        生成文本向量
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表
        """
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            
            # 转换为列表格式
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()
            
            logger.info(f"向量生成成功，文本数量: {len(texts)}")
            return embeddings
            
        except Exception as e:
            logger.error(f"向量生成失败: {e}")
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
                return []
            
            # 提取文本内容
            texts = [chunk['chunk_text'] for chunk in chunks]
            
            # 生成向量
            embeddings = self.generate_embeddings(texts)
            
            # 生成向量ID
            vector_ids = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                # 生成唯一的向量ID
                vector_id = f"{file_id}_{chunk['chunk_index']}_{hashlib.md5(chunk['chunk_text'].encode()).hexdigest()[:8]}"
                vector_ids.append(vector_id)
                
                # 构建元数据
                metadata = {
                    'file_id': file_id,
                    'file_name': chunk['file_name'],
                    'chunk_index': chunk['chunk_index'],
                    'chunk_size': chunk['chunk_size'],
                    'upload_time': datetime.now().isoformat()
                }
                metadatas.append(metadata)
            
            # 添加到向量数据库
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=vector_ids
            )
            
            logger.info(f"文档块添加到向量数据库成功，文件ID: {file_id}, 块数: {len(chunks)}")
            return vector_ids
            
        except Exception as e:
            logger.error(f"添加文档块到向量数据库失败: {e}")
            raise
    
    def search_similar_documents(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        搜索相似文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            相似文档列表
        """
        try:
            if top_k is None:
                top_k = self.top_k
            
            # 生成查询向量
            query_embedding = self.generate_embeddings([query])[0]
            
            # 搜索相似文档
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # 处理搜索结果
            similar_docs = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # 计算相似度分数（距离转换为相似度）
                    similarity_score = 1 - distance
                    
                    # 过滤低相似度的结果
                    if similarity_score >= self.similarity_threshold:
                        similar_doc = {
                            'document': doc,
                            'metadata': metadata,
                            'similarity_score': round(similarity_score, 4),
                            'rank': i + 1
                        }
                        similar_docs.append(similar_doc)
            
            logger.info(f"文档搜索完成，查询: {query[:50]}..., 结果数: {len(similar_docs)}")
            return similar_docs
            
        except Exception as e:
            logger.error(f"文档搜索失败: {e}")
            return []
    
    def delete_document_vectors(self, file_id: str) -> bool:
        """
        删除文档向量
        
        Args:
            file_id: 文件ID
            
        Returns:
            是否删除成功
        """
        try:
            # 查询该文件的所有向量
            results = self.collection.get(
                where={"file_id": file_id}
            )
            
            if results['ids']:
                # 删除向量
                self.collection.delete(ids=results['ids'])
                logger.info(f"文档向量删除成功，文件ID: {file_id}, 向量数: {len(results['ids'])}")
                return True
            else:
                logger.warning(f"未找到文档向量，文件ID: {file_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除文档向量失败: {e}")
            return False
    
    def get_vector_db_stats(self) -> Dict[str, Any]:
        """
        获取向量数据库统计信息
        
        Returns:
            统计信息
        """
        try:
            # 获取集合信息
            collection_info = self.collection.get()
            
            # 统计文件数量
            file_ids = set()
            for metadata in collection_info['metadatas']:
                if metadata and 'file_id' in metadata:
                    file_ids.add(metadata['file_id'])
            
            stats = {
                'total_vectors': len(collection_info['ids']),
                'total_files': len(file_ids),
                'collection_name': self.collection.name,
                'embedding_model': KNOWLEDGE_BASE_CONFIG['embedding_model']
            }
            
            logger.info(f"向量数据库统计信息: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"获取向量数据库统计信息失败: {e}")
            return {
                'total_vectors': 0,
                'total_files': 0,
                'collection_name': 'unknown',
                'embedding_model': 'unknown'
            }
    
    def update_document_vectors(self, file_id: str, chunks: List[Dict[str, Any]]) -> bool:
        """
        更新文档向量
        
        Args:
            file_id: 文件ID
            chunks: 新的文档块列表
            
        Returns:
            是否更新成功
        """
        try:
            # 先删除旧的向量
            self.delete_document_vectors(file_id)
            
            # 添加新的向量
            self.add_documents_to_vector_db(chunks, file_id)
            
            logger.info(f"文档向量更新成功，文件ID: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新文档向量失败: {e}")
            return False
    
    def batch_search(self, queries: List[str], top_k: Optional[int] = None) -> List[List[Dict[str, Any]]]:
        """
        批量搜索
        
        Args:
            queries: 查询列表
            top_k: 每个查询返回结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            if top_k is None:
                top_k = self.top_k
            
            # 生成查询向量
            query_embeddings = self.generate_embeddings(queries)
            
            # 批量搜索
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # 处理搜索结果
            all_results = []
            for query_idx, query in enumerate(queries):
                query_results = []
                if results['documents'] and results['documents'][query_idx]:
                    for i, (doc, metadata, distance) in enumerate(zip(
                        results['documents'][query_idx],
                        results['metadatas'][query_idx],
                        results['distances'][query_idx]
                    )):
                        similarity_score = 1 - distance
                        if similarity_score >= self.similarity_threshold:
                            similar_doc = {
                                'document': doc,
                                'metadata': metadata,
                                'similarity_score': round(similarity_score, 4),
                                'rank': i + 1
                            }
                            query_results.append(similar_doc)
                
                all_results.append(query_results)
            
            logger.info(f"批量搜索完成，查询数: {len(queries)}")
            return all_results
            
        except Exception as e:
            logger.error(f"批量搜索失败: {e}")
            return [[] for _ in queries] 