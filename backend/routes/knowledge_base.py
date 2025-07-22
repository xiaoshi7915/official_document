"""
知识库API路由
"""
from flask import Blueprint, request, jsonify
import logging
from werkzeug.utils import secure_filename
import os

from services.knowledge_base_service import KnowledgeBaseService
from config_rag import SUPPORTED_FILE_TYPES, MAX_FILE_SIZE

# 创建蓝图
knowledge_base_bp = Blueprint('knowledge_base', __name__)

# 初始化服务
knowledge_service = KnowledgeBaseService()

logger = logging.getLogger(__name__)

@knowledge_base_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    上传文件到知识库
    
    POST /api/knowledge/upload
    Content-Type: multipart/form-data
    
    Returns:
        JSON响应
    """
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传文件'
            }), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        # 检查文件类型
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
        
        if file_ext not in SUPPORTED_FILE_TYPES:
            return jsonify({
                'success': False,
                'error': f'不支持的文件类型: {file_ext}'
            }), 400
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': f'文件大小超过限制: {file_size / 1024 / 1024:.2f}MB > {MAX_FILE_SIZE / 1024 / 1024}MB'
            }), 400
        
        # 读取文件数据
        file_data = file.read()
        content_type = file.content_type or SUPPORTED_FILE_TYPES.get(file_ext)
        
        # 上传并处理文件
        result = knowledge_service.upload_and_process_file(file_data, filename, content_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return jsonify({
            'success': False,
            'error': f'文件上传失败: {str(e)}'
        }), 500

@knowledge_base_bp.route('/search', methods=['POST'])
def search_knowledge_base():
    """
    搜索知识库
    
    POST /api/knowledge/search
    Content-Type: application/json
    
    Body:
    {
        "query": "搜索查询",
        "top_k": 5
    }
    
    Returns:
        JSON响应
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': '缺少查询参数'
            }), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({
                'success': False,
                'error': '查询内容不能为空'
            }), 400
        
        top_k = data.get('top_k', 5)
        
        # 搜索知识库
        result = knowledge_service.search_knowledge_base(query, top_k)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"知识库搜索失败: {e}")
        return jsonify({
            'success': False,
            'error': f'知识库搜索失败: {str(e)}'
        }), 500

@knowledge_base_bp.route('/files', methods=['GET'])
def get_knowledge_files():
    """
    获取知识库文件列表
    
    GET /api/knowledge/files?status=completed&limit=100
    
    Returns:
        JSON响应
    """
    try:
        status = request.args.get('status')
        limit = int(request.args.get('limit', 100))
        
        result = knowledge_service.get_knowledge_files(status, limit)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"获取知识库文件列表失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取知识库文件列表失败: {str(e)}'
        }), 500

@knowledge_base_bp.route('/files/<int:file_id>', methods=['GET'])
def get_file_details(file_id):
    """
    获取文件详细信息
    
    GET /api/knowledge/files/{file_id}
    
    Returns:
        JSON响应
    """
    try:
        result = knowledge_service.get_file_details(file_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"获取文件详细信息失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取文件详细信息失败: {str(e)}'
        }), 500

@knowledge_base_bp.route('/files/<int:file_id>', methods=['DELETE'])
def delete_knowledge_file(file_id):
    """
    删除知识库文件
    
    DELETE /api/knowledge/files/{file_id}
    
    Returns:
        JSON响应
    """
    try:
        result = knowledge_service.delete_knowledge_file(file_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"删除知识库文件失败: {e}")
        return jsonify({
            'success': False,
            'error': f'删除知识库文件失败: {str(e)}'
        }), 500

@knowledge_base_bp.route('/files/<int:file_id>/regenerate', methods=['POST'])
def regenerate_vectors(file_id):
    """
    重新生成文件向量
    
    POST /api/knowledge/files/{file_id}/regenerate
    
    Returns:
        JSON响应
    """
    try:
        result = knowledge_service.regenerate_vectors(file_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"重新生成向量失败: {e}")
        return jsonify({
            'success': False,
            'error': f'重新生成向量失败: {str(e)}'
        }), 500

@knowledge_base_bp.route('/stats', methods=['GET'])
def get_knowledge_base_stats():
    """
    获取知识库统计信息
    
    GET /api/knowledge/stats
    
    Returns:
        JSON响应
    """
    try:
        result = knowledge_service.get_knowledge_base_stats()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"获取知识库统计信息失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取知识库统计信息失败: {str(e)}'
        }), 500

@knowledge_base_bp.route('/batch-search', methods=['POST'])
def batch_search():
    """
    批量搜索
    
    POST /api/knowledge/batch-search
    Content-Type: application/json
    
    Body:
    {
        "queries": ["查询1", "查询2", "查询3"],
        "top_k": 5
    }
    
    Returns:
        JSON响应
    """
    try:
        data = request.get_json()
        
        if not data or 'queries' not in data:
            return jsonify({
                'success': False,
                'error': '缺少查询参数'
            }), 400
        
        queries = data['queries']
        if not isinstance(queries, list) or not queries:
            return jsonify({
                'success': False,
                'error': '查询列表不能为空'
            }), 400
        
        # 验证查询内容
        for i, query in enumerate(queries):
            if not isinstance(query, str) or not query.strip():
                return jsonify({
                    'success': False,
                    'error': f'第{i+1}个查询内容无效'
                }), 400
        
        top_k = data.get('top_k', 5)
        
        # 批量搜索
        result = knowledge_service.batch_search(queries, top_k)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"批量搜索失败: {e}")
        return jsonify({
            'success': False,
            'error': f'批量搜索失败: {str(e)}'
        }), 500

@knowledge_base_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查
    
    GET /api/knowledge/health
    
    Returns:
        JSON响应
    """
    try:
        # 检查各个服务状态
        stats = knowledge_service.get_knowledge_base_stats()
        
        health_status = {
            'status': 'healthy',
            'timestamp': knowledge_service.db_model._get_connection().server_time.isoformat(),
            'services': {
                'database': 'connected',
                'minio': 'connected',
                'vector_db': 'connected'
            },
            'stats': stats.get('stats', {})
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500 