from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
import os
import json
import logging
from werkzeug.utils import secure_filename
import requests
from datetime import datetime
import tempfile
import docx
from docx import Document
from docx.shared import Inches

import logging
from logging.handlers import RotatingFileHandler

# 配置日志
if not os.path.exists('logs'):
    os.makedirs('logs')
    
# 创建日志文件处理器
file_handler = RotatingFileHandler('logs/backend.log', maxBytes=10485760, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# 获取Flask日志记录器
logger = logging.getLogger('backend')
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

try:
    from config import DB_CONFIG, DEEPSEEK_API_URL, DEEPSEEK_API_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
except ImportError:
    # 如果导入失败，尝试使用相对导入
    from backend.config import DB_CONFIG, DEEPSEEK_API_URL, DEEPSEEK_API_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS

app = Flask(__name__)
CORS(app)

# 添加请求日志中间件
@app.before_request
def log_request_info():
    logger.debug('请求头: %s', request.headers)
    logger.debug('请求体: %s', request.get_data())

# 添加响应日志中间件
@app.after_request
def log_response_info(response):
    logger.debug('响应状态: %s', response.status)
    logger.debug('响应头: %s', response.headers)
    return response

# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """获取数据库连接"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"数据库连接错误: {err}")
        return None

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """获取公文类型列表"""
    conn = get_db_connection()
    if not conn:
        # 如果数据库连接失败，返回本地定义的模板
        try:
            from config import DOCUMENT_TYPES
        except ImportError:
            from backend.config import DOCUMENT_TYPES
        templates = [{'id': dt[0], 'name': dt[1], 'description': dt[2]} for dt in DOCUMENT_TYPES]
        return jsonify({'data': templates})
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM document_types ORDER BY id")
    templates = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify({'data': templates})

@app.route('/api/generate-title', methods=['POST'])
def generate_title():
    """从内容生成标题"""
    data = request.json
    content = data.get('content', '')
    
    if not content:
        return jsonify({'success': False, 'message': '内容不能为空'})
    
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system", 
                        "content": "你是一个专业的公文标题生成助手，请根据提供的公文内容生成一个简洁、准确、符合公文规范的标题，不超过20个字。"
                    },
                    {
                        "role": "user", 
                        "content": f"请根据以下公文内容生成标题：\n\n{content}"
                    }
                ]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            title = result['choices'][0]['message']['content'].strip()
            return jsonify({'success': True, 'title': title})
        else:
            return jsonify({'success': False, 'message': 'API调用失败'})
            
    except Exception as e:
        print(f"生成标题错误: {e}")
        return jsonify({'success': False, 'message': '生成标题失败，请稍后再试'})

