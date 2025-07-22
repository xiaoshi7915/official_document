#!/bin/bash

# 公文生成系统启动脚本
echo "=== 公文生成系统启动脚本 ==="
echo "正在启动服务..."

# 检查是否在正确的目录
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "错误：请在项目根目录下运行此脚本"
    exit 1
fi

# 启动后端服务
echo "1. 启动后端服务 (端口: 5002)..."
cd backend
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
else
    echo "警告：未找到虚拟环境，请确保已安装所需依赖"
fi

# 在后台启动后端服务
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务已启动，PID: $BACKEND_PID"

# 等待后端服务启动
echo "等待后端服务启动..."
sleep 3

# 启动前端服务
echo "2. 启动前端服务 (端口: 8081)..."
cd ../frontend

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 在后台启动前端服务
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务已启动，PID: $FRONTEND_PID"

# 保存PID到文件
echo $BACKEND_PID > ../backend.pid
echo $FRONTEND_PID > ../frontend.pid

echo ""
echo "=== 服务启动完成 ==="
echo "前端服务: http://localhost:8081"
echo "前端服务: http://121.36.205.70:8081"
echo "后端服务: http://localhost:5002"
echo ""
echo "日志文件:"
echo "- 后端日志: backend.log"
echo "- 前端日志: frontend.log"
echo ""
echo "停止服务请运行: ./stop_services.sh"
echo "========================" 