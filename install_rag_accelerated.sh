#!/bin/bash

# 加速器版RAG知识库外挂功能安装脚本
echo "=== 加速器版RAG安装脚本 ==="
echo "使用国内镜像源加速安装..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo "检测到Python版本: $python_version"

if [[ $(echo "$python_version < 3.8" | bc -l) -eq 1 ]]; then
    echo "错误：需要Python 3.8或更高版本"
    exit 1
fi

# 检查当前目录
if [ ! -f "README.md" ]; then
    echo "错误：请在项目根目录运行此脚本"
    exit 1
fi

echo "开始安装RAG知识库外挂功能..."

# 1. 安装MinIO服务器
echo "1. 安装MinIO服务器..."
if ! command -v minio &> /dev/null; then
    echo "下载并安装MinIO服务器..."
    wget https://dl.min.io/server/minio/release/linux-amd64/minio -O /usr/local/bin/minio
    chmod +x /usr/local/bin/minio
    
    # 创建MinIO数据目录
    mkdir -p /opt/minio/data
    mkdir -p /opt/minio/config
    
    # 创建MinIO服务用户
    useradd -r minio-user -s /bin/false 2>/dev/null || true
    chown -R minio-user:minio-user /opt/minio
    
    echo "MinIO服务器安装完成"
else
    echo "MinIO服务器已安装"
fi

# 2. 安装MinIO客户端
echo "2. 安装MinIO客户端..."
if ! command -v mc &> /dev/null; then
    echo "下载并安装MinIO客户端..."
    wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc
    chmod +x /usr/local/bin/mc
    echo "MinIO客户端安装完成"
else
    echo "MinIO客户端已安装"
fi

# 3. 安装Python依赖
echo "3. 安装Python依赖..."
cd backend

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "激活现有虚拟环境..."
    source /venv/bin/activate
else
    echo "创建新的虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 配置pip使用国内镜像源
echo "配置pip使用国内镜像源..."
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 升级pip和基础工具
echo "升级pip和基础工具..."
pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install wheel setuptools -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 先卸载冲突的包
echo "清理冲突的包..."
pip uninstall -y huggingface-hub transformers sentence-transformers 2>/dev/null || true

# 按正确顺序安装依赖（使用国内镜像源）
echo "按正确顺序安装依赖..."

echo "1. 安装基础依赖..."
pip install numpy==1.24.3 -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install pandas==1.5.3 -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install scikit-learn==1.3.2 -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "2. 安装huggingface相关包..."
pip install huggingface-hub==0.16.4 -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install transformers==4.21.3 -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "3. 安装sentence-transformers..."
pip install sentence-transformers==2.2.2 -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "4. 安装向量数据库..."
pip install chromadb==0.4.22 -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "5. 安装文件处理库..."
pip install pypdf2==3.0.1 -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install python-docx==0.8.11 -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install openpyxl==3.1.2 -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "6. 安装MinIO客户端..."
pip install minio==7.2.0 -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "7. 安装其他工具..."
pip install requests==2.31.0 -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install python-dateutil==2.8.2 -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install tiktoken==0.5.1 -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 测试安装结果
echo "测试Python依赖安装..."
python3 -c "
import sys
print('Python版本:', sys.version)

try:
    import minio
    print('✓ minio 导入成功')
except ImportError as e:
    print('✗ minio 导入失败:', e)

try:
    import sentence_transformers
    print('✓ sentence_transformers 导入成功')
except ImportError as e:
    print('✗ sentence_transformers 导入失败:', e)

try:
    import chromadb
    print('✓ chromadb 导入成功')
except ImportError as e:
    print('✗ chromadb 导入失败:', e)

try:
    import pandas
    print('✓ pandas 导入成功')
except ImportError as e:
    print('✗ pandas 导入失败:', e)

try:
    import numpy
    print('✓ numpy 导入成功')
