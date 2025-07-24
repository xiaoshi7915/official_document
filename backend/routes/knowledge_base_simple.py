"""
简化的知识库API路由
不依赖MinIO，使用本地文件系统
"""
from flask import Blueprint, request, jsonify
import logging
from werkzeug.utils import secure_filename
import os
import hashlib
from datetime import datetime
import tempfile
import docx
import json

# 创建蓝图
knowledge_base_simple_bp = Blueprint('knowledge_base_simple', __name__)

logger = logging.getLogger(__name__)

# 支持的文件类型
SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.csv']
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 知识库文件存储目录
KNOWLEDGE_DIR = 'knowledge_files'
if not os.path.exists(KNOWLEDGE_DIR):
    os.makedirs(KNOWLEDGE_DIR)

@knowledge_base_simple_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    上传文件到知识库（简化版）
    
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
        file_ext = os.path.splitext(filename)[1]
        file_name_without_ext = os.path.splitext(filename)[0]
        final_filename = f"{file_name_without_ext}_{timestamp}_{unique_id}{file_ext}"
        
        # 保存文件到本地
        file_path = os.path.join(KNOWLEDGE_DIR, final_filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # 解析文件内容
        content = ""
        try:
            if file_ext == '.docx':
                doc = docx.Document(file_path)
                content = '\n'.join([para.text for para in doc.paragraphs])
            elif file_ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = f"文件类型 {file_ext} 暂不支持内容解析"
        except Exception as parse_error:
            logger.error(f"文件解析错误: {parse_error}")
            content = f"文件解析失败: {str(parse_error)}"
        
        # 保存文件信息到JSON文件
        file_info = {
            'file_id': unique_id,
            'file_name': final_filename,
            'original_name': filename,
            'file_type': file_ext,
            'file_size': file_size,
            'file_path': file_path,
            'content_hash': hashlib.md5(file_data).hexdigest(),
            'upload_time': datetime.now().isoformat(),
            'content_length': len(content),
            'status': 'completed'
        }
        
        info_file_path = os.path.join(KNOWLEDGE_DIR, f"{unique_id}.json")
        with open(info_file_path, 'w', encoding='utf-8') as f:
            json.dump(file_info, f, ensure_ascii=False, indent=2)
        
        logger.info(f"文件上传成功: {final_filename}, 内容长度: {len(content)}")
        
        return jsonify({
            'success': True,
            'file_id': unique_id,
            'file_name': final_filename,
            'original_name': filename,
            'status': 'completed',
            'message': '文件上传成功，已保存到知识库',
            'content_length': len(content)
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
    
    GET /api/knowledge/files
    
    Returns:
        JSON响应
    """
    try:
        files = []
        
        # 读取所有JSON信息文件
        for filename in os.listdir(KNOWLEDGE_DIR):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(KNOWLEDGE_DIR, filename), 'r', encoding='utf-8') as f:
                        file_info = json.load(f)
                        files.append(file_info)
                except Exception as e:
                    logger.error(f"读取文件信息失败 {filename}: {e}")
        
        # 按上传时间排序
        files.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
        
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
        # 查找对应的JSON文件
        json_file_path = os.path.join(KNOWLEDGE_DIR, f"{file_id}.json")
        
        if not os.path.exists(json_file_path):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
        
        # 读取文件信息
        with open(json_file_path, 'r', encoding='utf-8') as f:
            file_info = json.load(f)
        
        # 删除实际文件
        if os.path.exists(file_info['file_path']):
            os.remove(file_info['file_path'])
        
        # 删除JSON信息文件
        os.remove(json_file_path)
        
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
        file_count = len([f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith('.json')])
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'file_count': file_count,
            'storage_dir': KNOWLEDGE_DIR
        }), 200
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500 