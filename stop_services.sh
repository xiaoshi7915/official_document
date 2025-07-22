#!/bin/bash

# 公文生成系统停止脚本
echo "=== 公文生成系统停止脚本 ==="

# 停止后端服务
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm backend.pid
        echo "后端服务已停止"
    else
        echo "后端服务未运行"
        rm backend.pid
    fi
else
    echo "未找到后端服务PID文件"
fi

# 停止前端服务
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm frontend.pid
        echo "前端服务已停止"
    else
        echo "前端服务未运行"
        rm frontend.pid
    fi
else
    echo "未找到前端服务PID文件"
fi

# 强制停止可能残留的进程
echo "清理残留进程..."
pkill -f "python main.py" 2>/dev/null
pkill -f "vite" 2>/dev/null

echo "=== 服务停止完成 ===" 