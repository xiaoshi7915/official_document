#!/bin/bash

# RAG知识库外挂功能安装脚本
echo "=== RAG知识库外挂功能安装脚本 ==="
echo "正在安装RAG相关依赖和服务..."

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

# 1. 安装Python依赖
echo "1. 安装Python依赖..."
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

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装基础依赖
echo "安装基础依赖..."
pip install wheel setuptools

# 安装RAG依赖
echo "安装RAG功能依赖..."
pip install -r requirements_rag.txt

# 检查安装结果
if [ $? -eq 0 ]; then
    echo "Python依赖安装成功"
else
    echo "错误：Python依赖安装失败，尝试逐个安装..."
    
    # 逐个安装关键依赖
    echo "安装minio..."
    pip install minio==7.2.0
    
    echo "安装sentence-transformers..."
    pip install sentence-transformers==2.2.2
    
    echo "安装chromadb..."
    pip install chromadb==0.4.22
    
    echo "安装pandas..."
    pip install pandas==1.5.3
    
    echo "安装其他依赖..."
    pip install pypdf2==3.0.1 python-docx==0.8.11 openpyxl==3.1.2 numpy==1.24.3
    
    # 再次检查
    if [ $? -eq 0 ]; then
        echo "Python依赖安装成功（逐个安装）"
    else
        echo "错误：Python依赖安装仍然失败"
        exit 1
    fi
fi

cd ..

# 2. 下载并安装MinIO
echo "2. 安装MinIO服务..."

# 检查MinIO是否已安装
if command -v minio &> /dev/null; then
    echo "MinIO已安装，跳过下载"
else
    echo "下载MinIO..."
    wget -O minio https://dl.min.io/server/minio/release/linux-amd64/minio
    chmod +x minio
    sudo mv minio /usr/local/bin/
    
    if [ $? -eq 0 ]; then
        echo "MinIO安装成功"
    else
        echo "错误：MinIO安装失败"
        exit 1
    fi
fi

# 3. 创建MinIO数据目录
echo "3. 创建MinIO数据目录..."
sudo mkdir -p /data/minio
sudo chown $USER:$USER /data/minio

# 4. 创建MinIO服务文件
echo "4. 创建MinIO服务文件..."
sudo tee /etc/systemd/system/minio.service > /dev/null <<EOF
[Unit]
Description=MinIO
Documentation=https://docs.min.io
Wants=network-online.target
After=network-online.target
AssertFileIsExecutable=/usr/local/bin/minio

[Service]
WorkingDirectory=/usr/local/

User=$USER
Group=$USER
ProtectProc=invisible

EnvironmentFile=/etc/default/minio
ExecStart=/usr/local/bin/minio server \$MINIO_VOLUMES --console-address \$MINIO_CONSOLE_ADDRESS

# Let systemd restart this service always
Restart=always

# Specifies the maximum file descriptor number that can be opened by this process
LimitNOFILE=65536

# Specifies the maximum number of threads this process can create
TasksMax=infinity

# Disable timeout logic and wait until process is stopped
TimeoutStopSec=infinity
SendSIGKILL=no

[Install]
WantedBy=multi-user.target
EOF

# 5. 创建MinIO环境配置文件
echo "5. 创建MinIO环境配置..."
sudo tee /etc/default/minio > /dev/null <<EOF
# MinIO root user for the object store.
MINIO_ROOT_USER=minioadmin

# MinIO root secret for the object store.
MINIO_ROOT_PASSWORD=minioadmin

# MinIO volumes to be used by MinIO server.
MINIO_VOLUMES="/data/minio"

# MinIO server address.
MINIO_ADDRESS=":9000"

# MinIO console address.
MINIO_CONSOLE_ADDRESS=":9001"
EOF

# 6. 启动MinIO服务
echo "6. 启动MinIO服务..."
sudo systemctl daemon-reload
sudo systemctl enable minio
sudo systemctl start minio

# 检查MinIO服务状态
sleep 3
if sudo systemctl is-active --quiet minio; then
    echo "MinIO服务启动成功"
    echo "MinIO控制台地址: http://localhost:9001"
    echo "用户名: minioadmin"
    echo "密码: minioadmin"
else
    echo "错误：MinIO服务启动失败"
    sudo systemctl status minio
    exit 1
fi

# 7. 安装MinIO客户端
echo "7. 安装MinIO客户端..."
if command -v mc &> /dev/null; then
    echo "MinIO客户端已安装"
else
    wget -O mc https://dl.min.io/client/mc/release/linux-amd64/mc
    chmod +x mc
    sudo mv mc /usr/local/bin/
    echo "MinIO客户端安装成功"
fi

# 8. 配置MinIO客户端
echo "8. 配置MinIO客户端..."
mc alias set local http://localhost:9000 minioadmin minioadmin

# 9. 创建知识库存储桶
echo "9. 创建知识库存储桶..."
mc mb local/knowledge-base --ignore-existing

# 10. 创建必要的目录
echo "10. 创建必要的目录..."
mkdir -p backend/vector_db
mkdir -p backend/logs

