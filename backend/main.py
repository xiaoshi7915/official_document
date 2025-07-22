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
from docx.oxml.shared import OxmlElement, qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

import logging
from logging.handlers import RotatingFileHandler

# 配置日志 - 只记录关键信息
if not os.path.exists('logs'):
    os.makedirs('logs')
    
# 创建日志文件处理器
file_handler = RotatingFileHandler('logs/backend.log', maxBytes=10485760, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# 获取Flask日志记录器
logger = logging.getLogger('backend')
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)  # 改为INFO级别，减少详细日志

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

try:
    from config import DB_CONFIG, DEEPSEEK_API_URL, DEEPSEEK_API_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
except ImportError:
    # 如果导入失败，尝试使用相对导入
    from backend.config import DB_CONFIG, DEEPSEEK_API_URL, DEEPSEEK_API_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS

app = Flask(__name__)
CORS(app)

# 简化请求日志中间件
@app.before_request
def log_request_info():
    logger.info(f'请求: {request.method} {request.path}')

# 简化响应日志中间件
@app.after_request
def log_response_info(response):
    logger.info(f'响应: {response.status_code}')
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
        logger.error(f"数据库连接错误: {err}")
        return None

def replace_text_in_paragraphs(paragraphs, replacements):
    """支持跨run的文本替换，并处理段落格式"""
    for paragraph in paragraphs:
        # 合并所有run的文本
        full_text = ''.join(run.text for run in paragraph.runs)
        replaced = False
        for old, new in replacements.items():
            if old in full_text:
                full_text = full_text.replace(old, new)
                replaced = True
        if replaced and paragraph.runs:
            # 清空原有runs
            for run in paragraph.runs:
                run.text = ''
            # 只用第一个run写入新内容
            paragraph.runs[0].text = full_text

def apply_document_formatting(doc, content):
    """应用公文格式要求"""
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.shared import OxmlElement, qn
    
    # 设置段落格式
    for paragraph in doc.paragraphs:
        # 设置行距为30磅
        paragraph.paragraph_format.line_spacing = Pt(30)
        
        # 根据内容设置字体格式
        for run in paragraph.runs:
            text = run.text.strip()
            
            # 一级标题：一、二、三、... - 三号黑体字
            if text and text[0] in '一二三四五六七八九十' and text.endswith('、'):
                run.font.name = '黑体'
                run.font.size = Pt(16)  # 三号字约16磅
                run.font.bold = True
            
            # 二级标题：（一）（二）（三）... - 三号楷体_GB2312字
            elif text and text.startswith('（') and text.endswith('）') and len(text) == 4:
                run.font.name = '楷体_GB2312'
                run.font.size = Pt(16)
            
            # 三级标题：1. 2. 3. ... - 三号仿宋_GB2312字，加粗
            elif text and text[0].isdigit() and text.endswith('.'):
                run.font.name = '仿宋_GB2312'
                run.font.size = Pt(16)
                run.font.bold = True
            
            # 正文：三号仿宋_GB2312字
            else:
                run.font.name = '仿宋_GB2312'
                run.font.size = Pt(16)


