@echo off
echo ======================================
echo 智能质量保证系统 - 启动脚本
echo ======================================

REM 检查 Python 环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

echo Python 版本:
python --version

REM 检查虚拟环境
if not exist "venv" (
    echo.
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo.
echo 安装依赖...
pip install -r requirements.txt -q

echo.
echo ======================================
echo 启动服务器...
echo 访问 API 文档: http://localhost:8000/docs
echo ======================================
echo.

REM 启动服务器
python main.py
