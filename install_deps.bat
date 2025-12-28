@echo off
echo 正在安装 Python 依赖包...
cd /d %~dp0

REM 检查是否在虚拟环境中
if not exist "venv\Scripts\activate.bat" (
    echo 未找到虚拟环境，创建新的虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
pip install --upgrade pip
pip install pymysql flask flask-sqlalchemy sqlalchemy opendigger-pycli requests

echo.
echo 安装完成！
echo 现在可以运行: python run.py
pause