# 11. 设置环境变量
echo "11. 设置环境变量..."
cat >> ~/.bashrc <<EOF

# RAG知识库配置
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minioadmin
export MINIO_SECRET_KEY=minioadmin
export MINIO_SECURE=false
export MINIO_REGION=us-east-1
EOF

# 12. 测试安装
echo "12. 测试安装..."
cd backend

# 激活虚拟环境
source venv/bin/activate

# 测试Python依赖
echo "测试Python依赖..."
python3 -c "
try:
    import minio
    print('✓ minio导入成功')
except ImportError as e:
    print(f'✗ minio导入失败: {e}')
    exit(1)

try:
    import sentence_transformers
    print('✓ sentence_transformers导入成功')
except ImportError as e:
    print(f'✗ sentence_transformers导入失败: {e}')
    exit(1)

try:
    import chromadb
    print('✓ chromadb导入成功')
except ImportError as e:
    print(f'✗ chromadb导入失败: {e}')
    exit(1)

try:
    import PyPDF2
    print('✓ PyPDF2导入成功')
except ImportError as e:
    print(f'✗ PyPDF2导入失败: {e}')
    exit(1)

try:
    from docx import Document
    print('✓ python-docx导入成功')
except ImportError as e:
    print(f'✗ python-docx导入失败: {e}')
    exit(1)

try:
    import pandas as pd
    print('✓ pandas导入成功')
except ImportError as e:
    print(f'✗ pandas导入失败: {e}')
    exit(1)

print('所有Python依赖导入成功')
"

if [ $? -eq 0 ]; then
    echo "Python依赖测试通过"
else
    echo "错误：Python依赖测试失败"
    exit 1
fi

cd ..

# 13. 创建启动脚本
echo "13. 创建启动脚本..."
cat > start_rag_services.sh <<'EOF'
#!/bin/bash

# RAG服务启动脚本
echo "=== 启动RAG服务 ==="

# 启动MinIO服务
echo "启动MinIO服务..."
sudo systemctl start minio

# 等待MinIO启动
sleep 3

# 检查MinIO状态
if sudo systemctl is-active --quiet minio; then
    echo "MinIO服务启动成功"
else
    echo "错误：MinIO服务启动失败"
    exit 1
fi

# 启动后端服务
echo "启动后端服务..."
cd backend
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source /backend/venv/bin/activate
else
    echo "错误：虚拟环境不存在，请先运行安装脚本"
    exit 1
fi
python main.py > ../backend_rag.log 2>&1 &
BACKEND_PID=$!
echo "后端服务已启动，PID: $BACKEND_PID"

# 启动前端服务
echo "启动前端服务..."
cd ../frontend
npm run dev > ../frontend_rag.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务已启动，PID: $FRONTEND_PID"

# 保存PID
echo $BACKEND_PID > ../backend_rag.pid
echo $FRONTEND_PID > ../frontend_rag.pid

echo ""
echo "=== RAG服务启动完成 ==="
echo "MinIO控制台: http://localhost:9001"
echo "前端服务: http://localhost:8081"
echo "后端服务: http://localhost:5002"
echo ""
echo "停止服务请运行: ./stop_rag_services.sh"
echo "========================"
EOF

chmod +x start_rag_services.sh

# 创建停止脚本
cat > stop_rag_services.sh <<'EOF'
#!/bin/bash

# RAG服务停止脚本
echo "=== 停止RAG服务 ==="

# 停止后端服务
if [ -f "backend_rag.pid" ]; then
    BACKEND_PID=$(cat backend_rag.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm backend_rag.pid
        echo "后端服务已停止"
    else
        echo "后端服务未运行"
        rm backend_rag.pid
    fi
fi

# 停止前端服务
if [ -f "frontend_rag.pid" ]; then
    FRONTEND_PID=$(cat frontend_rag.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm frontend_rag.pid
        echo "前端服务已停止"
    else
        echo "前端服务未运行"
        rm frontend_rag.pid
    fi
fi

# 停止MinIO服务
echo "停止MinIO服务..."
sudo systemctl stop minio

echo "=== RAG服务停止完成 ==="
EOF

chmod +x stop_rag_services.sh

# 14. 安装完成
echo ""
echo "=== RAG知识库外挂功能安装完成 ==="
echo ""
echo "安装的服务和组件："
echo "✓ Python依赖包"
echo "✓ MinIO对象存储服务"
echo "✓ MinIO客户端工具"
echo "✓ 向量数据库配置"
echo "✓ 启动和停止脚本"
echo ""
echo "使用说明："
echo "1. 启动RAG服务: ./start_rag_services.sh"
echo "2. 停止RAG服务: ./stop_rag_services.sh"
echo "3. 访问MinIO控制台: http://localhost:9001"
echo "4. 访问前端应用: http://localhost:8081"
echo ""
echo "在公文生成页面，点击'上传文件作为参考'按钮即可使用知识库功能"
echo ""
echo "详细文档请参考: RAG_KNOWLEDGE_BASE.md"
echo "================================" 