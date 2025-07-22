# RAG知识库外挂功能实现说明

## 功能概述

本系统实现了基于RAG（Retrieval-Augmented Generation）的知识库外挂功能，允许用户上传文档作为参考，在生成公文时利用知识库内容增强生成质量。

## 技术架构

### 核心组件

1. **MinIO S3存储** - 文件存储服务
2. **MinerU智能解析** - 文档解析和文本提取
3. **ChromaDB向量数据库** - 向量存储和检索
4. **Sentence Transformers** - 文本向量化
5. **Flask后端API** - 服务接口
6. **Vue 3前端** - 用户界面

### 数据流程

```
用户上传文件 → MinerU解析 → 文本分块 → 向量化 → 存储到ChromaDB → RAG检索 → 大语言模型生成
```

## 功能特性

### 1. 文件上传和管理
- 支持多种文档格式：PDF、Word、Excel、TXT、Markdown、CSV
- 文件大小限制：50MB
- 自动文件去重和版本管理
- 异步处理，不阻塞用户操作

### 2. 智能文档解析
- **PDF解析**：使用PyPDF2提取文本和元数据
- **Word解析**：支持docx和doc格式，提取段落和表格
- **Excel解析**：支持xlsx和xls格式，提取工作表数据
- **文本解析**：支持多种编码格式
- **元数据提取**：自动提取文档标题、作者、创建时间等信息

### 3. 向量化处理
- 使用多语言向量模型：`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- 智能文本分块：1000词/块，200词重叠
- 自动向量生成和存储

### 4. 语义检索
- 基于余弦相似度的语义搜索
- 可配置的相似度阈值（默认0.7）
- 支持Top-K检索（默认5个结果）
- 批量搜索支持

### 5. 知识库管理
- 文件状态跟踪：processing、completed、failed
- 检索日志记录
- 统计信息展示
- 文件删除和向量重建

## API接口

### 文件上传
```
POST /api/knowledge/upload
Content-Type: multipart/form-data

Response:
{
  "success": true,
  "file_id": 123,
  "file_name": "document_20250127_123456.pdf",
  "original_name": "document.pdf",
  "status": "processing",
  "message": "文件上传成功，正在处理中..."
}
```

### 知识库搜索
```
POST /api/knowledge/search
Content-Type: application/json

Body:
{
  "query": "搜索查询",
  "top_k": 5
}

Response:
{
  "success": true,
  "query": "搜索查询",
  "results": [
    {
      "content": "检索到的文档内容",
      "file_name": "document.pdf",
      "similarity_score": 0.85,
      "rank": 1,
      "metadata": {...}
    }
  ],
  "total_results": 3,
  "response_time_ms": 150
}
```

### 文件管理
```
GET /api/knowledge/files - 获取文件列表
GET /api/knowledge/files/{file_id} - 获取文件详情
DELETE /api/knowledge/files/{file_id} - 删除文件
POST /api/knowledge/files/{file_id}/regenerate - 重新生成向量
```

### 统计信息
```
GET /api/knowledge/stats - 获取统计信息
GET /api/knowledge/health - 健康检查
```

## 数据库设计

### knowledge_files表
```sql
CREATE TABLE knowledge_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    upload_time DATETIME NOT NULL,
    status ENUM('processing', 'completed', 'failed') DEFAULT 'processing',
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### document_chunks表
```sql
CREATE TABLE document_chunks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT NOT NULL,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_size INT NOT NULL,
    vector_id VARCHAR(255),
    embedding_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES knowledge_files(id) ON DELETE CASCADE
);
```