def replace_text_in_document(doc, replacements):
    # 段落
    replace_text_in_paragraphs(doc.paragraphs, replacements)
    # 表格
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                replace_text_in_paragraphs(cell.paragraphs, replacements)

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """获取公文类型列表"""
    logger.info("获取模板列表")
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
                        "content": "你是一个专业的公文写作助手，请根据提供的公文内容生成一个简洁、准确的标题。标题应该符合公文格式规范。"
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
            logger.info(f"生成标题成功: {title}")
            return jsonify({'success': True, 'title': title})
        else:
            logger.error(f"API调用失败: {response.status_code}")
            return jsonify({'success': False, 'message': 'API调用失败'})
            
    except Exception as e:
        logger.error(f"生成标题错误: {e}")
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
                        "content": f"你是一个专业的公文写作助手，请根据提供的主题生成一篇符合{document_type}格式规范的公文内容。内容应该结构清晰、语言规范、符合公文写作要求。请直接返回正文内容，不要包含标题。"
                    },
                    {
                        "role": "user", 
                        "content": f"请根据以下主题生成{document_type}内容：\n\n{topic}"
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            logger.info(f"生成内容成功，长度: {len(content)}")
            return jsonify({'success': True, 'content': content})
        else:
            logger.error(f"API调用失败: {response.status_code}")
            return jsonify({'success': False, 'message': 'API调用失败'})
            
    except Exception as e:
        logger.error(f"生成内容错误: {e}")
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
            
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
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
                
                logger.info(f"文件解析成功，内容长度: {len(content)}")
            except Exception as parse_error:
                logger.error(f"文件解析错误: {parse_error}")
                return jsonify({'success': False, 'message': f'文件解析失败: {str(parse_error)}'})
            finally:
                # 删除临时文件
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logger.error(f"删除临时文件失败: {e}")
            
            return jsonify({'success': True, 'content': content})
            
        except Exception as e:
            logger.error(f"文件上传错误: {e}")
            return jsonify({'success': False, 'message': f'文件上传失败: {str(e)}'})
    else:
        return jsonify({'success': False, 'message': '不支持的文件类型'})

@app.route('/api/generate', methods=['POST'])
def generate_document():
    """生成公文"""
    logger.info("接收到生成公文请求")
    
    try:
        data = request.json
        template_type = data.get('template_type', '')
        metadata = data.get('metadata', {})
        content = data.get('content', '')
        
        logger.info(f"模板类型: {template_type}, 标题: {metadata.get('title', '')}")
        
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
                        template_type,
                        metadata.get('title', ''),
                        content,
                        json.dumps(metadata)
                    ))
                    document_id = cursor.lastrowid
                    conn.commit()
                    logger.info(f"数据已保存到数据库，ID: {document_id}")
                except Exception as db_error:
                    logger.error(f"数据库保存错误: {db_error}")
                finally:
                    cursor.close()
                    conn.close()
        except Exception as conn_error:
            logger.error(f"数据库连接错误: {conn_error}")
        
        # 使用docx模板生成Word文档
        try:
            logger.info("开始使用模板生成Word文档")
            
            # 获取模板文件路径
            template_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates')
            template_file = os.path.join(template_dir, f'{template_type}.docx')
            
            if not os.path.exists(template_file):
                logger.error(f"模板文件不存在: {template_file}")
                return jsonify({'success': False, 'message': '模板文件不存在'})
            
            # 加载模板文档
            doc = Document(template_file)
            
            # 准备替换内容 - 支持现有模板格式和新的{{}}格式
            replacements = {
                # 版头字段 - 支持现有格式
                '××★1年': metadata.get('year', '2025年'),
                '特急': metadata.get('urgencyLevel', ''),
                '机关代字(20××)×号': f"{metadata.get('senderCode', '')}({metadata.get('year', '2025')}){metadata.get('serialNumber', '')}号",
                '签发人:姓名一姓名二': f"签发人:{metadata.get('senderSignature', '')}",
                
                # 主体字段 - 支持现有格式
                '××××关于××××XXXXXXXX×××的报告': metadata.get('title', ''),
                '××××关于××××XXXXXXXX×××的纪要': metadata.get('title', ''),
                '主送机关:': f"主送机关:{metadata.get('recipient', '')}",
                '正文内容': content,
                
                # 署名字段 - 支持现有格式
                '机关短署名': metadata.get('senderSignature', ''),
                '20××年×月×日': metadata.get('date', ''),
                '(附注内容)': f"({metadata.get('notes', '')})",
                
                # 版记字段 - 支持现有格式
                '抄送:抄送机关1,抄送机关2,抄送机关3,抄送机关4,抄送机关5。': f"抄送:{metadata.get('copyTo', '')}",
                
                # 印发字段 - 支持现有格式
                '印发机关': metadata.get('printingOrg', ''),
                '20××年×月×日印发': f"{metadata.get('printingDate', '')}印发",
                
                # 同时支持新的{{}}格式
                '{{copyNumber}}': metadata.get('copyNumber', '000001'),
                '{{securityLevel}}': metadata.get('securityLevel', '一般'),
                '{{securityPeriod}}': metadata.get('securityPeriod', '1年'),
                '{{urgencyLevel}}': metadata.get('urgencyLevel', '特急'),
                '{{sender}}': metadata.get('sender', '省委宣传部'),
                '{{senderSymbol}}': metadata.get('senderSymbol', '文件'),
                '{{senderCode}}': metadata.get('senderCode', '机关代字'),
                '{{year}}': metadata.get('year', '2025'),
                '{{serialNumber}}': metadata.get('serialNumber', '1'),
                '{{senderSignature}}': metadata.get('senderSignature', '姓名1'),
                '{{title}}': metadata.get('title', ''),
                '{{recipient}}': metadata.get('recipient', ''),
                '{{content}}': content,
                '{{date}}': metadata.get('date', ''),
                '{{notes}}': metadata.get('notes', ''),
                '{{copyTo}}': metadata.get('copyTo', '杭州市委宣传部'),
                '{{printingOrg}}': metadata.get('printingOrg', '印发机关'),
                '{{printingDate}}': metadata.get('printingDate', '')
            }
            
            # 执行文本替换
            replace_text_in_document(doc, replacements)
            
            # 应用公文格式要求
            apply_document_formatting(doc, content)
            
            # 保存文档
            temp_dir = tempfile.gettempdir()
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
            temp_file_path = temp_file.name
            temp_file.close()
            
            doc.save(temp_file_path)
            
            download_url = f'/api/download/{os.path.basename(temp_file_path)}'
            logger.info(f"文档生成成功: {download_url}")
            
            return jsonify({
                'success': True,
                'document_id': document_id,
                'download_url': download_url
            })
            
        except Exception as doc_error:
            logger.error(f"文档生成错误: {doc_error}")
            return jsonify({'success': False, 'message': f'文档生成失败: {str(doc_error)}'})
            
    except Exception as e:
        logger.error(f"处理请求错误: {e}")
        return jsonify({'success': False, 'message': f'处理请求失败: {str(e)}'})

