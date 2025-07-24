# -*- coding: utf-8 -*-
"""
模型路径配置
"""

import os

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 模型目录
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')

# 句子嵌入模型路径
SENTENCE_TRANSFORMER_MODEL = os.path.join(MODELS_DIR, 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# 检查模型是否存在
def check_model_exists():
    """检查模型文件是否存在"""
    required_files = ['config.json', 'pytorch_model.bin', 'sentence_bert_config.json']
    
    for file in required_files:
        file_path = os.path.join(SENTENCE_TRANSFORMER_MODEL, file)
        if not os.path.exists(file_path):
            print(f"❌ 模型文件缺失: {file_path}")
            return False
    
    print("✓ 所有模型文件存在")
    return True

if __name__ == "__main__":
    check_model_exists()
