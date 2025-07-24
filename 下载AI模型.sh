#!/bin/bash

echo "=== 下载AI模型解决网络连接问题 ==="
echo "下载sentence-transformers模型到本地"
echo "开始时间: $(date)"
echo ""

# 设置工作目录
PROJECT_DIR="/opt/official_ai_writer/official_document"
BACKEND_DIR="$PROJECT_DIR/backend"
MODELS_DIR="$PROJECT_DIR/models"

cd $PROJECT_DIR

# 创建模型目录
echo "1. 创建模型目录..."
mkdir -p $MODELS_DIR
cd $MODELS_DIR

# 检查网络连接
echo ""
echo "2. 检查网络连接..."
if ping -c 1 huggingface.co > /dev/null 2>&1; then
    echo "✓ 可以连接到huggingface.co"
else
    echo "❌ 无法连接到huggingface.co"
    echo "尝试使用国内镜像..."
fi

# 设置国内镜像
echo ""
echo "3. 配置国内镜像..."
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_URL=https://hf-mirror.com

# 下载模型
echo ""
echo "4. 下载sentence-transformers模型..."
MODEL_NAME="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

echo "正在下载模型: $MODEL_NAME"
echo "这可能需要几分钟时间，请耐心等待..."

# 使用huggingface-cli下载
cd $BACKEND_DIR
source venv/bin/activate

# 设置下载参数
export HF_HUB_DISABLE_TELEMETRY=1
export HF_HUB_OFFLINE=0

# 下载模型
echo "开始下载..."
huggingface-cli download $MODEL_NAME --local-dir $MODELS_DIR/$MODEL_NAME --local-dir-use-symlinks False

if [ $? -eq 0 ]; then
    echo "✓ 模型下载成功"
else
    echo "❌ 模型下载失败，尝试其他方法..."
    
    # 尝试使用git clone
    echo "尝试使用git clone..."
    cd $MODELS_DIR
    git clone https://huggingface.co/$MODEL_NAME
    
    if [ $? -eq 0 ]; then
        echo "✓ 使用git clone下载成功"
    else
        echo "❌ git clone也失败，尝试手动下载..."
        
        # 创建模型目录结构
        mkdir -p $MODEL_NAME
        cd $MODEL_NAME
        
        # 下载必要的文件
        echo "手动下载模型文件..."
        wget -O config.json https://huggingface.co/$MODEL_NAME/raw/main/config.json
        wget -O pytorch_model.bin https://huggingface.co/$MODEL_NAME/resolve/main/pytorch_model.bin
        wget -O sentence_bert_config.json https://huggingface.co/$MODEL_NAME/raw/main/sentence_bert_config.json
        wget -O special_tokens_map.json https://huggingface.co/$MODEL_NAME/raw/main/special_tokens_map.json
        wget -O tokenizer_config.json https://huggingface.co/$MODEL_NAME/raw/main/tokenizer_config.json
        wget -O tokenizer.json https://huggingface.co/$MODEL_NAME/raw/main/tokenizer.json
        wget -O vocab.txt https://huggingface.co/$MODEL_NAME/raw/main/vocab.txt
        
        echo "✓ 手动下载完成"
    fi
fi

# 验证模型文件
echo ""
echo "5. 验证模型文件..."
cd $MODELS_DIR
if [ -d "$MODEL_NAME" ]; then
    echo "✓ 模型目录存在"
    ls -la $MODEL_NAME/
    
    # 检查关键文件
    if [ -f "$MODEL_NAME/config.json" ]; then
        echo "✓ config.json存在"
    else
        echo "❌ config.json缺失"
    fi
    
    if [ -f "$MODEL_NAME/pytorch_model.bin" ]; then
        echo "✓ pytorch_model.bin存在"
    else
        echo "❌ pytorch_model.bin缺失"
    fi
else
    echo "❌ 模型目录不存在"
    exit 1
fi

# 修改配置文件使用本地模型
echo ""
echo "6. 修改配置文件使用本地模型..."
cd $BACKEND_DIR

# 查找配置文件
CONFIG_FILES=("config.py" "settings.py" "config.py" "knowledge_base_config.py")

for config_file in "${CONFIG_FILES[@]}"; do
    if [ -f "$config_file" ]; then
        echo "找到配置文件: $config_file"
        
        # 备份原文件
        cp $config_file ${config_file}.backup
        
        # 修改embedding_model路径
        sed -i "s|sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2|$MODELS_DIR/$MODEL_NAME|g" $config_file
        
        echo "✓ 已修改 $config_file"
        break
    fi
done

# 创建模型路径配置文件
echo ""
echo "7. 创建模型路径配置..."
cat > $BACKEND_DIR/model_paths.py << EOF
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
EOF

echo "✓ 模型路径配置文件已创建"

# 测试模型加载
echo ""
echo "8. 测试模型加载..."
cd $BACKEND_DIR
source venv/bin/activate

python -c "
import os
import sys
sys.path.append('$BACKEND_DIR')

try:
    from model_paths import SENTENCE_TRANSFORMER_MODEL, check_model_exists
    
    if check_model_exists():
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
        print('✓ 模型加载成功')
        
        # 测试编码
        test_text = '这是一个测试句子'
        embedding = model.encode(test_text)
        print(f'✓ 编码测试成功，向量维度: {embedding.shape}')
    else:
        print('❌ 模型文件不完整')
except Exception as e:
    print(f'❌ 模型加载失败: {e}')
"

echo ""
echo "=== 模型下载和配置完成 ==="
echo "模型路径: $MODELS_DIR/$MODEL_NAME"
echo ""
echo "现在可以启动服务："
echo "cd $BACKEND_DIR"
echo "source venv/bin/activate"
echo "python main.py"
echo ""
echo "或者使用启动脚本："
echo "bash start_with_offline_models.sh" 