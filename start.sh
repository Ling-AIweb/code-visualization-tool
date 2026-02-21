#!/bin/bash

# 代码逻辑可视化工具启动脚本

echo "🚀 启动代码逻辑可视化工具..."

# 检查后端虚拟环境
if [ ! -d "backend/venv" ]; then
    echo "📦 创建后端虚拟环境..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# 启动后端
echo "🔧 启动后端服务..."
cd backend
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
python main.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

# 启动前端
echo "🎨 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ 服务启动成功！"
echo "📍 前端地址: http://localhost:3000"
echo "📍 后端地址: http://localhost:8000"
echo "📍 API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待进程
wait $BACKEND_PID $FRONTEND_PID
