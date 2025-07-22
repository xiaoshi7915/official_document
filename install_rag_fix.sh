#!/bin/bash

# 修复版RAG知识库外挂功能安装脚本
echo "=== 修复版RAG安装脚本 ==="
echo "专门处理版本冲突问题..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
echo "检测到Python版本: $python_version"

if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "错误：需要Python 3.8或更高版本"
    exit 1
fi

# 检查是否在项目根目录
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "错误：请在项目根目录下运行此脚本"
    exit 1
fi

# 进入后端目录
cd backend

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "激活现有虚拟环境..."
    source venv/bin/activate
else
    echo "创建新的虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 升级pip和基础工具
echo "升级pip和基础工具..."
pip install --upgrade pip
pip install wheel setuptools

# 先卸载冲突的包
echo "卸载冲突的包..."
pip uninstall -y huggingface-hub transformers sentence-transformers

# 按正确顺序安装依赖
echo "按正确顺序安装依赖..."

echo "1. 安装基础依赖..."
pip install numpy==1.24.3
pip install pandas==1.5.3
pip install scikit-learn==1.3.2

echo "2. 安装huggingface相关包..."
pip install huggingface-hub==0.16.4
pip install transformers==4.21.3

echo "3. 安装sentence-transformers..."
pip install sentence-transformers==2.2.2

echo "4. 安装其他机器学习库..."
pip install chromadb==0.4.22
pip install faiss-cpu==1.7.4

echo "5. 安装文档解析库..."
pip install pypdf2==3.0.1
pip install python-docx==0.8.11
pip install openpyxl==3.1.2

echo "6. 安装其他工具..."
pip install minio==7.2.0
pip install tiktoken==0.5.2
pip install python-multipart==0.0.6
pip install aiofiles==23.2.1
pip install requests==2.31.0
pip install python-dateutil==2.8.2

# 测试安装
echo "测试安装..."
python3 -c "
import sys
print(f'Python版本: {sys.version}')

modules = [
    'minio',
    'sentence_transformers', 
    'chromadb',
    'PyPDF2',
    'docx',
    'pandas',
    'numpy',
    'sklearn'
]

for module in modules:
    try:
        __import__(module)
        print(f'✓ {module} 导入成功')
    except ImportError as e:
        print(f'✗ {module} 导入失败: {e}')
        sys.exit(1)

print('所有依赖安装成功！')
"

if [ $? -eq 0 ]; then
    echo "=== RAG依赖安装成功 ==="
    echo ""
    echo "下一步："
    echo "1. 运行完整的安装脚本: ./install_rag.sh"
    echo "2. 或者手动启动MinIO服务"
    echo "3. 启动应用: ./start_services.sh"
else
    echo "=== RAG依赖安装失败 ==="
    echo "请检查错误信息并手动安装缺失的依赖"
    exit 1
fi

cd .. 