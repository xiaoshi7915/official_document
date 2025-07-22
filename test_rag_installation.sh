#!/bin/bash

# RAG知识库安装测试脚本
echo "=== RAG知识库安装测试 ==="

# 检查当前目录
if [ ! -f "README.md" ]; then
    echo "错误：请在项目根目录运行此脚本"
    exit 1
fi

echo "开始测试RAG知识库安装..."

# 1. 测试MinIO服务器
echo "1. 测试MinIO服务器..."
if command -v minio &> /dev/null; then
    echo "✓ MinIO服务器已安装"
    minio --version
else
    echo "✗ MinIO服务器未安装"
fi

# 2. 测试MinIO客户端
echo ""
echo "2. 测试MinIO客户端..."
if command -v mc &> /dev/null; then
    echo "✓ MinIO客户端已安装"
    mc --version
else
    echo "✗ MinIO客户端未安装"
fi

# 3. 测试Python依赖
echo ""
echo "3. 测试Python依赖..."
cd backend

if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
    
    echo "测试Python依赖导入..."
    python3 -c "
import sys
print('Python版本:', sys.version)

dependencies = [
    ('minio', 'MinIO客户端'),
    ('sentence_transformers', 'Sentence Transformers'),
    ('chromadb', 'ChromaDB向量数据库'),
    ('pandas', 'Pandas数据处理'),
    ('numpy', 'NumPy数值计算'),
    ('pypdf2', 'PDF处理'),
    ('docx', 'Word文档处理'),
    ('openpyxl', 'Excel处理')
]

success_count = 0
total_count = len(dependencies)

for module, name in dependencies:
    try:
        __import__(module)
        print(f'✓ {name} ({module}) 导入成功')
        success_count += 1
    except ImportError as e:
        print(f'✗ {name} ({module}) 导入失败: {e}')

print(f'\\n测试结果: {success_count}/{total_count} 个依赖安装成功')

if success_count == total_count:
    print('🎉 所有依赖安装成功！')
else:
    print('⚠️  部分依赖安装失败，请检查安装日志')
"
else
    echo "✗ 虚拟环境不存在"
fi

cd ..

# 4. 测试配置文件
echo ""
echo "4. 测试配置文件..."
if [ -f "backend/config_rag.py" ]; then
    echo "✓ RAG配置文件存在"
else
    echo "✗ RAG配置文件不存在"
fi

# 5. 测试启动脚本
echo ""
echo "5. 测试启动脚本..."
if [ -f "start_rag_simple.sh" ]; then
    echo "✓ 简化启动脚本存在"
else
    echo "✗ 简化启动脚本不存在"
fi

if [ -f "start_rag_services.sh" ]; then
    echo "✓ 完整启动脚本存在"
else
    echo "✗ 完整启动脚本不存在"
fi

# 6. 测试MinIO服务状态
echo ""
echo "6. 测试MinIO服务状态..."
if pgrep -f "minio server" > /dev/null; then
    echo "✓ MinIO服务器正在运行"
    echo "MinIO控制台地址: http://localhost:9001"
else
    echo "✗ MinIO服务器未运行"
    echo "启动命令: ./start_rag_simple.sh"
fi

# 7. 测试后端服务状态
echo ""
echo "7. 测试后端服务状态..."
if pgrep -f "python run.py" > /dev/null; then
    echo "✓ 后端服务正在运行"
    echo "后端API地址: http://localhost:5000"
else
    echo "✗ 后端服务未运行"
    echo "启动命令: cd backend && source venv/bin/activate && python run.py"
fi

echo ""
echo "=== 测试完成 ==="
echo ""
echo "如果所有测试都通过，说明RAG知识库功能安装成功！"
echo "现在可以访问前端界面测试功能：http://localhost:8081"
echo "" 