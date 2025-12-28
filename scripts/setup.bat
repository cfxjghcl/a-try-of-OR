#本文件用于一键初始化项目

@echo off
echo ====================================
echo   项目环境初始化脚本
echo ====================================
echo.

echo [1] 检查 Python 版本
python --version
if errorlevel 1 (
    echo ❌ Python 未安装
    pause
    exit /b 1
)

echo [2] 创建必要的目录结构
mkdir backend\logs 2>nul
mkdir frontend\dist 2>nul
mkdir scripts\database 2>nul
mkdir scripts\testing 2>nul
mkdir data 2>nul

echo [3] 设置虚拟环境
if exist "backend\venv" (
    echo ✅ 虚拟环境已存在
) else (
    echo 创建虚拟环境...
    cd backend
    python -m venv venv
    cd ..
)

echo [4] 安装后端依赖
if exist "backend\requirements.txt" (
    echo 安装 requirements.txt 中的包...
    call backend\venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r backend\requirements.txt
) else (
    echo 安装基础依赖包...
    call backend\venv\Scripts\activate.bat
    pip install flask flask-sqlalchemy flask-cors pymysql opendigger-pycli requests
)

echo [5] 安装前端依赖（如果存在 package.json）
if exist "frontend\package.json" (
    echo 安装前端依赖...
    cd frontend
    npm install
    cd ..
)

echo.
echo ====================================
echo   ✅ 项目初始化完成！
echo ====================================
echo.
echo 后续步骤：
echo 1. 启动后端: cd backend && python run.py
echo 2. 启动前端: cd frontend && npm run dev
echo.
pause