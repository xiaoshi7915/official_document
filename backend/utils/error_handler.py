"""
全局异常处理模块
实现统一的异常处理机制，提供详细的错误信息和日志记录
"""

from flask import jsonify, request
from werkzeug.exceptions import HTTPException
import traceback
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class CustomException(Exception):
    """自定义异常基类"""
    def __init__(self, message: str, error_code: str = None, status_code: int = 500, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "CUSTOM_ERROR"
        self.status_code = status_code
        self.details = details or {}

class ValidationError(CustomException):
    """验证错误"""
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "VALIDATION_ERROR", 400, details)
        self.field = field

class ResourceNotFoundError(CustomException):
    """资源未找到错误"""
    def __init__(self, resource: str, resource_id: str = None, details: Dict[str, Any] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message, "RESOURCE_NOT_FOUND", 404, details)

class ServiceUnavailableError(CustomException):
    """服务不可用错误"""
    def __init__(self, service: str, reason: str = None, details: Dict[str, Any] = None):
        message = f"{service} service unavailable"
        if reason:
            message += f": {reason}"
        super().__init__(message, "SERVICE_UNAVAILABLE", 503, details)

class AuthenticationError(CustomException):
    """认证错误"""
    def __init__(self, message: str = "Authentication failed", details: Dict[str, Any] = None):
        super().__init__(message, "AUTHENTICATION_ERROR", 401, details)

class AuthorizationError(CustomException):
    """授权错误"""
    def __init__(self, message: str = "Insufficient permissions", details: Dict[str, Any] = None):
        super().__init__(message, "AUTHORIZATION_ERROR", 403, details)

