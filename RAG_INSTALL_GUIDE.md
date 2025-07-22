# RAG知识库外挂功能安装指南

## 安装方式选择

### 方式一：超简化安装（强烈推荐）
使用国内镜像源，只安装核心依赖，速度最快：

```bash
# 1. 进入项目目录
cd /opt/office_ai_writer/official_document

# 2. 运行超简化安装脚本
./install_rag_ultra_simple.sh
```

### 方式二：加速器安装（推荐）
使用国内镜像源，安装完整功能：

```bash
# 1. 进入项目目录
cd /opt/office_ai_writer/official_document

# 2. 运行加速器安装脚本
./install_rag_accelerated.sh
```

### 方式三：修复版安装
如果遇到版本冲突问题，使用修复版安装脚本：

```bash
# 1. 进入项目目录
cd /opt/office_ai_writer/official_document

# 2. 运行修复版安装脚本
./install_rag_fix.sh
```

### 方式二：简化安装
如果修复版安装成功，可以尝试简化安装脚本：

```bash
# 运行简化安装脚本
./install_rag_simple.sh
```

### 方式二：完整安装
如果简化安装成功，可以运行完整安装脚本：

```bash
# 运行完整安装脚本
./install_rag.sh
```

### 方式三：手动安装
如果自动安装失败，可以手动安装：

```bash
# 1. 进入后端目录
cd backend

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 升级pip
pip install --upgrade pip

# 4. 逐个安装依赖
pip install minio==7.2.0
pip install numpy==1.24.3
pip install pandas==1.5.3
pip install scikit-learn==1.3.2
pip install sentence-transformers==2.2.2
pip install chromadb==0.4.22
pip install faiss-cpu==1.7.4
pip install pypdf2==3.0.1
pip install python-docx==0.8.11
pip install openpyxl==3.1.2
pip install tiktoken==0.5.2
pip install python-multipart==0.0.6
pip install aiofiles==23.2.1
pip install requests==2.31.0
pip install python-dateutil==2.8.2
```

## 常见问题解决

### 1. pandas版本问题
如果遇到pandas版本不兼容，使用Python 3.8兼容版本：

```bash
pip install pandas==1.5.3
```

### 2. 编译错误
如果遇到编译错误，安装编译工具：

```bash
# CentOS/RHEL
sudo yum install gcc gcc-c++ python3-devel

# Ubuntu/Debian
sudo apt-get install build-essential python3-dev
```

### 3. 内存不足
如果内存不足，可以分批安装：

```bash
# 第一批：基础依赖
pip install minio==7.2.0 numpy==1.24.3 pandas==1.5.3

# 第二批：机器学习库
pip install scikit-learn==1.3.2 sentence-transformers==2.2.2

# 第三批：向量数据库
pip install chromadb==0.4.22 faiss-cpu==1.7.4

# 第四批：文档解析
pip install pypdf2==3.0.1 python-docx==0.8.11 openpyxl==3.1.2
```

### 4. 网络问题
如果网络连接慢，使用国内镜像：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple minio==7.2.0
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple sentence-transformers==2.2.2
# ... 其他依赖
```

## 验证安装

### 方式一：使用测试脚本（推荐）
```bash
# 运行自动化测试脚本
./test_rag_installation.sh
```

### 方式二：手动验证
```bash
cd backend
source venv/bin/activate
python3 -c "
import minio
import sentence_transformers
import chromadb
import PyPDF2
from docx import Document
import pandas as pd
print('所有依赖安装成功！')
"
```

## 启动服务

### 1. 启动MinIO服务
```bash
# 下载MinIO
wget -O minio https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/

# 创建数据目录
sudo mkdir -p /data/minio
sudo chown $USER:$USER /data/minio

# 启动MinIO
minio server /data/minio --console-address ":9001"
```

### 2. 启动应用
```bash
# 启动原有服务
./start_services.sh

# 或者启动RAG服务
./start_rag_services.sh
```

## 访问地址

- **前端应用**: http://localhost:8081
- **MinIO控制台**: http://localhost:9001
  - 用户名: minioadmin
  - 密码: minioadmin

## 使用RAG功能

1. 在公文生成页面，点击"上传文件作为参考"按钮
2. 选择要上传的文档文件
3. 系统自动处理并存储到知识库
4. 文件处理完成后即可作为参考使用

## 故障排除

### 1. 依赖导入失败
检查虚拟环境是否正确激活：
```bash
which python
pip list
```

### 2. MinIO连接失败
检查MinIO服务状态：
```bash
ps aux | grep minio
netstat -tlnp | grep 9000
```

### 3. 向量数据库错误
检查ChromaDB目录权限：
```bash
ls -la backend/vector_db/
```

### 4. 内存不足
增加swap空间或使用更小的模型：
```bash
# 修改config_rag.py中的模型配置
'embedding_model': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
```

## 联系支持

如果遇到其他问题，请：
1. 检查日志文件：`backend/logs/`
2. 查看错误信息
3. 参考完整文档：`RAG_KNOWLEDGE_BASE.md` 