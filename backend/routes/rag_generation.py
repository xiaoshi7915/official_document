"""
RAG增强的公文生成API
集成知识库检索和AI生成
"""
from flask import Blueprint, request, jsonify
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os

# 确保使用正确的SQLite版本
try:
    from utils.sqlite_init import init_sqlite
    init_sqlite()
except ImportError:
    # 如果导入失败，手动设置SQLite
    import sys
    import os
    from pathlib import Path
    
    venv_path = Path(__file__).parent.parent / "venv"
    site_packages = list(venv_path.glob("lib/python*/site-packages"))
    if site_packages:
        pysqlite3_path = site_packages[0] / "pysqlite3"
        if pysqlite3_path.exists():
            sys.path.insert(0, str(pysqlite3_path))
    
    try:
        import pysqlite3
        import sqlite3
        sys.modules['sqlite3'] = pysqlite3
    except ImportError:
        pass

# 导入服务
try:
    from services.vector_service import VectorService
    from models.knowledge_management import KnowledgeManagementModel
    # 使用新的安全配置模块
    try:
        from config.security import security_config
        DEEPSEEK_API_URL = security_config.DEEPSEEK_API_URL
        DEEPSEEK_API_KEY = security_config.DEEPSEEK_API_KEY
    except ImportError:
        # 如果安全配置不可用，使用默认值
        DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
        DEEPSEEK_API_KEY = None
    import requests
except ImportError as e:
    print(f"RAG模块导入失败: {e}")
    VectorService = None
    KnowledgeManagementModel = None
    DEEPSEEK_API_URL = None
    DEEPSEEK_API_KEY = None

# 导入统一的日志管理器
try:
    from utils.logger import get_route_logger
    logger = get_route_logger('rag_generation')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# 创建蓝图
rag_generation_bp = Blueprint('rag_generation', __name__)

# 初始化服务
try:
    if VectorService and KnowledgeManagementModel:
        vector_service = VectorService()
        db_model = KnowledgeManagementModel()
    else:
        vector_service = None
        db_model = None
except Exception as e:
    print(f"RAG服务初始化失败: {e}")
    vector_service = None
    db_model = None

@rag_generation_bp.route('/generate-with-rag', methods=['POST'])
def generate_with_rag():
    """
    RAG增强的公文生成
    
    POST /api/rag/generate-with-rag
    Content-Type: application/json
    
    Body:
    {
        "document_type": "报告",
        "topic": "主题内容",
        "title": "标题",
        "reference_file_ids": ["file_id1", "file_id2"],
        "user_id": "user123"
    }
    
    Returns:
        JSON响应
    """
    try:
        # 检查服务是否可用
        if not vector_service or not db_model:
            return jsonify({
                'success': False,
                'error': 'RAG服务不可用，请检查系统配置'
            }), 503
        
        start_time = time.time()
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '缺少请求数据'
            }), 400
        
        document_type = data.get('document_type', '')
        topic = data.get('topic', '')
        title = data.get('title', '')
        reference_file_ids = data.get('reference_file_ids', [])
        user_id = data.get('user_id', 'anonymous')
        
        if not topic:
            return jsonify({
                'success': False,
                'error': '主题内容不能为空'
            }), 400
        
        # 创建生成记录
        generation_record = {
            'user_id': user_id,
            'document_type': document_type,
            'title': title,
            'topic': topic,
            'reference_files': reference_file_ids,
            'generation_method': 'rag_enhanced',
            'status': 'processing'
        }
        
        record_id = db_model.insert_generation_record(generation_record)
        
        try:
            # 1. 从知识库检索相关内容
            rag_context = ""
            if reference_file_ids:
                logger.info(f"开始从知识库检索相关内容，文件IDs: {reference_file_ids}")
                
                # 构建检索查询
                search_query = f"{topic} {document_type}"
                
                # 搜索向量数据库
                similar_chunks = vector_service.search_similar_chunks(
                    search_query, 
                    top_k=10, 
                    file_ids=reference_file_ids
                )
                
                if similar_chunks:
                    # 构建RAG上下文
                    rag_context = "参考文档内容：\n\n"
                    for i, chunk in enumerate(similar_chunks[:5]):  # 只使用前5个最相关的块
                        rag_context += f"【参考{i+1}】\n{chunk['content']}\n\n"
                    
                    logger.info(f"检索到 {len(similar_chunks)} 个相关文档块")
                else:
                    logger.warning("未检索到相关文档内容")
            
            # 2. 构建AI提示
            system_prompt = f"""你是一个专业的公文写作助手，请根据提供的主题和参考文档内容，生成一篇符合{document_type}格式规范的公文内容。

要求：
1. 只生成纯正文内容，不要包含公文格式元素（如标题、主送机关、发文机关、发文日期等）
2. 内容结构清晰、语言规范、符合公文写作要求
3. 充分利用参考文档中的相关信息
4. 生成的内容要符合{document_type}的特点和要求
5. 直接返回正文内容，不要包含标题和其他格式元素
6. 不要包含```markdown```标记，直接输出内容

参考文档内容：
{rag_context}

请根据以下主题生成{document_type}内容："""

            user_prompt = f"{topic}"
            
            # 3. 调用AI生成内容
            logger.info("开始调用AI生成内容")
            
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
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    "max_tokens": 3000,
                    "temperature": 0.7
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_content = result['choices'][0]['message']['content'].strip()
                
                generation_time = int(time.time() - start_time)
                
                # 4. 更新生成记录
                db_model.update_generation_record(record_id, {
                    'content': generated_content,
                    'rag_context': rag_context,
                    'status': 'completed',
                    'generation_time': generation_time
                })
                
                # 5. 更新知识库使用统计
                for file_id in reference_file_ids:
                    db_model.update_usage_stats(file_id)
                
                logger.info(f"RAG增强生成成功，记录ID: {record_id}, 耗时: {generation_time}秒")
                
                return jsonify({
                    'success': True,
                    'record_id': record_id,
                    'content': generated_content,
                    'rag_context': rag_context,
                    'generation_time': generation_time,
                    'message': 'RAG增强生成成功'
                }), 200
            else:
                error_msg = f"AI生成失败: {response.status_code}"
                logger.error(error_msg)
                
                # 更新失败记录
                db_model.update_generation_record(record_id, {
                    'status': 'failed',
                    'error_message': error_msg
                })
                
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 500
                
        except Exception as e:
            error_msg = f"RAG生成过程失败: {str(e)}"
            logger.error(error_msg)
            
            # 更新失败记录
            if record_id:
                db_model.update_generation_record(record_id, {
                    'status': 'failed',
                    'error_message': error_msg
                })
            
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
            
    except Exception as e:
        logger.error(f"RAG生成API错误: {e}")
        return jsonify({
            'success': False,
            'error': f'RAG生成API错误: {str(e)}'
        }), 500

