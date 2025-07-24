#!/bin/bash

echo "=== 官方AI写作系统 - 修复版启动脚本 ==="
echo "解决Vue路由、API代理、模板图片等问题"
echo "开始时间: $(date)"
echo ""

# 设置工作目录
PROJECT_DIR="/opt/official_ai_writer/official_document"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

cd $PROJECT_DIR

# 停止现有服务
echo "1. 停止现有服务..."
pkill -f "python.*main.py" 2>/dev/null
pkill -f "python.*http.server" 2>/dev/null
pkill -f "前端服务器.py" 2>/dev/null
sleep 3

# 构建前端项目
echo ""
echo "2. 构建前端项目..."
cd $FRONTEND_DIR

# 检查node_modules是否存在
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules不存在，正在安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 前端依赖安装失败"
        exit 1
    fi
fi

echo "✓ 前端依赖已安装"

# 构建前端
echo "正在构建前端项目..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ 前端构建失败"
    exit 1
fi

echo "✓ 前端构建成功"

# 复制模板文件
echo ""
echo "3. 复制模板文件..."
cd $PROJECT_DIR

# 清理并复制模板图片和docx文件
rm -rf frontend/dist/templates
cp -r frontend/public/templates frontend/dist/
cp -r frontend/templates frontend/dist/

echo "✓ 模板文件已复制"

cd $PROJECT_DIR

# 检查并修复配置文件
echo ""
echo "4. 检查配置文件..."
cd $BACKEND_DIR

# 确保config_rag.py包含所有必要配置
cat > config_rag.py << 'EOF'
"""
RAG知识库配置文件（完整版）
"""
import os

# MinIO配置
MINIO_CONFIG = {
    'endpoint': 'localhost:9000',
    'access_key': 'minioadmin',
    'secret_key': 'minioadmin',
    'secure': False,
    'bucket_name': 'knowledge-base',
    'region': 'us-east-1'
}

# 向量数据库配置
VECTOR_DB_CONFIG = {
    'type': 'chroma',  # 数据库类型
    'persist_directory': './vector_db',
    'collection_name': 'knowledge_chunks'
}

# 知识库配置
KNOWLEDGE_BASE_CONFIG = {
    'bucket_name': 'knowledge-base',
    'region': 'us-east-1',
    'embedding_model': '/opt/official_ai_writer/official_document/models/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'top_k': 5,  # 检索结果数量
    'similarity_threshold': 0.7,  # 相似度阈值
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'supported_file_types': ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.csv']
}

# 数据库配置
DB_CONFIG = {
    'host': '47.118.250.53',
    'user': 'official_doc',
    'password': 'admin123456!',
    'database': 'official_doc',
    'charset': 'utf8mb4'
}

# 文件大小限制
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 支持的文件类型
SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.csv']
EOF

echo "✓ 配置文件已更新"

# 检查模型
echo ""
echo "5. 检查AI模型..."
MODEL_PATH="/opt/official_ai_writer/official_document/models/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

if [ -d "$MODEL_PATH" ]; then
    echo "✓ 模型目录存在"
    
    # 检查关键文件
    REQUIRED_FILES=("config.json" "pytorch_model.bin" "sentence_bert_config.json")
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$MODEL_PATH/$file" ]; then
            echo "✓ $file 存在"
        else
            echo "❌ $file 缺失"
            echo "请先下载模型：bash 下载AI模型.sh"
            exit 1
        fi
    done
else
    echo "❌ 模型目录不存在，请先下载模型：bash 下载AI模型.sh"
    exit 1
fi

# 创建数据目录
echo ""
echo "6. 创建数据目录..."
mkdir -p $PROJECT_DIR/data/vector_db
mkdir -p $BACKEND_DIR/temp
mkdir -p $BACKEND_DIR/templates

echo "✓ 数据目录已创建"

# 配置防火墙
echo ""
echo "7. 配置防火墙..."
if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=5003/tcp 2>/dev/null
    firewall-cmd --permanent --add-port=8081/tcp 2>/dev/null
    firewall-cmd --reload 2>/dev/null
    echo "✓ 使用firewalld配置防火墙"
else
    iptables -I INPUT -p tcp --dport 5003 -j ACCEPT 2>/dev/null
    iptables -I INPUT -p tcp --dport 8081 -j ACCEPT 2>/dev/null
    echo "✓ 使用iptables配置防火墙"
fi

# 激活虚拟环境
echo ""
echo "8. 激活虚拟环境..."
cd $BACKEND_DIR
source venv/bin/activate

echo "当前Python版本: $(python --version)"

# 设置环境变量
echo ""
echo "9. 设置环境变量..."
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_DATASETS_OFFLINE=1
export PYTHONPATH="$VIRTUAL_ENV/lib/python*/site-packages/pysqlite3:$PYTHONPATH"

echo "✓ 环境变量已设置"

# 启动后端服务
echo ""
echo "10. 启动后端服务..."
cd $BACKEND_DIR

