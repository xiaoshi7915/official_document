"""
输入验证和清理模块
实现文件验证、XSS防护、SQL注入防护等安全功能
"""

import re
import os
import magic
import hashlib
from typing import List, Optional, Dict, Any, Tuple
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

class InputValidator:
    """输入验证器"""
    
    # 文件类型白名单
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.csv'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'text/plain',
        'text/markdown',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'text/csv',
        'application/octet-stream'  # 某些系统可能返回此类型
    }
    
    # 危险字符列表
    DANGEROUS_CHARS = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
    
    # 文件大小限制（50MB）
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    @classmethod
    def validate_filename(cls, filename: str) -> bool:
        """验证文件名安全性"""
        if not filename:
            logger.warning("文件名为空")
            return False
        
        # 检查文件扩展名
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            logger.warning(f"不支持的文件扩展名: {file_ext}")
            return False
        
        # 检查文件名是否包含危险字符
        for char in cls.DANGEROUS_CHARS:
            if char in filename:
                logger.warning(f"文件名包含危险字符: {char}")
                return False
        
        # 检查文件名长度
        if len(filename) > 255:
            logger.warning("文件名过长")
            return False
        
        return True
    
    @classmethod
    def validate_file_content(cls, file_path: str) -> bool:
        """验证文件内容类型"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"文件不存在: {file_path}")
                return False
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > cls.MAX_FILE_SIZE:
                logger.warning(f"文件过大: {file_size} bytes")
                return False
            
            # 检查MIME类型
            try:
                mime_type = magic.from_file(file_path, mime=True)
                if mime_type not in cls.ALLOWED_MIME_TYPES:
                    # 对于application/octet-stream，进一步检查文件扩展名
                    if mime_type == 'application/octet-stream':
                        file_ext = os.path.splitext(file_path)[1].lower()
                        if file_ext in cls.ALLOWED_EXTENSIONS:
                            logger.info(f"文件扩展名验证通过: {file_ext}")
                            return True
                    logger.warning(f"不支持的文件类型: {mime_type}")
                    return False
                return True
            except Exception as magic_error:
                logger.warning(f"MIME类型检测失败: {magic_error}，使用扩展名验证")
                # 如果MIME检测失败，使用扩展名验证
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext in cls.ALLOWED_EXTENSIONS:
                    logger.info(f"文件扩展名验证通过: {file_ext}")
                    return True
                return False
            
        except Exception as e:
            logger.error(f"文件内容验证失败: {e}")
            return False
    
    @classmethod
    def validate_file_size(cls, file_size: int) -> bool:
        """验证文件大小"""
        return file_size <= cls.MAX_FILE_SIZE
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """清理文件名"""
        if not filename:
            return ""
        
        # 获取文件扩展名
        name, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        # 验证扩展名
        if ext not in cls.ALLOWED_EXTENSIONS:
            return ""
        
        # 清理文件名（保留中文和基本字符）
        import re
        # 移除危险字符，但保留中文字符
        safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
        # 移除多余的空格和点
        safe_name = re.sub(r'\s+', '_', safe_name.strip())
        safe_name = re.sub(r'\.+', '.', safe_name)
        
        # 如果清理后为空，使用默认名称
        if not safe_name:
            safe_name = "uploaded_file"
        
        # 限制长度
        if len(safe_name) > 200:
            safe_name = safe_name[:200]
        
        return safe_name + ext
    
    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """清理文本输入，防止XSS"""
        if not text:
            return ""
        
        import html
        
        # HTML转义
        text = html.escape(text)
        
        # 移除危险脚本标签
        text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<iframe.*?</iframe>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<object.*?</object>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<embed.*?>', '', text, flags=re.IGNORECASE)
        
        # 移除JavaScript事件处理器
        text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
        
        # 移除危险协议
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'data:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'vbscript:', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    @classmethod
    def sanitize_sql_input(cls, text: str) -> str:
        """清理SQL输入，防止SQL注入"""
        if not text:
            return ""
        
        # 移除SQL注入相关的危险字符和模式
        dangerous_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
            r'(\b(or|and)\b\s+\d+\s*=\s*\d+)',
            r'(\b(or|and)\b\s+\'\w+\'\s*=\s*\'\w+\')',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(from|into|where|set|values)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(table|database|schema|user|password)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(information_schema|sys|mysql|sqlite)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(version|user|database|schema|table|column)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(load_file|into\s+outfile|into\s+dumpfile)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(concat|group_concat|substring|substr|mid|left|right)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(hex|unhex|bin|unbin|oct|unoct)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(cast|convert|char|ascii|ord|chr)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(sleep|benchmark|get_lock|release_lock)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(load_file|into\s+outfile|into\s+dumpfile)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(concat|group_concat|substring|substr|mid|left|right)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(hex|unhex|bin|unbin|oct|unoct)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(cast|convert|char|ascii|ord|chr)\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(sleep|benchmark|get_lock|release_lock)\b)',
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 移除注释
        text = re.sub(r'--.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        text = re.sub(r'#.*$', '', text, flags=re.MULTILINE)
        
        # 移除分号（防止多语句执行）
        text = text.replace(';', '')
        
        return text.strip()
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """验证邮箱格式"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """验证手机号格式"""
        if not phone:
            return False
        
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    @classmethod
    def validate_url(cls, url: str) -> bool:
        """验证URL格式"""
        if not url:
            return False
        
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    @classmethod
    def generate_file_hash(cls, file_path: str) -> str:
        """生成文件哈希值"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"生成文件哈希失败: {e}")
            return ""

