#!/bin/bash

echo "======================================"
echo "智能质量保证系统 - 启动脚本"
echo "======================================"

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python3"
    exit 1
fi

echo "Python 版本:"
python3 --version

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo ""
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "安装依赖..."
pip install -r requirements.txt -q

echo ""
echo "======================================"
echo "启动服务器..."
echo "访问 API 文档: http://localhost:8000/docs"
echo "======================================"
echo ""

# 启动服务器
python main.py
