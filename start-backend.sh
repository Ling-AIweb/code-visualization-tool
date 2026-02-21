#!/bin/bash

echo "🔧 启动后端 API 服务..."

cd /Users/liwei/Desktop/demo/0218/backend

# 激活虚拟环境
source venv/bin/activate

echo "📍 API 地址: http://localhost:8000"
echo "📍 API 文档: http://localhost:8000/docs"
echo "📍 按 Ctrl+C 停止服务"
echo ""

python main.py
