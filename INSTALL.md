# 安装部署指南

## 系统要求

### 软件环境
- Python 3.8+ 
- Node.js 16+
- npm 或 yarn

### 操作系统
- Windows 10/11
- Windows Server 2016+

## 快速安装

### 方法一：使用启动脚本（推荐）

1. 双击运行 `start.bat`
2. 脚本会自动检查环境并安装依赖
3. 启动完成后访问 http://localhost:5173

### 方法二：手动安装

#### 1. 安装后端依赖

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. 安装前端依赖

```bash
cd frontend
npm install
```

#### 3. 启动服务

启动后端：
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

启动前端：
```bash
cd frontend
npm run dev
```

## 配置说明

### 后端配置
- 配置文件：`backend/config.py`
- 端口：5000
- 输出目录：`backend/output`
- 临时目录：`backend/temp`

### 前端配置
- 配置文件：`frontend/vite.config.js`
- 端口：5173
- API代理：自动代理到后端5000端口

## 模板配置

1. 将15个公文模板文件放入 `templates` 目录
2. 模板文件命名格式：`{类型}.docx`
3. 支持的模板类型见 `templates/README.md`

## 访问地址

- 前端界面：http://localhost:5173
- 后端API：http://localhost:5000
- API文档：http://localhost:5000/docs

## 常见问题

### Q: Python环境问题
A: 确保安装Python 3.8+，并添加到系统PATH

### Q: Node.js环境问题  
A: 确保安装Node.js 16+，并添加到系统PATH

### Q: 端口占用问题
A: 修改配置文件中的端口号，或关闭占用端口的程序

### Q: 模板文件问题
A: 确保模板文件格式正确，放置在templates目录下

## 生产部署

### 后端部署
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000
```

### 前端部署
```bash
npm run build
# 将dist目录部署到Web服务器
```

### Nginx配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 技术支持

如遇到问题，请检查：
1. 系统环境是否满足要求
2. 依赖包是否正确安装
3. 端口是否被占用
4. 模板文件是否完整