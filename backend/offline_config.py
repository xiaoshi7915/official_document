# -*- coding: utf-8 -*-
"""
离线模型配置
"""

import os

# 设置离线模式
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_DATASETS_OFFLINE'] = '1'

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 模型目录
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')

# 句子嵌入模型路径
SENTENCE_TRANSFORMER_MODEL = os.path.join(MODELS_DIR, 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# 知识库配置
KNOWLEDGE_BASE_CONFIG = {
    'embedding_model': SENTENCE_TRANSFORMER_MODEL,
    'vector_db_path': os.path.join(PROJECT_ROOT, 'data', 'vector_db'),
    'chunk_size': 1000,
    'chunk_overlap': 200
}

print(f"✓ 使用离线模型: {SENTENCE_TRANSFORMER_MODEL}")