@app.route('/api/preview/<filename>')
def preview_file(filename):
    """预览生成的文档"""
    logger.info(f"请求预览文件: {filename}")
    
    try:
        file_path = os.path.join(tempfile.gettempdir(), filename)
        
        if os.path.exists(file_path):
            logger.info(f"文件存在，准备预览: {file_path}")
            return send_file(file_path, as_attachment=False, download_name='公文.docx')
        else:
            logger.error(f"文件不存在: {file_path}")
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        logger.error(f"预览文件错误: {e}")
        return jsonify({'error': f'预览文件错误: {str(e)}'}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """下载生成的文档"""
    logger.info(f"请求下载文件: {filename}")
    
    try:
        file_path = os.path.join(tempfile.gettempdir(), filename)
        
        if os.path.exists(file_path):
            logger.info(f"文件存在，准备下载: {file_path}")
            return send_file(file_path, as_attachment=True, download_name='公文.docx')
        else:
            logger.error(f"文件不存在: {file_path}")
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        logger.error(f"下载文件错误: {e}")
        return jsonify({'error': f'下载文件错误: {str(e)}'}), 500

if __name__ == '__main__':
    print("启动公文生成系统后端服务...")
    print("数据库配置:", DB_CONFIG['host'])
    print("DeepSeek API配置:", "已配置" if DEEPSEEK_API_KEY != "sk-your-api-key-here" else "未配置")
    
    app.run(debug=True, host='0.0.0.0', port=5002)