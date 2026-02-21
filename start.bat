@echo off
REM 代码逻辑可视化工具启动脚本 (Windows)

echo 🚀 启动代码逻辑可视化工具...

REM 检查后端虚拟环境
if not exist "backend\venv" (
    echo 📦 创建后端虚拟环境...
    cd backend
    python -m venv venv
    cd ..
)

REM 启动后端
echo 🔧 启动后端服务...
cd backend
call venv\Scripts\activate
pip install -r requirements.txt > nul 2>&1
start /B python main.py
cd ..

REM 等待后端启动
timeout /t 3 /nobreak > nul

REM 检查前端依赖
if not exist "frontend\node_modules" (
    echo 📦 安装前端依赖...
    cd frontend
    call npm install
    cd ..
)

REM 启动前端
echo 🎨 启动前端服务...
cd frontend
start /B npm run dev
cd ..

echo.
echo ✅ 服务启动成功！
echo 📍 前端地址: http://localhost:3000
echo 📍 后端地址: http://localhost:8000
echo 📍 API 文档: http://localhost:8000/docs
echo.
echo 按任意键关闭此窗口...
pause > nul
