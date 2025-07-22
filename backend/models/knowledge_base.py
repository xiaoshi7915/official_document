"""
知识库数据库模型
"""
import mysql.connector
from datetime import datetime
from typing import List, Dict, Optional, Any
import json
import logging

from config import DB_CONFIG

logger = logging.getLogger(__name__)

class KnowledgeBaseModel:
    """知识库数据库模型类"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.db_config = DB_CONFIG
    
    def _get_connection(self):
        """获取数据库连接"""
        try:
            return mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as err:
            logger.error(f"数据库连接错误: {err}")
            raise
    
    def create_tables(self):
        """创建知识库相关表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 知识库文件表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_files (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    file_name VARCHAR(255) NOT NULL,
                    original_name VARCHAR(255) NOT NULL,
                    file_type VARCHAR(50) NOT NULL,
                    file_size BIGINT NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    content_hash VARCHAR(64) NOT NULL,
                    upload_time DATETIME NOT NULL,
                    status ENUM('processing', 'completed', 'failed') DEFAULT 'processing',
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_file_name (file_name),
                    INDEX idx_status (status),
                    INDEX idx_upload_time (upload_time)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 文档块表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    file_id INT NOT NULL,
                    chunk_index INT NOT NULL,
                    chunk_text TEXT NOT NULL,
                    chunk_size INT NOT NULL,
                    vector_id VARCHAR(255),
                    embedding_data JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES knowledge_files(id) ON DELETE CASCADE,
                    INDEX idx_file_id (file_id),
                    INDEX idx_chunk_index (chunk_index),
                    INDEX idx_vector_id (vector_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 检索记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS retrieval_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    retrieved_chunks JSON,
                    document_type VARCHAR(50),
                    user_id VARCHAR(100),
                    response_time_ms INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_query_text (query_text(100)),
                    INDEX idx_document_type (document_type),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("知识库数据库表创建成功")
            
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise
    
    def insert_knowledge_file(self, file_info: Dict[str, Any]) -> int:
        """
        插入知识库文件记录
        
        Args:
            file_info: 文件信息字典
            
        Returns:
            文件ID
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            sql = """
                INSERT INTO knowledge_files 
                (file_name, original_name, file_type, file_size, file_path, content_hash, upload_time, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                file_info['file_name'],
                file_info['original_name'],
                file_info['file_type'],
                file_info['file_size'],
                file_info['file_path'],
                file_info.get('content_hash', ''),
                file_info['upload_time'],
                json.dumps(file_info.get('metadata', {}))
            )
            
            cursor.execute(sql, values)
            file_id = cursor.lastrowid
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"知识库文件记录插入成功，ID: {file_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"插入知识库文件记录失败: {e}")
            raise
    
    def update_file_status(self, file_id: int, status: str, metadata: Dict[str, Any] = None):
        """
        更新文件状态
        
        Args:
            file_id: 文件ID
            status: 状态
            metadata: 元数据
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if metadata:
                sql = """
                    UPDATE knowledge_files 
                    SET status = %s, metadata = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                values = (status, json.dumps(metadata), file_id)
            else:
                sql = """
                    UPDATE knowledge_files 
                    SET status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                values = (status, file_id)
            
            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"文件状态更新成功，ID: {file_id}, 状态: {status}")
            
        except Exception as e:
            logger.error(f"更新文件状态失败: {e}")
            raise
    
    def insert_document_chunks(self, file_id: int, chunks: List[Dict[str, Any]]):
        """
        插入文档块记录
        
        Args:
            file_id: 文件ID
            chunks: 文档块列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            sql = """
                INSERT INTO document_chunks 
                (file_id, chunk_index, chunk_text, chunk_size, vector_id, embedding_data)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            values_list = []
            for chunk in chunks:
                values = (
                    file_id,
                    chunk['chunk_index'],
                    chunk['chunk_text'],
                    chunk['chunk_size'],
                    chunk.get('vector_id', ''),
                    json.dumps(chunk.get('embedding_data', {}))
                )
                values_list.append(values)
            
            cursor.executemany(sql, values_list)
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"文档块插入成功，文件ID: {file_id}, 块数: {len(chunks)}")
            
        except Exception as e:
            logger.error(f"插入文档块失败: {e}")
            raise
    
    def get_knowledge_files(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取知识库文件列表
        
        Args:
            status: 状态过滤
            limit: 限制数量
            
        Returns:
            文件列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            if status:
                sql = """
                    SELECT * FROM knowledge_files 
                    WHERE status = %s 
                    ORDER BY upload_time DESC 
                    LIMIT %s
                """
                cursor.execute(sql, (status, limit))
            else:
                sql = """
                    SELECT * FROM knowledge_files 
                    ORDER BY upload_time DESC 
                    LIMIT %s
                """
                cursor.execute(sql, (limit,))
            
            files = cursor.fetchall()
            
            # 解析JSON字段
            for file in files:
                if file.get('metadata'):
                    file['metadata'] = json.loads(file['metadata'])
            
            cursor.close()
            conn.close()
            
            return files
            
        except Exception as e:
            logger.error(f"获取知识库文件列表失败: {e}")
            return []
    
    def get_file_by_id(self, file_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取文件信息
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件信息
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = "SELECT * FROM knowledge_files WHERE id = %s"
            cursor.execute(sql, (file_id,))
            
            file = cursor.fetchone()
            
            if file and file.get('metadata'):
                file['metadata'] = json.loads(file['metadata'])
            
            cursor.close()
            conn.close()
            
            return file
            
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            return None
    
    def get_document_chunks(self, file_id: int) -> List[Dict[str, Any]]:
        """
        获取文档块列表
        
        Args:
            file_id: 文件ID
            
        Returns:
            文档块列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                SELECT * FROM document_chunks 
                WHERE file_id = %s 
                ORDER BY chunk_index
            """
            cursor.execute(sql, (file_id,))
            
            chunks = cursor.fetchall()
            
            # 解析JSON字段
            for chunk in chunks:
                if chunk.get('embedding_data'):
                    chunk['embedding_data'] = json.loads(chunk['embedding_data'])
            
            cursor.close()
            conn.close()
            
            return chunks
            
        except Exception as e:
            logger.error(f"获取文档块失败: {e}")
            return []
    
    def delete_knowledge_file(self, file_id: int) -> bool:
        """
        删除知识库文件
        
        Args:
            file_id: 文件ID
            
        Returns:
            是否删除成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 删除文档块（外键约束会自动删除）
            sql = "DELETE FROM knowledge_files WHERE id = %s"
            cursor.execute(sql, (file_id,))
            
            affected_rows = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            success = affected_rows > 0
            if success:
                logger.info(f"知识库文件删除成功，ID: {file_id}")
            else:
                logger.warning(f"知识库文件不存在，ID: {file_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"删除知识库文件失败: {e}")
            return False
    
    def insert_retrieval_log(self, log_info: Dict[str, Any]):
        """
        插入检索日志
        
        Args:
            log_info: 日志信息
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            sql = """
                INSERT INTO retrieval_logs 
                (query_text, retrieved_chunks, document_type, user_id, response_time_ms)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            values = (
                log_info['query_text'],
                json.dumps(log_info.get('retrieved_chunks', [])),
                log_info.get('document_type', ''),
                log_info.get('user_id', ''),
                log_info.get('response_time_ms', 0)
            )
            
            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("检索日志插入成功")
            
        except Exception as e:
            logger.error(f"插入检索日志失败: {e}")
    
    def get_retrieval_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        获取检索统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            统计信息
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 总检索次数
            sql1 = """
                SELECT COUNT(*) as total_queries 
                FROM retrieval_logs 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            cursor.execute(sql1, (days,))
            total_queries = cursor.fetchone()['total_queries']
            
            # 平均响应时间
            sql2 = """
                SELECT AVG(response_time_ms) as avg_response_time 
                FROM retrieval_logs 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            cursor.execute(sql2, (days,))
            avg_response_time = cursor.fetchone()['avg_response_time'] or 0
            
            # 文档类型分布
            sql3 = """
                SELECT document_type, COUNT(*) as count 
                FROM retrieval_logs 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY document_type
            """
            cursor.execute(sql3, (days,))
            document_type_stats = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                'total_queries': total_queries,
                'avg_response_time': round(avg_response_time, 2),
                'document_type_stats': document_type_stats
            }
            
        except Exception as e:
            logger.error(f"获取检索统计失败: {e}")
            return {
                'total_queries': 0,
                'avg_response_time': 0,
                'document_type_stats': []
            }