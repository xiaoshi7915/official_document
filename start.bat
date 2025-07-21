@echo off
echo 启动党政机关公文生成服务...
echo.

echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo Python未安装或未添加到PATH，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 检查Node.js环境...
node --version
if %errorlevel% neq 0 (
    echo Node.js未安装或未添加到PATH，请先安装Node.js 16+
    pause
    exit /b 1
)

echo.
echo 安装后端依赖...
cd backend
if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装Python依赖包...
pip install -r requirements.txt

echo 创建必要目录...
if not exist output mkdir output
if not exist temp mkdir temp

echo.
echo 启动后端服务...
start "Backend Server" cmd /k "cd /d %cd% && venv\Scripts\activate.bat && python main.py"

cd ..

echo.
echo 安装前端依赖...
cd frontend
if not exist node_modules (
    echo 安装npm依赖包...
    npm install
)

echo.
echo 启动前端服务...
start "Vue Frontend" cmd /k "cd /d %cd% && npm run dev"

cd ..

echo.
echo 服务启动完成！
echo 后端API: http://localhost:5000
echo 前端界面: http://localhost:5173
echo.
echo 按任意键退出...
pause