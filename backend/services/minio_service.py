"""
MinIO S3服务类
用于文件存储和管理
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from minio import Minio
from minio.error import S3Error

from config_rag import MINIO_CONFIG, KNOWLEDGE_BASE_CONFIG

# 导入统一的日志管理器
try:
    from utils.logger import get_service_logger
    logger = get_service_logger('minio_service')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class MinioService:
    """MinIO S3服务类"""
    
    def __init__(self):
        """初始化MinIO客户端"""
        try:
            self.client = Minio(
                MINIO_CONFIG['endpoint'],
                access_key=MINIO_CONFIG['access_key'],
                secret_key=MINIO_CONFIG['secret_key'],
                secure=MINIO_CONFIG['secure'],
                region=MINIO_CONFIG['region']
            )
            self.bucket_name = KNOWLEDGE_BASE_CONFIG['bucket_name']
            self._ensure_bucket_exists()
            logger.info("MinIO客户端初始化成功")
        except Exception as e:
            logger.error(f"MinIO客户端初始化失败: {e}")
            raise
    
    def _ensure_bucket_exists(self):
        """确保存储桶存在"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"创建存储桶: {self.bucket_name}")
            else:
                logger.info(f"存储桶已存在: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"存储桶操作失败: {e}")
            raise
    
    def upload_file(self, file_path: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        上传文件到MinIO
        
        Args:
            file_path: 本地文件路径
            file_name: 存储的文件名，如果为None则使用原文件名
            
        Returns:
            包含文件信息的字典
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 生成唯一的文件名
            if file_name is None:
                file_name = os.path.basename(file_path)
            
            # 添加时间戳和UUID避免文件名冲突
            file_ext = os.path.splitext(file_name)[1]
            file_name_without_ext = os.path.splitext(file_name)[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            final_file_name = f"{file_name_without_ext}_{timestamp}_{unique_id}{file_ext}"
            
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            # 上传文件
            result = self.client.fput_object(
                self.bucket_name,
                final_file_name,
                file_path
            )
            
            file_info = {
                'file_name': final_file_name,
                'original_name': file_name,
                'file_size': file_size,
                'etag': result.etag,
                'version_id': result.version_id,
                'upload_time': datetime.now().isoformat(),
                'bucket_name': self.bucket_name
            }
            
            logger.info(f"文件上传成功: {final_file_name}")
            return file_info
            
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            raise
    
    def upload_file_data(self, file_data: bytes, file_name: str, content_type: str = None) -> Dict[str, Any]:
        """
        上传文件数据到MinIO
        
        Args:
            file_data: 文件数据
            file_name: 文件名
            content_type: 内容类型
            
        Returns:
            包含文件信息的字典
        """
        try:
            import io
            
            # 生成唯一的文件名
            file_ext = os.path.splitext(file_name)[1]
            file_name_without_ext = os.path.splitext(file_name)[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            final_file_name = f"{file_name_without_ext}_{timestamp}_{unique_id}{file_ext}"
            
            # 创建BytesIO对象
            data_stream = io.BytesIO(file_data)
            
            # 上传文件
            result = self.client.put_object(
                self.bucket_name,
                final_file_name,
                data_stream,
                len(file_data),
                content_type=content_type
            )
            
            file_info = {
                'file_name': final_file_name,
                'original_name': file_name,
                'file_size': len(file_data),
                'etag': result.etag,
                'version_id': result.version_id,
                'upload_time': datetime.now().isoformat(),
                'bucket_name': self.bucket_name,
                'content_type': content_type
            }
            
            logger.info(f"文件数据上传成功: {final_file_name}")
            return file_info
            
        except Exception as e:
            logger.error(f"文件数据上传失败: {e}")
            raise
    
    def download_file(self, file_name: str, local_path: str) -> bool:
        """
        从MinIO下载文件
        
        Args:
            file_name: 文件名
            local_path: 本地保存路径
            
        Returns:
            是否下载成功
        """
        try:
            self.client.fget_object(self.bucket_name, file_name, local_path)
            logger.info(f"文件下载成功: {file_name} -> {local_path}")
            return True
        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            return False
    
    def get_file_data(self, file_name: str) -> Optional[bytes]:
        """
        获取文件数据
        
        Args:
            file_name: 文件名
            
        Returns:
            文件数据
        """
        try:
            response = self.client.get_object(self.bucket_name, file_name)
            data = response.read()
            response.close()
            response.release_conn()
            logger.info(f"获取文件数据成功: {file_name}")
            return data
        except Exception as e:
            logger.error(f"获取文件数据失败: {e}")
            return None
    
    def delete_file(self, file_name: str) -> bool:
        """
        删除文件
        
        Args:
            file_name: 文件名
            
        Returns:
            是否删除成功
        """
        try:
            self.client.remove_object(self.bucket_name, file_name)
            logger.info(f"文件删除成功: {file_name}")
            return True
        except Exception as e:
            logger.error(f"文件删除失败: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """
        列出文件
        
        Args:
            prefix: 文件前缀
            
        Returns:
            文件列表
        """
        try:
            files = []
            objects = self.client.list_objects(self.bucket_name, prefix=prefix, recursive=True)
            
            for obj in objects:
                file_info = {
                    'file_name': obj.object_name,
                    'file_size': obj.size,
                    'last_modified': obj.last_modified.isoformat(),
                    'etag': obj.etag
                }
                files.append(file_info)
            
            logger.info(f"列出文件成功，共{len(files)}个文件")
            return files
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            return []
    
    def get_file_info(self, file_name: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            file_name: 文件名
            
        Returns:
            文件信息
        """
        try:
            stat = self.client.stat_object(self.bucket_name, file_name)
            file_info = {
                'file_name': stat.object_name,
                'file_size': stat.size,
                'last_modified': stat.last_modified.isoformat(),
                'etag': stat.etag,
                'content_type': stat.content_type
            }
            return file_info
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            return None
    
    def generate_presigned_url(self, file_name: str, expires: int = 3600) -> Optional[str]:
        """
        生成预签名URL
        
        Args:
            file_name: 文件名
            expires: 过期时间（秒）
            
        Returns:
            预签名URL
        """
        try:
            url = self.client.presigned_get_object(
                self.bucket_name,
                file_name,
                expires=timedelta(seconds=expires)
            )
            logger.info(f"生成预签名URL成功: {file_name}")
            return url
        except Exception as e:
            logger.error(f"生成预签名URL失败: {e}")
            return None
    
    def check_file_exists(self, file_name: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            file_name: 文件名
            
        Returns:
            文件是否存在
        """
        try:
            self.client.stat_object(self.bucket_name, file_name)
            return True
        except S3Error:
            return False
        except Exception as e:
            logger.error(f"检查文件存在性失败: {e}")
            return False 