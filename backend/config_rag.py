"""
RAG知识库配置文件（完整版）
"""
import os

# MinIO配置
MINIO_CONFIG = {
    'endpoint': 'localhost:9000',
    'access_key': 'minioadmin',
    'secret_key': 'minioadmin',
    'secure': False,
    'bucket_name': 'knowledge-base',
    'region': 'us-east-1'
}

# 向量数据库配置
VECTOR_DB_CONFIG = {
    'type': 'chroma',  # 数据库类型
    'persist_directory': './vector_db',
    'collection_name': 'knowledge_chunks'
}

# 知识库配置
KNOWLEDGE_BASE_CONFIG = {
    'bucket_name': 'knowledge-base',
    'region': 'us-east-1',
    'embedding_model': '/opt/official_ai_writer/official_document/models/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'top_k': 5,  # 检索结果数量
    'similarity_threshold': 0.7,  # 相似度阈值
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'supported_file_types': ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.csv']
}

# 数据库配置
DB_CONFIG = {
    'host': '47.118.250.53',
    'user': 'official_doc',
    'password': 'admin123456!',
    'database': 'official_doc',
    'charset': 'utf8mb4'
}

# 文件大小限制
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 支持的文件类型
SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.csv']
