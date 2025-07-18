# 党政机关公文自动生成系统

基于GB/T9704-2012标准的党政机关公文自动生成系统，支持15种公文类型的模板化生成。

![系统预览](docs/preview.png)

## 功能特点

- **标准合规**：严格遵循GB/T9704-2012党政机关公文格式标准
- **多种公文类型**：支持15种常用公文类型（公告、通知、报告、请示等）
- **多格式支持**：支持Markdown和Word格式输入
- **模板预览**：提供图片、HTML和文本三种预览模式
- **自动排版**：根据标准自动进行公文排版
- **一键生成**：快速生成符合标准的公文Word文档

## 支持的公文类型

1. **公告**：向国内外宣布重要事项或者法定事项
2. **公通**：公开通报有关情况
3. **决定**：对重要事项作出决策和部署
4. **命令**：依照有关法律公布行政法规和规章
5. **公报**：公布重要决定或重大事项
6. **意见**：对重要问题提出见解和处理办法
7. **通知**：发布、传达要求下级机关执行和有关单位周知或者执行的事项
8. **通报**：表彰先进、批评错误、传达重要精神和告知重要情况
9. **报告**：向上级机关汇报工作、反映情况、回复询问
10. **请示**：向上级机关请求指示或批准
11. **批复**：答复下级机关请示事项
12. **议函**：不相隶属机关之间商洽工作、询问和答复问题
13. **纪要**：记录会议主要情况和议定事项
14. **函送**：向有关机关和单位告知事项
15. **报送**：向上级机关报送材料

## 技术架构

### 后端

- **Python + FastAPI**：提供高性能API服务
- **python-docx**：处理Word文档生成
- **mammoth**：Word文档转HTML
- **PIL**：图像处理和预览生成

### 前端

- **Vue 3**：现代化的前端框架
- **Element Plus**：UI组件库
- **Axios**：API请求处理
- **Vue Router**：前端路由管理

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/yourusername/official-document-generator.git
cd official-document-generator
```

2. **使用启动脚本（Windows）**

```bash
start.bat
```

3. **手动安装**

后端安装：
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

前端安装：
```bash
cd frontend
npm install
```

### 启动服务

后端启动：
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

前端启动：
```bash
cd frontend
npm run dev
```

访问地址：http://localhost:3000

## 项目结构

```
├── backend/           # FastAPI后端
│   ├── models/        # 数据模型
│   ├── services/      # 业务逻辑
│   ├── output/        # 生成的文档输出目录
│   └── temp/          # 临时文件目录
├── frontend/          # Vue前端
│   ├── public/        # 静态资源
│   ├── src/           # 源代码
│   └── templates/     # 公文模板文件
└── docs/              # 文档
```

## 使用指南

1. 在首页选择需要的公文类型
2. 点击"预览模板"可以查看模板样式
3. 点击"使用此模板"或"开始生成公文"进入生成页面
4. 填写公文基本信息和正文内容
5. 点击"生成公文"按钮
6. 下载生成的Word文档

## 贡献指南

欢迎贡献代码或提出建议！请遵循以下步骤：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

如有问题或建议，请通过以下方式联系我们：

- 项目负责人：[您的名字](mailto:your.email@example.com)
- 项目主页：[GitHub项目地址](https://github.com/yourusername/official-document-generator)

## 致谢

- 感谢所有为本项目做出贡献的开发者
- 特别感谢提供公文标准和模板支持的相关机构