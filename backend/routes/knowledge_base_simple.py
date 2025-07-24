"""
简化的知识库API路由
集成MinerU解析和向量数据库
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import hashlib
from datetime import datetime
import tempfile
import docx
import json
import threading
import time

# 导入自定义服务
from services.mineru_parser import MinerUParser
from services.vector_service import VectorService
from models.knowledge_management import KnowledgeManagementModel

# 导入统一的日志管理器
try:
    from utils.logger import get_route_logger
    logger = get_route_logger('knowledge_base_simple')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# 创建蓝图
knowledge_base_simple_bp = Blueprint('knowledge_base_simple', __name__)

# 支持的文件类型
SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.csv']
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 知识库文件存储目录
KNOWLEDGE_DIR = 'knowledge_files'
if not os.path.exists(KNOWLEDGE_DIR):
    os.makedirs(KNOWLEDGE_DIR)

# 初始化服务
mineru_parser = MinerUParser()
vector_service = VectorService()
db_model = KnowledgeManagementModel()

@knowledge_base_simple_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    上传文件到知识库（集成MinerU解析和向量数据库）
    
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
        file_ext = os.path.splitext(filename)[1].lower()
        
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
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = hashlib.md5(file_data).hexdigest()[:8]
        file_name_without_ext = os.path.splitext(filename)[0]
        final_filename = f"{file_name_without_ext}_{timestamp}_{unique_id}{file_ext}"
        
        # 保存文件到本地
        file_path = os.path.join(KNOWLEDGE_DIR, final_filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # 准备文件信息
        file_info = {
            'file_name': final_filename,
            'original_name': filename,
            'file_type': file_ext,
            'file_size': file_size,
            'file_path': file_path,
            'content_hash': hashlib.md5(file_data).hexdigest(),
            'upload_time': datetime.now().isoformat(),
            'status': 'processing'
        }
        
        # 插入数据库记录
        file_id = db_model.insert_knowledge_file(file_info)
        
        if not file_id:
            return jsonify({
                'success': False,
                'error': '数据库插入失败'
            }), 500
        
        # 异步处理文档
        def process_document():
            try:
                logger.info(f"开始处理文档: {file_id}")
                
                # 1. 使用MinerU解析文档
                parse_result = mineru_parser.parse_document(file_data, filename)
                
                if not parse_result['success']:
                    db_model.update_file_status(file_id, 'failed', {
                        'error': parse_result['error'],
                        'parse_status': 'failed'
                    })
                    return
                
                # 2. 更新解析状态
                db_model.update_file_status(file_id, 'processing', {
                    'parse_status': 'completed',
                    'content_length': parse_result['content_length'],
                    'metadata': parse_result['metadata']
                })
                
                # 3. 文本分块
                chunks = mineru_parser.chunk_text(parse_result['content'])
                
                if not chunks:
                    db_model.update_file_status(file_id, 'failed', {
                        'error': '文本分块失败',
                        'parse_status': 'completed',
                        'vector_status': 'failed'
                    })
                    return
                
                # 4. 添加到向量数据库
                vector_ids = vector_service.add_documents_to_vector_db(chunks, file_id)
                
                if not vector_ids:
                    db_model.update_file_status(file_id, 'failed', {
                        'error': '向量化失败',
                        'parse_status': 'completed',
                        'vector_status': 'failed'
                    })
                    return
                
                # 5. 保存文档块到数据库
                for i, chunk in enumerate(chunks):
                    chunk['vector_id'] = vector_ids[i] if i < len(vector_ids) else ''
                
                db_model.insert_document_chunks(file_id, chunks)
                
                # 6. 更新最终状态
                db_model.update_file_status(file_id, 'completed', {
                    'parse_status': 'completed',
                    'vector_status': 'completed',
                    'chunk_count': len(chunks),
                    'vector_count': len(vector_ids),
                    'content_length': parse_result['content_length']
                })
                
                logger.info(f"文档处理完成: {file_id}")
                
            except Exception as e:
                logger.error(f"文档处理失败: {file_id}, 错误: {e}")
                db_model.update_file_status(file_id, 'failed', {
                    'error': str(e),
                    'parse_status': 'failed',
                    'vector_status': 'failed'
                })
        
        # 启动异步处理线程
        thread = threading.Thread(target=process_document)
        thread.daemon = True
        thread.start()
        
        logger.info(f"文件上传成功: {final_filename}, 开始异步处理")
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'file_name': final_filename,
            'original_name': filename,
            'status': 'processing',
            'message': '文件上传成功，正在处理中...'
        }), 200
        
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return jsonify({
            'success': False,
            'error': f'文件上传失败: {str(e)}'
        }), 500

@knowledge_base_simple_bp.route('/files', methods=['GET'])
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
        
        files = db_model.get_knowledge_files(status, limit)
        
        return jsonify({
            'success': True,
            'files': files,
            'total': len(files)
        }), 200
        
    except Exception as e:
        logger.error(f"获取文件列表失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取文件列表失败: {str(e)}'
        }), 500

@knowledge_base_simple_bp.route('/files/<file_id>', methods=['DELETE'])
def delete_knowledge_file(file_id):
    """
    删除知识库文件
    
    DELETE /api/knowledge/files/<file_id>
    
    Returns:
        JSON响应
    """
    try:
        # 获取文件信息
        files = db_model.get_knowledge_files()
        file_info = None
        for file in files:
            if file['file_id'] == file_id:
                file_info = file
                break
        
        if not file_info:
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
        
        # 删除向量数据库中的文档块
        vector_service.delete_file_chunks(file_id)
        
        # 删除实际文件
        if os.path.exists(file_info['file_path']):
            os.remove(file_info['file_path'])
        
        # 删除数据库记录（通过外键约束自动删除相关记录）
        # 这里需要在数据库模型中添加删除方法
        
        logger.info(f"文件删除成功: {file_info['file_name']}")
        
        return jsonify({
            'success': True,
            'message': '文件删除成功'
        }), 200
        
    except Exception as e:
        logger.error(f"删除文件失败: {e}")
        return jsonify({
            'success': False,
            'error': f'删除文件失败: {str(e)}'
        }), 500

@knowledge_base_simple_bp.route('/search', methods=['POST'])
def search_knowledge_base():
    """
    搜索知识库
    
    POST /api/knowledge/search
    Content-Type: application/json
    
    Body:
    {
        "query": "搜索查询",
        "top_k": 5,
        "file_ids": ["file_id1", "file_id2"]
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
        file_ids = data.get('file_ids')
        
        # 搜索向量数据库
        similar_chunks = vector_service.search_similar_chunks(query, top_k, file_ids)
        
        # 更新使用统计
        for chunk in similar_chunks:
            if 'file_id' in chunk['metadata']:
                db_model.update_usage_stats(chunk['metadata']['file_id'])
        
        return jsonify({
            'success': True,
            'query': query,
            'results': similar_chunks,
            'total': len(similar_chunks)
        }), 200
        
    except Exception as e:
        logger.error(f"知识库搜索失败: {e}")
        return jsonify({
            'success': False,
            'error': f'知识库搜索失败: {str(e)}'
        }), 500

@knowledge_base_simple_bp.route('/stats', methods=['GET'])
def get_knowledge_stats():
    """
    获取知识库统计信息
    
    GET /api/knowledge/stats
    
    Returns:
        JSON响应
    """
    try:
        # 获取数据库统计
        files = db_model.get_knowledge_files()
        
        # 获取向量数据库统计
        vector_stats = vector_service.get_collection_stats()
        
        # 统计状态分布
        status_stats = {}
        for file in files:
            status = file.get('status', 'unknown')
            status_stats[status] = status_stats.get(status, 0) + 1
        
        stats = {
            'total_files': len(files),
            'status_distribution': status_stats,
            'vector_stats': vector_stats,
            'storage_dir': KNOWLEDGE_DIR
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取统计信息失败: {str(e)}'
        }), 500

@knowledge_base_simple_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查
    
    GET /api/knowledge/health
    
    Returns:
        JSON响应
    """
    try:
        # 检查存储目录
        if not os.path.exists(KNOWLEDGE_DIR):
            os.makedirs(KNOWLEDGE_DIR)
        
        # 统计文件数量
        files = db_model.get_knowledge_files()
        file_count = len(files)
        
        # 检查向量数据库
        vector_stats = vector_service.get_collection_stats()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'file_count': file_count,
            'vector_chunks': vector_stats['total_chunks'],
            'storage_dir': KNOWLEDGE_DIR
        }), 200
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500 