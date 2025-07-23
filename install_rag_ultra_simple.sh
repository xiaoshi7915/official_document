#!/bin/bash

# 超简化版RAG知识库外挂功能安装脚本
echo "=== 超简化版RAG安装脚本 ==="
echo "只安装核心依赖，使用国内镜像源..."

# 检查当前目录
if [ ! -f "README.md" ]; then
    echo "错误：请在项目根目录运行此脚本"
    exit 1
fi

echo "开始安装RAG知识库外挂功能..."

# 1. 安装MinIO服务器（简化版）
echo "1. 安装MinIO服务器..."
if ! command -v minio &> /dev/null; then
    echo "下载并安装MinIO服务器..."
    wget https://dl.min.io/server/minio/release/linux-amd64/minio -O /usr/local/bin/minio
    chmod +x /usr/local/bin/minio
    
    # 创建MinIO数据目录
    mkdir -p /opt/minio/data
    echo "MinIO服务器安装完成"
else
    echo "MinIO服务器已安装"
fi

# 2. 安装MinIO客户端（简化版）
echo "2. 安装MinIO客户端..."
if ! command -v mc &> /dev/null; then
    echo "下载并安装MinIO客户端..."
    wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc
    chmod +x /usr/local/bin/mc
    echo "MinIO客户端安装完成"
else
    echo "MinIO客户端已安装"
fi

# 3. 安装Python依赖（超简化版）
echo "3. 安装Python依赖（超简化版）..."
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

# 升级pip
echo "升级pip..."
pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 只安装最核心的依赖
echo "安装核心依赖..."

echo "1. 安装MinIO客户端..."
pip install minio -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "2. 安装向量化库..."
pip install sentence-transformers -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "3. 安装向量数据库..."
pip install chromadb -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "4. 安装文件处理库..."
pip install pypdf2 python-docx openpyxl -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "5. 安装其他工具..."
pip install requests pandas numpy -i https://pypi.tuna.tsinghua.edu.cn/simple/

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
"

cd ..

# 4. 创建简化配置文件
echo "4. 创建RAG配置文件..."
cat > backend/config_rag.py << 'EOF'
"""
RAG知识库配置文件（简化版）
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

# 5. 创建简化启动脚本
echo "5. 创建RAG服务启动脚本..."
cat > start_rag_simple.sh << 'EOF'
#!/bin/bash

echo "启动RAG知识库服务（简化版）..."

# 启动MinIO服务器
echo "启动MinIO服务器..."
nohup minio server /opt/minio/data --console-address ":9001" > /opt/minio/minio.log 2>&1 &
echo "MinIO服务器已启动，控制台地址: http://localhost:9001"

# 等待MinIO启动
sleep 3

# 配置MinIO客户端
echo "配置MinIO客户端..."
mc alias set myminio http://localhost:9000 minioadmin minioadmin

# 创建知识库存储桶
echo "创建知识库存储桶..."
mc mb myminio/knowledge-base 2>/dev/null || echo "存储桶已存在"

echo "RAG知识库服务启动完成！"
echo "MinIO控制台: http://localhost:9001"
echo "现在可以启动后端服务: cd backend && source venv/bin/activate && python run.py"
EOF

chmod +x start_rag_simple.sh

# 6. 创建日志目录
mkdir -p logs

echo ""
echo "=== 超简化版RAG知识库外挂功能安装完成 ==="
echo ""
echo "安装内容："
echo "✓ MinIO服务器和客户端"
echo "✓ Python核心依赖包（使用国内镜像源）"
echo "✓ RAG配置文件"
echo "✓ 简化启动脚本"
echo ""
echo "使用方法："
echo "1. 启动MinIO服务: ./start_rag_simple.sh"
echo "2. 启动后端服务: cd backend && source venv/bin/activate && python run.py"
echo "3. 访问MinIO控制台: http://localhost:9001"
echo "4. 访问前端界面: http://localhost:8081"
echo ""
echo "注意：这是简化版本，如果遇到问题请使用完整版安装脚本"
echo "" 