@rag_generation_bp.route('/generate-outline', methods=['POST'])
def generate_outline():
    """
    RAG增强的大纲生成
    
    POST /api/rag/generate-outline
    Content-Type: application/json
    
    Body:
    {
        "document_type": "报告",
        "topic": "主题内容",
        "title": "标题",
        "reference_file_ids": ["file_id1", "file_id2"],
        "user_id": "user123",
        "generation_type": "outline"
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
        
        document_type = data.get('document_type', '')
        topic = data.get('topic', '')
        title = data.get('title', '')
        reference_file_ids = data.get('reference_file_ids', [])
        user_id = data.get('user_id', 'anonymous')
        generation_type = data.get('generation_type', 'outline')
        
        if not topic:
            return jsonify({
                'success': False,
                'error': '主题内容不能为空'
            }), 400
        
        # 创建生成记录
        generation_record = {
            'user_id': user_id,
            'document_type': document_type,
            'title': title,
            'topic': topic,
            'reference_files': reference_file_ids,
            'generation_method': 'rag_outline',
            'status': 'processing'
        }
        
        record_id = db_model.insert_generation_record(generation_record)
        
        try:
            # 1. 从知识库检索相关内容
            rag_context = ""
            if reference_file_ids:
                logger.info(f"开始从知识库检索相关内容，文件IDs: {reference_file_ids}")
                
                # 构建检索查询
                search_query = f"{topic} {document_type} 大纲"
                
                # 搜索向量数据库
                similar_chunks = vector_service.search_similar_chunks(
                    search_query, 
                    top_k=10, 
                    file_ids=reference_file_ids
                )
                
                if similar_chunks:
                    # 构建RAG上下文
                    context_parts = []
                    for chunk in similar_chunks:
                        context_parts.append(f"相关内容：{chunk['content']}")
                    
                    rag_context = "\n\n".join(context_parts)
                    logger.info(f"检索到 {len(similar_chunks)} 个相关内容片段")
                else:
                    logger.info("未检索到相关内容")
            else:
                logger.info("未提供参考文件，跳过知识库检索")
            
            # 2. 构建AI提示词（专门用于大纲生成）
            if rag_context:
                prompt = f"""你是一个专业的公文写作助手，请根据以下信息生成一个详细的公文大纲：

主题：{topic}
公文类型：{document_type}

参考信息：
{rag_context}

请生成一个结构清晰、层次分明的大纲，包含以下要求：
1. 只生成纯内容大纲，不要包含公文格式元素（如标题、主送机关、发文机关、发文日期等）
2. 大纲最多只有三级标题（一级、二级、三级）
3. 使用标准的Markdown格式（# ## ###）
4. 每个章节都要有明确的主题
5. 大纲要逻辑清晰，层次分明
6. 不要包含```markdown```标记，直接输出内容