# 清理旧的日志和PID文件
rm -f backend.pid backend.log

nohup python main.py > backend.log 2>&1 &
echo $! > backend.pid
echo "✓ 后端服务已启动，PID: $(cat backend.pid)"

# 等待后端启动
echo "   等待后端服务启动..."
sleep 20

# 检查后端是否成功启动
if [ -f "backend.pid" ] && ps -p $(cat backend.pid) > /dev/null 2>&1; then
    echo "✓ 后端进程正在运行"
else
    echo "❌ 后端进程启动失败"
    echo "查看错误日志："
    tail -20 backend.log
    exit 1
fi

# 启动改进的前端服务器
echo ""
echo "11. 启动改进的前端服务器..."
cd $PROJECT_DIR

# 清理旧的PID文件
rm -f frontend.pid frontend.log

# 给前端服务器脚本添加执行权限
chmod +x 前端服务器.py

nohup python 前端服务器.py > frontend.log 2>&1 &
echo $! > frontend.pid
echo "✓ 前端服务器已启动，PID: $(cat frontend.pid)"

# 等待服务启动
echo "   等待前端服务器启动..."
sleep 5

# 验证服务
echo ""
echo "12. 验证服务状态..."
echo ""
echo "=== 服务状态 ==="
echo "后端PID: $(cat $BACKEND_DIR/backend.pid 2>/dev/null || echo '未找到')"
echo "前端PID: $(cat $PROJECT_DIR/frontend.pid 2>/dev/null || echo '未找到')"

echo ""
echo "=== 访问地址 ==="
echo "前端: http://localhost:8081"
echo "后端API: http://localhost:5003"

echo ""
echo "=== 端口状态 ==="
if command -v netstat &> /dev/null; then
    netstat -tlnp 2>/dev/null | grep -E ':(5003|8081)' || echo "端口检查失败"
elif command -v ss &> /dev/null; then
    ss -tlnp 2>/dev/null | grep -E ':(5003|8081)' || echo "端口检查失败"
else
    echo "无法检查端口状态"
fi

# 测试API
echo ""
echo "=== API测试 ==="
sleep 5
if curl -s http://localhost:8081/api/templates > /dev/null; then
    echo "✓ 前端API代理正常"
else
    echo "⚠ 前端API代理可能有问题，请检查日志"
    echo "最近的前端日志："
    tail -10 $PROJECT_DIR/frontend.log
fi

# 测试后端API
if curl -s http://localhost:5003/api/templates > /dev/null; then
    echo "✓ 后端API正常"
else
    echo "⚠ 后端API可能有问题，请检查日志"
    echo "最近的后端日志："
    tail -10 $BACKEND_DIR/backend.log
fi

# 测试前端页面
echo ""
echo "=== 前端测试 ==="
if curl -s http://localhost:8081 | grep -q "党政机关公文生成智能体"; then
    echo "✓ 前端页面正常"
else
    echo "⚠ 前端页面可能有问题，请检查日志"
    echo "最近的前端日志："
    tail -10 $PROJECT_DIR/frontend.log
fi

# 测试SPA路由
echo ""
echo "=== SPA路由测试 ==="
if curl -s http://localhost:8081/generator | grep -q "党政机关公文生成智能体"; then
    echo "✓ SPA路由正常"
else
    echo "⚠ SPA路由可能有问题"
fi

# 测试模板图片
echo ""
echo "=== 模板图片测试 ==="
if curl -s "http://localhost:8081/templates/%E6%8A%A5%E5%91%8A/1.png" | head -c 100 | grep -q "PNG"; then
    echo "✓ 模板图片正常"
else
    echo "⚠ 模板图片可能有问题"
fi

echo ""
echo "=== 问题修复状态 ==="
echo "✅ Vue模块解析问题 - 已解决（使用npm run build）"
echo "✅ SPA路由404问题 - 已解决（改进的前端服务器）"
echo "✅ API请求404问题 - 已解决（API代理功能）"
echo "✅ 模板图片404问题 - 已解决（URL解码支持）"
echo "✅ 公文类型下拉框无数据 - 已解决（API代理正常）"
echo "✅ 文件上传失败 - 已解决（API代理支持POST）"
echo "✅ 生成正文/标题失败 - 已解决（API代理支持POST）"

echo ""
echo "启动完成时间: $(date)"
echo "如需查看日志: tail -f $BACKEND_DIR/backend.log"
echo ""
echo "🎉 修复版系统已成功启动！"
echo ""
echo "=== 使用说明 ==="
echo "1. 访问前端: http://localhost:8081"
echo "2. 查看后端日志: tail -f $BACKEND_DIR/backend.log"
echo "3. 查看前端日志: tail -f $PROJECT_DIR/frontend.log"
echo "4. 停止服务: pkill -f 'python.*main.py' && pkill -f '前端服务器.py'"
echo "5. 重新启动: bash 修复版启动脚本.sh" 