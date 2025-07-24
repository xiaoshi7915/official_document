from flask import Blueprint, request, jsonify
import requests
import time
from datetime import datetime
import os

# 导入统一的日志管理器
try:
    from utils.logger import get_route_logger
    logger = get_route_logger('ai_operations')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# 创建蓝图
ai_operations_bp = Blueprint('ai_operations', __name__)

# 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

@ai_operations_bp.route('/text-operation', methods=['POST'])
def text_operation():
    """
    AI文本操作API
    
    POST /api/ai/text-operation
    Content-Type: application/json
    
    Body:
    {
        "action": "continue|expand|summarize|rewrite|polish",
        "selectedText": "选中的文本内容",
        "fullContent": "完整文档内容",
        "extraRequirements": "额外要求（可选）"
    }
    
    Returns:
        JSON响应
    """
    try:
        start_time = time.time()
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '缺少请求数据'
            }), 400
        
        action = data.get('action', '')
        selected_text = data.get('selectedText', '')
        full_content = data.get('fullContent', '')
        extra_requirements = data.get('extraRequirements', '')
        
        if not selected_text:
            return jsonify({
                'success': False,
                'error': '选中的文本内容不能为空'
            }), 400
        
        if not action:
            return jsonify({
                'success': False,
                'error': '操作类型不能为空'
            }), 400
        
        # 验证操作类型
        valid_actions = ['continue', 'expand', 'summarize', 'rewrite', 'polish']
        if action not in valid_actions:
            return jsonify({
                'success': False,
                'error': f'不支持的操作类型: {action}'
            }), 400
        
        # 构建操作提示词
        prompt = build_operation_prompt(action, selected_text, full_content, extra_requirements)
        
        # 调用AI API
        logger.info(f"开始执行AI操作: {action}")
        
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.7,
            'max_tokens': 2000
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result['choices'][0]['message']['content'].strip()
            
            end_time = time.time()
            operation_time = end_time - start_time
            
            logger.info(f"AI操作成功，耗时: {operation_time:.2f}秒")
            
            return jsonify({
                'success': True,
                'result': generated_text,
                'operation_time': operation_time,
                'action': action
            }), 200
        else:
            error_msg = f"AI API调用失败: {response.status_code} - {response.text}"
            logger.error(error_msg)
            
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
            
    except Exception as e:
        error_msg = f"AI操作失败: {str(e)}"
        logger.error(error_msg)
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

def build_operation_prompt(action, selected_text, full_content, extra_requirements):
    """
    构建AI操作的提示词
    """
    base_prompt = f"""你是一个专业的公文写作助手。请根据以下信息对选中的文本进行{get_action_name(action)}操作：

选中文本：
{selected_text}

完整文档内容（作为背景知识）：
{full_content}

额外要求：
{extra_requirements if extra_requirements else '无'}

操作要求：
{get_action_requirements(action)}

请直接输出处理后的文本内容，不要包含其他说明文字。"""

    return base_prompt

def get_action_name(action):
    """
    获取操作的中文名称
    """
    action_names = {
        'continue': '续写',
        'expand': '扩写',
        'summarize': '缩写',
        'rewrite': '重写',
        'polish': '润色'
    }
    return action_names.get(action, action)

def get_action_requirements(action):
    """
    获取操作的具体要求
    """
    requirements = {
        'continue': """续写要求：
1. 保持原文的风格和语气
2. 内容要连贯，逻辑清晰
3. 符合公文写作规范
4. 续写内容要与原文形成完整的段落或章节""",
        
        'expand': """扩写要求：
1. 在保持原文核心意思的基础上进行扩展
2. 增加细节描述、具体例子或深入分析
3. 保持公文写作的严谨性
4. 扩写后的内容要更加丰富和完整""",
        
        'summarize': """缩写要求：
1. 保留原文的核心信息和关键要点
2. 简化表达，去除冗余内容
3. 保持逻辑结构清晰
4. 缩写后的内容要简洁明了""",
        
        'rewrite': """重写要求：
1. 保持原文的核心意思和主要观点
2. 使用不同的表达方式和句式结构
3. 改善语言表达，使其更加清晰准确
4. 保持公文写作的规范性""",
        
        'polish': """润色要求：
1. 优化语言表达，使其更加准确、生动
2. 改善句式结构，增强可读性
3. 修正语法错误和用词不当
4. 保持公文写作的正式性和专业性"""
    }
    return requirements.get(action, '') 