请直接输出大纲内容，不要包含其他说明文字。"""
            else:
                prompt = f"""你是一个专业的公文写作助手，请根据以下信息生成一个详细的公文大纲：

主题：{topic}
公文类型：{document_type}

请生成一个结构清晰、层次分明的大纲，包含以下要求：
1. 只生成纯内容大纲，不要包含公文格式元素（如标题、主送机关、发文机关、发文日期等）
2. 大纲最多只有三级标题（一级、二级、三级）
3. 使用标准的Markdown格式（# ## ###）
4. 每个章节都要有明确的主题
5. 大纲要逻辑清晰，层次分明
6. 不要包含```markdown```标记，直接输出内容

请直接输出大纲内容，不要包含其他说明文字。"""
            
            # 3. 调用AI API生成大纲
            logger.info("开始调用AI API生成大纲")
            
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
                generated_content = result['choices'][0]['message']['content'].strip()
                
                # 4. 更新生成记录
                if record_id:
                    db_model.update_generation_record(record_id, {
                        'status': 'completed',
                        'generated_content': generated_content,
                        'completion_time': datetime.now().isoformat()
                    })
                
                end_time = time.time()
                generation_time = end_time - start_time
                
                logger.info(f"大纲生成成功，耗时: {generation_time:.2f}秒")
                
                return jsonify({
                    'success': True,
                    'content': generated_content,
                    'doc_id': f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'generation_time': generation_time,
                    'record_id': record_id
                }), 200
            else:
                error_msg = f"AI API调用失败: {response.status_code} - {response.text}"
                logger.error(error_msg)
                
                # 更新失败记录
                if record_id:
                    db_model.update_generation_record(record_id, {
                        'status': 'failed',
                        'error_message': error_msg
                    })
                
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 500
                
        except Exception as e:
            error_msg = f"大纲生成过程中发生错误: {str(e)}"
            logger.error(error_msg)
            
            # 更新失败记录
            if record_id:
                db_model.update_generation_record(record_id, {
                    'status': 'failed',
                    'error_message': error_msg
                })
            
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
            
    except Exception as e:
        logger.error(f"大纲生成API错误: {e}")
        return jsonify({
            'success': False,
            'error': f'大纲生成API错误: {str(e)}'
        }), 500

@rag_generation_bp.route('/records', methods=['GET'])
def get_generation_records():
    """
    获取公文生成记录
    
    GET /api/rag/records?user_id=user123&limit=50
    
    Returns:
        JSON响应
    """
    try:
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 50))
        
        records = db_model.get_generation_records(user_id, limit)
        
        return jsonify({
            'success': True,
            'records': records,
            'total': len(records)
        }), 200
        
    except Exception as e:
        logger.error(f"获取生成记录失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取生成记录失败: {str(e)}'
        }), 500

@rag_generation_bp.route('/records/<int:record_id>', methods=['GET'])
def get_generation_record_detail(record_id):
    """
    获取公文生成记录详情
    
    GET /api/rag/records/<record_id>
    
    Returns:
        JSON响应
    """
    try:
        records = db_model.get_generation_records()
        record = None
        
        for r in records:
            if r['id'] == record_id:
                record = r
                break
        
        if not record:
            return jsonify({
                'success': False,
                'error': '记录不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'record': record
        }), 200
        
    except Exception as e:
        logger.error(f"获取生成记录详情失败: {e}")
        return jsonify({
            'success': False,
            'error': f'获取生成记录详情失败: {str(e)}'
        }), 500

@rag_generation_bp.route('/search-context', methods=['POST'])
def search_context():
    """
    搜索相关上下文（用于预览）
    
    POST /api/rag/search-context
    Content-Type: application/json
    
    Body:
    {
        "query": "搜索查询",
        "file_ids": ["file_id1", "file_id2"],
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
        file_ids = data.get('file_ids', [])
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({
                'success': False,
                'error': '查询内容不能为空'
            }), 400
        
        # 搜索向量数据库
        similar_chunks = vector_service.search_similar_chunks(query, top_k, file_ids)
        
        # 格式化结果
        context_results = []
        for chunk in similar_chunks:
            context_results.append({
                'content': chunk['content'],
                'file_id': chunk['metadata'].get('file_id', ''),
                'chunk_index': chunk['metadata'].get('chunk_index', 0),
                'similarity': 1 - chunk.get('distance', 0)  # 转换为相似度
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'results': context_results,
            'total': len(context_results)
        }), 200
        
    except Exception as e:
        logger.error(f"搜索上下文失败: {e}")
        return jsonify({
            'success': False,
            'error': f'搜索上下文失败: {str(e)}'
        }), 500 