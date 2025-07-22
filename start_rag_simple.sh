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