except ImportError as e:
    print('✗ numpy 导入失败:', e)

try:
    import pypdf2
    print('✓ pypdf2 导入成功')
except ImportError as e:
    print('✗ pypdf2 导入失败:', e)

try:
    import docx
    print('✓ python-docx 导入成功')
except ImportError as e:
    print('✗ python-docx 导入失败:', e)

try:
    import openpyxl
    print('✓ openpyxl 导入成功')
except ImportError as e:
    print('✗ openpyxl 导入失败:', e)
"

cd ..

# 4. 创建配置文件
echo "4. 创建RAG配置文件..."
cat > backend/config_rag.py << 'EOF'
"""
RAG知识库配置文件
"""
import os

# MinIO配置
MINIO_CONFIG = {
    'endpoint': 'localhost:9000',
    'access_key': 'minioadmin',
    'secret_key': 'minioadmin',
    'secure': False,
    'bucket_name': 'knowledge-base'
}

# 向量数据库配置
VECTOR_DB_CONFIG = {
    'persist_directory': './vector_db',
    'collection_name': 'knowledge_chunks'
}

# 知识库配置
KNOWLEDGE_BASE_CONFIG = {
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'supported_file_types': ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.csv']
}

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'official_document',
    'charset': 'utf8mb4'
}

# 文件大小限制
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 支持的文件类型
SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.csv']
EOF

# 5. 创建启动脚本
echo "5. 创建RAG服务启动脚本..."
cat > start_rag_services.sh << 'EOF'
#!/bin/bash

echo "启动RAG知识库服务..."

# 启动MinIO服务器
echo "启动MinIO服务器..."
nohup minio server /opt/minio/data --console-address ":9001" > /opt/minio/minio.log 2>&1 &
echo "MinIO服务器已启动，控制台地址: http://localhost:9001"

# 等待MinIO启动
sleep 5

# 配置MinIO客户端
echo "配置MinIO客户端..."
mc alias set myminio http://localhost:9000 minioadmin minioadmin

# 创建知识库存储桶
echo "创建知识库存储桶..."
mc mb myminio/knowledge-base 2>/dev/null || echo "存储桶已存在"

# 启动后端服务
echo "启动后端服务..."
cd backend
source venv/bin/activate
nohup python run.py > ../logs/backend.log 2>&1 &
echo "后端服务已启动"

cd ..

echo "RAG知识库服务启动完成！"
echo "MinIO控制台: http://localhost:9001"
echo "后端API: http://localhost:5000"
echo "前端界面: http://localhost:8081"
EOF

chmod +x start_rag_services.sh

# 6. 创建停止脚本
echo "6. 创建RAG服务停止脚本..."
cat > stop_rag_services.sh << 'EOF'
#!/bin/bash

echo "停止RAG知识库服务..."

# 停止后端服务
echo "停止后端服务..."
pkill -f "python run.py" 2>/dev/null || echo "后端服务未运行"

# 停止MinIO服务器
echo "停止MinIO服务器..."
pkill -f "minio server" 2>/dev/null || echo "MinIO服务器未运行"

echo "RAG知识库服务已停止"
EOF

chmod +x stop_rag_services.sh

# 7. 创建日志目录
mkdir -p logs

echo ""
echo "=== RAG知识库外挂功能安装完成 ==="
echo ""
echo "安装内容："
echo "✓ MinIO服务器和客户端"
echo "✓ Python依赖包（使用国内镜像源）"
echo "✓ RAG配置文件"
echo "✓ 服务启动和停止脚本"
echo ""
echo "使用方法："
echo "1. 启动RAG服务: ./start_rag_services.sh"
echo "2. 停止RAG服务: ./stop_rag_services.sh"
echo "3. 访问MinIO控制台: http://localhost:9001"
echo "4. 访问前端界面: http://localhost:8081"
echo ""
echo "注意：首次启动需要配置MinIO存储桶和数据库连接"
echo "" 