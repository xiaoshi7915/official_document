# 官方AI写作系统

基于GB/T9704-2012标准的党政机关公文生成智能体系统。

## 系统概述

本系统是一个完整的党政机关公文生成平台，支持多种公文类型的智能生成，包括报告、公报、公告、函送、纪要、决定、决议、命令、批复、请示、通报、通告、通知、议案、意见等15种公文类型。

## 技术架构

- **前端**：Vue.js 3 + Vite + Element Plus
- **后端**：Python Flask + FastAPI
- **AI模型**：sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- **向量数据库**：ChromaDB
- **文件存储**：MinIO
- **数据库**：MySQL

## 系统特性

- ✅ 支持15种公文类型
- ✅ 智能内容生成
- ✅ 文件上传和知识库管理
- ✅ 模板预览和选择
- ✅ 符合GB/T9704-2012标准
- ✅ 离线AI模型支持
- ✅ 完整的SPA路由支持
- ✅ API代理和静态文件服务

## 快速开始

### 1. 环境要求

- Python 3.12+
- Node.js 16+
- MySQL 8.0+
- MinIO (可选，用于文件存储)

### 2. 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd official_document

# 一键启动（包含所有依赖安装和配置）
bash 修复版启动脚本.sh
```

### 3. 访问系统

- **前端界面**：http://localhost:8081
- **后端API**：http://localhost:5003

## 详细部署步骤

### 1. 下载AI模型

```bash
bash 下载AI模型.sh
```

### 2. 配置防火墙

```bash
bash configure_firewall.sh
```

### 3. 启动系统

```bash
bash 修复版启动脚本.sh
```

## 项目结构

```
official_document/
├── backend/                 # 后端服务
│   ├── main.py             # 主应用入口
│   ├── config_rag.py       # RAG配置
│   ├── venv/               # Python虚拟环境
│   └── ...
├── frontend/               # 前端应用
│   ├── src/                # 源代码
│   ├── public/             # 静态资源
│   ├── dist/               # 构建输出
│   └── ...
├── models/                 # AI模型文件
├── data/                   # 数据目录
├── 前端服务器.py           # 改进的前端服务器
├── 修复版启动脚本.sh       # 完整启动脚本
├── 下载AI模型.sh           # 模型下载脚本
├── configure_firewall.sh   # 防火墙配置
└── README.md              # 项目说明
```

## 核心文件说明

### 启动脚本

- **`修复版启动脚本.sh`**：完整的系统启动脚本，包含前端构建、后端启动、服务验证等所有步骤

### 前端服务器

- **`前端服务器.py`**：改进的前端服务器，支持SPA路由、API代理、静态文件服务

### 配置文件

- **`backend/config_rag.py`**：RAG知识库配置
- **`frontend/vite.config.js`**：前端构建配置

## 功能模块

### 1. 公文生成

- 支持15种公文类型
- 智能内容生成
- 模板预览和选择
- 实时预览

### 2. 知识库管理

- 文件上传（支持PDF、DOCX、TXT、MD等格式）
- 文档向量化存储
- 智能检索和匹配

### 3. 用户界面

- 响应式设计
- 现代化UI
- 直观的操作流程

## 问题解决

系统已解决的主要问题：

- ✅ Vue模块解析问题
- ✅ SPA路由404问题  
- ✅ API请求404问题
- ✅ 模板图片404问题
- ✅ 公文类型下拉框无数据
- ✅ 文件上传失败
- ✅ 生成正文/标题失败

详细解决方案请参考：[问题修复总结.md](问题修复总结.md)

## 日志查看

```bash
# 后端日志
tail -f backend/backend.log

# 前端日志
tail -f frontend.log
```

## 服务管理

```bash
# 停止服务
pkill -f 'python.*main.py' && pkill -f '前端服务器.py'

# 重启服务
bash 修复版启动脚本.sh
```

## 开发说明

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 后端开发

```bash
cd backend
source venv/bin/activate
python main.py
```

## 技术特点

1. **离线AI模型**：支持完全离线运行
2. **智能代理**：前端服务器自动代理API请求
3. **路由支持**：完整的SPA路由支持
4. **文件服务**：静态文件和模板文件自动服务
5. **错误处理**：完善的异常处理机制

## 许可证

本项目遵循相关开源许可证。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 联系方式

如有问题，请通过GitHub Issues联系。
