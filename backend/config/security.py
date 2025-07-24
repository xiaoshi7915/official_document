"""
安全配置模块
实现敏感信息保护，包括环境变量管理、配置验证等
"""

import os
import secrets
from typing import Dict, Any, List
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import logging

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class SecurityConfig:
    """安全配置类"""
    
    # 从环境变量读取敏感信息
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    # 加密密钥（生产环境应使用密钥管理服务）
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    if not ENCRYPTION_KEY:
        ENCRYPTION_KEY = Fernet.generate_key().decode('utf-8')
        logger.warning("未设置ENCRYPTION_KEY，已自动生成新密钥")
    elif isinstance(ENCRYPTION_KEY, str):
        # 确保密钥是字节格式
        try:
            Fernet(ENCRYPTION_KEY.encode('utf-8'))
        except Exception:
            # 如果密钥无效，重新生成
            ENCRYPTION_KEY = Fernet.generate_key().decode('utf-8')
            logger.warning("ENCRYPTION_KEY无效，已重新生成新密钥")
    
    # 数据库配置
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', '47.118.250.53'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'database': os.getenv('DB_NAME', 'official_doc'),
        'user': os.getenv('DB_USER', 'official_doc'),
        'password': DB_PASSWORD,
        'charset': os.getenv('DB_CHARSET', 'utf8mb4')
    }
    
    # 数据库连接池配置（用于连接池时使用）
    DB_POOL_CONFIG = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20))
    }
    
    # API配置
    API_CONFIG = {
        'timeout': int(os.getenv('API_TIMEOUT', 30)),
        'max_retries': int(os.getenv('API_MAX_RETRIES', 3))
    }
    
    # MinIO配置
    MINIO_CONFIG = {
        'access_key': MINIO_ACCESS_KEY,
        'secret_key': MINIO_SECRET_KEY,
        'endpoint': os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
        'bucket': os.getenv('MINIO_BUCKET', 'knowledge-base'),
        'region': os.getenv('MINIO_REGION', 'us-east-1')
    }
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """验证关键配置是否存在，返回缺失的配置项列表"""
        missing_vars = []
        
        # 检查必需的配置项
        required_vars = [
            ('DEEPSEEK_API_KEY', cls.DEEPSEEK_API_KEY),
            ('DB_PASSWORD', cls.DB_PASSWORD),
            ('JWT_SECRET_KEY', cls.JWT_SECRET_KEY)
        ]
        
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        return missing_vars
    
    @classmethod
    def get_safe_config_dict(cls) -> Dict[str, Any]:
        """获取安全的配置字典（不包含敏感信息）"""
        return {
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'debug': os.getenv('DEBUG', 'true').lower() == 'true',
            'database': {
                'host': cls.DB_CONFIG['host'],
                'port': cls.DB_CONFIG['port'],
                'database': cls.DB_CONFIG['database'],
                'user': cls.DB_CONFIG['user'],
                'charset': cls.DB_CONFIG['charset'],
                'pool_size': cls.DB_POOL_CONFIG['pool_size']
            },
            'api': {
                'url': cls.DEEPSEEK_API_URL,
                'timeout': cls.API_CONFIG['timeout'],
                'max_retries': cls.API_CONFIG['max_retries']
            },
            'minio': {
                'endpoint': cls.MINIO_CONFIG['endpoint'],
                'bucket': cls.MINIO_CONFIG['bucket'],
                'region': cls.MINIO_CONFIG['region']
            },
            'file': {
                'upload_folder': os.getenv('UPLOAD_FOLDER', 'temp'),
                'max_file_size': int(os.getenv('MAX_FILE_SIZE', 52428800)),
                'allowed_extensions': os.getenv('ALLOWED_EXTENSIONS', '.pdf,.docx,.doc,.txt,.md').split(',')
            },
            'vector': {
                'model_path': os.getenv('MODEL_PATH'),
                'persist_directory': os.getenv('VECTOR_PERSIST_DIR', './vector_db'),
                'collection_name': os.getenv('VECTOR_COLLECTION_NAME', 'knowledge_chunks'),
                'chunk_size': int(os.getenv('CHUNK_SIZE', 1000)),
                'chunk_overlap': int(os.getenv('CHUNK_OVERLAP', 200)),
                'top_k': int(os.getenv('VECTOR_TOP_K', 5)),
                'similarity_threshold': float(os.getenv('SIMILARITY_THRESHOLD', 0.7))
            }
        }
    
    @classmethod
    def generate_secure_key(cls, key_type: str = 'jwt') -> str:
        """生成安全的密钥"""
        if key_type == 'jwt':
            return secrets.token_hex(32)
        elif key_type == 'encryption':
            return Fernet.generate_key().decode()
        else:
            raise ValueError(f"不支持的密钥类型: {key_type}")
    
    @classmethod
    def encrypt_sensitive_data(cls, data: str) -> str:
        """加密敏感数据"""
        if not cls.ENCRYPTION_KEY:
            raise ValueError("未设置加密密钥")
        
        f = Fernet(cls.ENCRYPTION_KEY.encode('utf-8'))
        return f.encrypt(data.encode()).decode()
    
    @classmethod
    def decrypt_sensitive_data(cls, encrypted_data: str) -> str:
        """解密敏感数据"""
        if not cls.ENCRYPTION_KEY:
            raise ValueError("未设置加密密钥")
        
        f = Fernet(cls.ENCRYPTION_KEY.encode('utf-8'))
        return f.decrypt(encrypted_data.encode()).decode()

# 初始化时验证配置
def init_security_config():
    """初始化安全配置"""
    missing_vars = SecurityConfig.validate_config()
    
    if missing_vars:
        logger.error(f"缺少必要的环境变量: {missing_vars}")
        logger.error("请检查 .env 文件或环境变量设置")
        raise ValueError(f"缺少必要的环境变量: {missing_vars}")
    
    logger.info("安全配置验证通过")
    logger.info(f"当前环境: {os.getenv('ENVIRONMENT', 'development')}")
    
    # 记录配置摘要（不包含敏感信息）
    config_summary = SecurityConfig.get_safe_config_dict()
    logger.info(f"配置摘要: {config_summary}")

# 导出配置实例
security_config = SecurityConfig() 