class RateLimitError(CustomException):
    """频率限制错误"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, details: Dict[str, Any] = None):
        super().__init__(message, "RATE_LIMIT_ERROR", 429, details)
        self.retry_after = retry_after

class FileUploadError(CustomException):
    """文件上传错误"""
    def __init__(self, message: str, file_name: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "FILE_UPLOAD_ERROR", 400, details)
        self.file_name = file_name

class DatabaseError(CustomException):
    """数据库错误"""
    def __init__(self, message: str, operation: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "DATABASE_ERROR", 500, details)
        self.operation = operation

class APIError(CustomException):
    """API调用错误"""
    def __init__(self, message: str, api_name: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "API_ERROR", 500, details)
        self.api_name = api_name

def create_error_response(error: Exception, include_traceback: bool = False) -> Dict[str, Any]:
    """创建统一的错误响应格式"""
    response = {
        'success': False,
        'timestamp': datetime.now().isoformat(),
        'path': request.path,
        'method': request.method,
        'error_message': str(error)
    }
    
    # 添加自定义异常信息
    if isinstance(error, CustomException):
        response.update({
            'error_code': error.error_code,
            'status_code': error.status_code,
            'details': error.details
        })
        
        # 添加字段特定信息
        if hasattr(error, 'field') and error.field:
            response['field'] = error.field
        
        if hasattr(error, 'file_name') and error.file_name:
            response['file_name'] = error.file_name
        
        if hasattr(error, 'operation') and error.operation:
            response['operation'] = error.operation
        
        if hasattr(error, 'api_name') and error.api_name:
            response['api_name'] = error.api_name
        
        if hasattr(error, 'retry_after') and error.retry_after:
            response['retry_after'] = error.retry_after
    
    # 添加HTTP异常信息
    elif isinstance(error, HTTPException):
        response.update({
            'error_code': 'HTTP_ERROR',
            'status_code': error.code,
            'details': {'description': error.description}
        })
    
    # 添加通用异常信息
    else:
        response.update({
            'error_code': 'INTERNAL_ERROR',
            'status_code': 500,
            'details': {}
        })
    
    # 在开发环境中添加堆栈跟踪
    if include_traceback:
        response['traceback'] = traceback.format_exc()
    
    return response

def log_error(error: Exception, request_data: Dict[str, Any] = None):
    """记录错误日志"""
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'path': request.path,
        'method': request.method,
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'request_data': request_data or {}
    }
    
    # 添加自定义异常信息
    if isinstance(error, CustomException):
        error_info.update({
            'error_code': error.error_code,
            'status_code': error.status_code,
            'details': error.details
        })
    
    # 记录错误日志
    logger.error(f"异常详情: {error_info}", exc_info=True)

def register_error_handlers(app):
    """注册全局错误处理器"""
    
    @app.errorhandler(CustomException)
    def handle_custom_exception(error):
        """处理自定义异常"""
        response = create_error_response(error)
        log_error(error)
        return jsonify(response), error.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """处理HTTP异常"""
        response = create_error_response(error)
        log_error(error)
        return jsonify(response), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """处理通用异常"""
        include_traceback = app.debug
        response = create_error_response(error, include_traceback)
        log_error(error)
        return jsonify(response), 500
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """处理404错误"""
        response = {
            'success': False,
            'error_code': 'NOT_FOUND',
            'error_message': '请求的资源不存在',
            'status_code': 404,
            'timestamp': datetime.now().isoformat(),
            'path': request.path,
            'method': request.method,
            'available_endpoints': [
                '/api/knowledge/upload',
                '/api/knowledge/files',
                '/api/knowledge/files/<file_id>',
                '/api/rag/generate-with-rag',
                '/api/rag/generate-outline',
                '/api/rag/search-context',
                '/api/health',
                '/api/config/status'
            ]
        }
        return jsonify(response), 404
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """处理400错误（包括SSL/TLS协议错误）"""
        error_message = str(error)
        
        # 检查是否是SSL/TLS协议错误
        if "Bad request version" in error_message or "SSL" in error_message.upper():
            response = {
                'success': False,
                'error_code': 'SSL_TLS_ERROR',
                'error_message': '检测到SSL/TLS协议错误，请使用HTTP协议访问',
                'status_code': 400,
                'timestamp': datetime.now().isoformat(),
                'path': request.path,
                'method': request.method,
                'details': {
                    'suggestion': '请确保使用HTTP协议而不是HTTPS协议访问API',
                    'correct_url': f"http://{request.host}{request.path}"
                }
            }
        else:
            response = create_error_response(error)
        
        log_error(error)
        return jsonify(response), 400

# 便捷的错误创建函数
def create_validation_error(message: str, field: str = None, details: Dict[str, Any] = None) -> ValidationError:
    """创建验证错误"""
    return ValidationError(message, field, details)

def create_not_found_error(resource: str, resource_id: str = None, details: Dict[str, Any] = None) -> ResourceNotFoundError:
    """创建资源未找到错误"""
    return ResourceNotFoundError(resource, resource_id, details)

def create_service_error(service: str, reason: str = None, details: Dict[str, Any] = None) -> ServiceUnavailableError:
    """创建服务不可用错误"""
    return ServiceUnavailableError(service, reason, details)

def create_auth_error(message: str = "Authentication failed", details: Dict[str, Any] = None) -> AuthenticationError:
    """创建认证错误"""
    return AuthenticationError(message, details)

def create_authz_error(message: str = "Insufficient permissions", details: Dict[str, Any] = None) -> AuthorizationError:
    """创建授权错误"""
    return AuthorizationError(message, details)

def create_rate_limit_error(message: str = "Rate limit exceeded", retry_after: int = None, details: Dict[str, Any] = None) -> RateLimitError:
    """创建频率限制错误"""
    return RateLimitError(message, retry_after, details)

def create_file_upload_error(message: str, file_name: str = None, details: Dict[str, Any] = None) -> FileUploadError:
    """创建文件上传错误"""
    return FileUploadError(message, file_name, details)

def create_database_error(message: str, operation: str = None, details: Dict[str, Any] = None) -> DatabaseError:
    """创建数据库错误"""
    return DatabaseError(message, operation, details)

def create_api_error(message: str, api_name: str = None, details: Dict[str, Any] = None) -> APIError:
    """创建API错误"""
    return APIError(message, api_name, details) 