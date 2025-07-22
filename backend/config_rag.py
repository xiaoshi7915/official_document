"""
RAG知识库配置文件（简化版）
"""
import os

# MinIO配置
MINIO_CONFIG = {
    'endpoint': 'localhost:9000',
    'access_key': 'minioadmin',
    'secret_key': 'minioadmin',
    'secure': False,
    'bucket_name': 'knowledge-base'
}

# 向量数据库配置
VECTOR_DB_CONFIG = {
    'persist_directory': './vector_db',
    'collection_name': 'knowledge_chunks'
}

# 知识库配置
KNOWLEDGE_BASE_CONFIG = {
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'supported_file_types': ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.csv']
}

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'official_document',
    'charset': 'utf8mb4'
}

# 文件大小限制
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 支持的文件类型
SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.csv']