### retrieval_logs表
```sql
CREATE TABLE retrieval_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_text TEXT NOT NULL,
    retrieved_chunks JSON,
    document_type VARCHAR(50),
    user_id VARCHAR(100),
    response_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 配置说明

### MinIO配置
```python
MINIO_CONFIG = {
    'endpoint': 'localhost:9000',
    'access_key': 'minioadmin',
    'secret_key': 'minioadmin',
    'secure': False,
    'region': 'us-east-1'
}
```

### 知识库配置
```python
KNOWLEDGE_BASE_CONFIG = {
    'bucket_name': 'knowledge-base',
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'embedding_model': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
    'max_tokens': 4000,
    'temperature': 0.7,
    'top_k': 5,
    'similarity_threshold': 0.7
}
```

### 向量数据库配置
```python
VECTOR_DB_CONFIG = {
    'type': 'chroma',
    'persist_directory': './vector_db',
    'collection_name': 'knowledge_base'
}
```

## 部署要求

### 系统依赖
- Python 3.8+
- Node.js 16+
- MySQL 5.7+
- MinIO Server

### Python依赖
```
minio==7.2.0
sentence-transformers==2.2.2
langchain==0.1.0
langchain-community==0.0.10
chromadb==0.4.22
faiss-cpu==1.7.4
pypdf2==3.0.1
python-docx==0.8.11
mammoth==1.6.0
openpyxl==3.1.2
pandas==2.1.4
numpy==1.24.3
scikit-learn==1.3.2
tiktoken==0.5.2
python-multipart==0.0.6
aiofiles==23.2.1
```

## 使用指南

### 1. 启动MinIO服务
```bash
# 下载并启动MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
./minio server /data --console-address ":9001"
```

### 2. 安装Python依赖
```bash
pip install -r requirements_rag.txt
```

### 3. 配置环境变量
```bash
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minioadmin
export MINIO_SECRET_KEY=minioadmin
```

### 4. 启动服务
```bash
# 启动后端服务
cd backend
python main.py

# 启动前端服务
cd frontend
npm run dev
```

### 5. 使用知识库功能
1. 在公文生成页面，点击"上传文件作为参考"按钮
2. 选择要上传的文档文件
3. 系统自动解析、向量化并存储到知识库
4. 在生成公文时，系统会自动检索相关知识库内容

## 性能优化

### 1. 向量化优化
- 使用GPU加速（如果可用）
- 批量处理文档块
- 缓存向量模型

### 2. 检索优化
- 索引优化
- 查询缓存
- 并行检索

### 3. 存储优化
- 文件压缩
- 向量压缩
- 定期清理

## 监控和日志

### 日志配置
```python
RAG_LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/rag.log'
}
```

### 监控指标
- 文件上传成功率
- 处理时间统计
- 检索响应时间
- 向量数据库状态

## 故障排除

### 常见问题

1. **MinIO连接失败**
   - 检查MinIO服务状态
   - 验证访问密钥配置
   - 检查网络连接

2. **向量化失败**
   - 检查模型下载
   - 验证内存使用
   - 检查文件格式

3. **检索结果为空**
   - 检查相似度阈值设置
   - 验证向量数据库状态
   - 检查查询文本质量

### 调试命令
```bash
# 检查MinIO状态
mc admin info local

# 检查向量数据库
python -c "import chromadb; print(chromadb.__version__)"

# 检查模型下载
python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"
```

## 扩展功能

### 未来计划
1. **多模态支持** - 支持图片、音频等多媒体文件
2. **实时更新** - 支持文档实时同步
3. **权限管理** - 用户级别的知识库访问控制
4. **版本控制** - 文档版本管理和回滚
5. **协作功能** - 多用户协作编辑和共享

### 集成建议
1. **与现有系统集成** - 与公文生成系统深度集成
2. **API扩展** - 提供更多RESTful API接口
3. **Webhook支持** - 支持事件通知
4. **插件系统** - 支持第三方插件扩展

## 总结

RAG知识库外挂功能为公文生成系统提供了强大的知识增强能力，通过智能文档解析、向量化存储和语义检索，显著提升了公文生成的质量和准确性。该功能采用模块化设计，易于扩展和维护，为未来的功能增强奠定了坚实的基础。 