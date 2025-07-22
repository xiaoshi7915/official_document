# RAG知识库功能快速开始

## 🚀 一键安装（推荐）

```bash
# 进入项目目录
cd /opt/office_ai_writer/official_document

# 运行超简化安装脚本（使用国内镜像源，速度最快）
./install_rag_ultra_simple.sh
```

## ✅ 验证安装

```bash
# 运行测试脚本验证安装
./test_rag_installation.sh
```

## 🎯 启动服务

```bash
# 启动MinIO服务
./start_rag_simple.sh

# 启动后端服务（新终端）
cd backend && source venv/bin/activate && python run.py

# 启动前端服务（新终端）
cd frontend && npm run dev
```

## 🌐 访问地址

- **前端应用**: http://localhost:8081
- **MinIO控制台**: http://localhost:9001 (用户名/密码: minioadmin/minioadmin)

## 📖 使用RAG功能

1. 打开前端应用
2. 进入公文生成页面
3. 点击"上传文件作为参考"按钮
4. 选择PDF、Word、Excel等文档
5. 系统自动处理并存储到知识库
6. 文件处理完成后即可作为参考使用

## 🔧 如果安装失败

### 方案一：加速器安装
```bash
./install_rag_accelerated.sh
```

### 方案二：修复版安装
```bash
./install_rag_fix.sh
```

### 方案三：手动安装
```bash
cd backend
source venv/bin/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple minio sentence-transformers chromadb pypdf2 python-docx openpyxl pandas numpy
```

## 📚 详细文档

- [完整安装指南](RAG_INSTALL_GUIDE.md)
- [功能详细说明](RAG_KNOWLEDGE_BASE.md)
- [实现总结](RAG_IMPLEMENTATION_SUMMARY.md)

## 🆘 常见问题

**Q: 安装速度慢？**
A: 使用超简化安装脚本，已配置国内镜像源

**Q: 依赖安装失败？**
A: 尝试加速器安装或修复版安装脚本

**Q: MinIO启动失败？**
A: 检查端口9000是否被占用，或修改配置文件中的端口

**Q: 向量数据库错误？**
A: 检查backend/vector_db目录权限，确保可写

## 📞 技术支持

如果遇到问题，请：
1. 运行测试脚本：`./test_rag_installation.sh`
2. 查看日志文件：`backend/logs/`
3. 检查错误信息并参考详细文档 