class FileUploadValidator:
    """文件上传验证器"""
    
    @classmethod
    def validate_upload(cls, file, max_size: int = None) -> Tuple[bool, str]:
        """验证文件上传"""
        if not file:
            return False, "没有文件"
        
        if not file.filename:
            return False, "文件名不能为空"
        
        # 验证文件名
        if not InputValidator.validate_filename(file.filename):
            return False, "文件名不合法"
        
        # 验证文件大小
        max_size = max_size or InputValidator.MAX_FILE_SIZE
        if file.content_length and file.content_length > max_size:
            return False, f"文件过大，最大允许 {max_size / (1024*1024):.1f}MB"
        
        return True, "验证通过"
    
    @classmethod
    def save_and_validate_file(cls, file, upload_folder: str) -> Tuple[bool, str, str]:
        """保存并验证文件"""
        try:
            # 验证上传
            is_valid, message = cls.validate_upload(file)
            if not is_valid:
                return False, message, ""
            
            # 清理文件名
            safe_filename = InputValidator.sanitize_filename(file.filename)
            if not safe_filename:
                return False, "文件名清理失败", ""
            
            # 确保上传目录存在
            os.makedirs(upload_folder, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(upload_folder, safe_filename)
            file.save(file_path)
            
            # 验证文件内容
            if not InputValidator.validate_file_content(file_path):
                # 删除危险文件
                os.remove(file_path)
                return False, "文件内容验证失败", ""
            
            return True, "文件保存成功", file_path
            
        except Exception as e:
            logger.error(f"文件保存失败: {e}")
            return False, f"文件保存失败: {str(e)}", ""

class ContentValidator:
    """内容验证器"""
    
    @classmethod
    def validate_document_data(cls, data: Dict[str, Any]) -> Tuple[bool, str]:
        """验证文档数据"""
        required_fields = ['document_type', 'topic', 'title']
        
        for field in required_fields:
            if not data.get(field):
                return False, f"缺少必需字段: {field}"
        
        # 验证字段长度
        if len(data.get('title', '')) > 200:
            return False, "标题过长，最大200字符"
        
        if len(data.get('topic', '')) > 500:
            return False, "主题过长，最大500字符"
        
        # 清理文本内容
        for field in ['title', 'topic', 'content']:
            if field in data and data[field]:
                data[field] = InputValidator.sanitize_text(data[field])
        
        return True, "验证通过"
    
    @classmethod
    def validate_search_query(cls, query: str) -> Tuple[bool, str]:
        """验证搜索查询"""
        if not query or not query.strip():
            return False, "搜索查询不能为空"
        
        if len(query.strip()) > 1000:
            return False, "搜索查询过长，最大1000字符"
        
        # 清理查询内容
        clean_query = InputValidator.sanitize_text(query.strip())
        
        return True, clean_query 