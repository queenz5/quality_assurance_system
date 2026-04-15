#!/bin/bash

echo "======================================"
echo "质量保障系统 - 前端启动"
echo "======================================"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "错误: 未找到 Node.js，请先安装 Node.js"
    exit 1
fi

echo "Node.js 版本:"
node --version

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo ""
    echo "安装依赖..."
    npm install
fi

echo ""
echo "======================================"
echo "启动开发服务器..."
echo "访问地址: http://localhost:3000"
echo "======================================"
echo ""

# 启动开发服务器
npm run dev