@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    """从主题生成内容"""
    data = request.json
    topic = data.get('topic', '')
    document_type = data.get('document_type', '')
    
    if not topic:
        return jsonify({'success': False, 'message': '主题不能为空'})
    
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system", 
                        "content": f"你是一个专业的公文写作助手，请根据提供的主题生成一篇符合{document_type}格式规范的公文内容。内容应该结构清晰、语言规范、符合公文写作要求。"
                    },
                    {
                        "role": "user", 
                        "content": f"请根据以下主题生成{document_type}内容：\n\n{topic}"
                    }
                ]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            return jsonify({'success': True, 'content': content})
        else:
            return jsonify({'success': False, 'message': 'API调用失败'})
            
    except Exception as e:
        print(f"生成内容错误: {e}")
        return jsonify({'success': False, 'message': '生成内容失败，请稍后再试'})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件并解析内容"""
    logger.info("接收到文件上传请求")
    
    if 'file' not in request.files:
        logger.error("没有文件在请求中")
        return jsonify({'success': False, 'message': '没有文件'})
    
    file = request.files['file']
    if file.filename == '':
        logger.error("文件名为空")
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    logger.info(f"上传的文件: {file.filename}")
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            
            # 确保上传目录存在
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
                logger.info(f"创建上传目录: {UPLOAD_FOLDER}")
            
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            logger.info(f"保存文件到: {file_path}")
            
            file.save(file_path)
            logger.info(f"文件保存成功: {file_path}")
            
            content = ""
            try:
                if filename.endswith('.md'):
                    logger.info("解析Markdown文件")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                elif filename.endswith('.docx'):
                    logger.info("解析Word文件")
                    doc = docx.Document(file_path)
                    content = '\n'.join([para.text for para in doc.paragraphs])
                elif filename.endswith('.txt'):
                    logger.info("解析文本文件")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                
                logger.info("文件解析成功")
            except Exception as parse_error:
                logger.error(f"文件解析错误: {parse_error}", exc_info=True)
                return jsonify({'success': False, 'message': f'文件解析失败: {str(parse_error)}'})
            finally:
                # 删除临时文件
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"临时文件已删除: {file_path}")
                except Exception as cleanup_error:
                    logger.error(f"清理临时文件失败: {cleanup_error}")
            
            logger.info("文件处理成功，返回内容")
            return jsonify({'success': True, 'content': content})
            
        except Exception as e:
            logger.error(f"文件处理错误: {e}", exc_info=True)
            return jsonify({'success': False, 'message': f'文件处理失败: {str(e)}'})
    
    logger.error(f"不支持的文件格式: {file.filename}")
    return jsonify({'success': False, 'message': '不支持的文件格式'})

@app.route('/api/generate', methods=['POST'])
def generate_document():
    """生成公文"""
    logger.info("接收到生成公文请求")
    
    try:
        data = request.json
        logger.info(f"请求数据: {data}")
        
        # 保存到数据库
        document_id = None
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO generated_documents 
                        (document_type_id, title, content, metadata) 
                        VALUES (%s, %s, %s, %s)
                    """, (
                        data.get('template_type', ''),
                        data.get('metadata', {}).get('title', ''),
                        data.get('content', ''),
                        json.dumps(data.get('metadata', {}))
                    ))
                    document_id = cursor.lastrowid
                    conn.commit()
                    logger.info(f"数据已保存到数据库，ID: {document_id}")
                except Exception as db_error:
                    logger.error(f"数据库保存错误: {db_error}", exc_info=True)
                finally:
                    cursor.close()
                    conn.close()
        except Exception as conn_error:
            logger.error(f"数据库连接错误: {conn_error}", exc_info=True)
        
        # 生成Word文档
        try:
            logger.info("开始生成Word文档")
            doc = Document()
            
            # 添加标题
            title = data.get('metadata', {}).get('title', '公文标题')
            logger.info(f"添加标题: {title}")
            title_para = doc.add_heading(title, 0)
            title_para.alignment = 1  # 居中对齐
            
            # 添加发文机关
            sender = data.get('metadata', {}).get('sender', '')
            if sender:
                logger.info(f"添加发文机关: {sender}")
                sender_para = doc.add_paragraph(sender)
                sender_para.alignment = 1  # 居中对齐
            
            # 添加正文内容
            content = data.get('content', '')
            if content:
                logger.info("添加正文内容")
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        doc.add_paragraph(para.strip())
            
            # 添加日期
            date = data.get('metadata', {}).get('date', '')
            if date:
                logger.info(f"添加日期: {date}")
                date_para = doc.add_paragraph(date)
                date_para.alignment = 2  # 右对齐
            
            # 保存文档
            temp_dir = tempfile.gettempdir()
            logger.info(f"临时目录: {temp_dir}")
            
            # 确保临时目录存在
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
            temp_file_path = temp_file.name
            temp_file.close()
            
            logger.info(f"保存文档到: {temp_file_path}")
            doc.save(temp_file_path)
            
            download_url = f'/api/download/{os.path.basename(temp_file_path)}'
            logger.info(f"文档生成成功，下载URL: {download_url}")
            
            return jsonify({
                'success': True,
                'document_id': document_id,
                'download_url': download_url
            })
            
        except Exception as doc_error:
            logger.error(f"文档生成错误: {doc_error}", exc_info=True)
            return jsonify({'success': False, 'message': f'文档生成失败: {str(doc_error)}'})
            
    except Exception as e:
        logger.error(f"处理请求错误: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'处理请求失败: {str(e)}'})

@app.route('/api/download/<filename>')
def download_file(filename):
    """下载生成的文档"""
    logger.info(f"请求下载文件: {filename}")
    
    try:
        file_path = os.path.join(tempfile.gettempdir(), filename)
        logger.info(f"文件路径: {file_path}")
        
        if os.path.exists(file_path):
            logger.info(f"文件存在，准备下载")
            return send_file(file_path, as_attachment=True, download_name='公文.docx')
        else:
            logger.error(f"文件不存在: {file_path}")
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        logger.error(f"下载文件错误: {e}", exc_info=True)
        return jsonify({'error': f'下载文件错误: {str(e)}'}), 500

if __name__ == '__main__':
    print("启动公文生成系统后端服务...")
    print("数据库配置:", DB_CONFIG['host'])
    print("DeepSeek API配置:", "已配置" if DEEPSEEK_API_KEY != "sk-your-api-key-here" else "未配置")
    
    app.run(debug=True, host='0.0.0.0', port=5000)