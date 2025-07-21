from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
import os
import json
from werkzeug.utils import secure_filename
import requests
from datetime import datetime
import tempfile
import docx
from docx import Document
from docx.shared import Inches

app = Flask(__name__)
CORS(app)

# 数据库配置
DB_CONFIG = {
    'host': '47.118.250.53',
    'port': 3306,
    'database': 'official_doc',
    'user': 'official_doc',
    'password': 'admin123456!'
}

# DeepSeek API配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-your-api-key-here")

def get_db_connection():
    """获取数据库连接"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"数据库连接错误: {err}")
        return None

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)