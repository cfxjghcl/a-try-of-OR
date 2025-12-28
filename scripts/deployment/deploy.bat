#基础部署脚本（开发环境

@echo off
echo ====================================
echo   OR 项目本地部署脚本 (开发环境)
echo ====================================
echo.

REM 1. 检查是否在项目根目录
echo [1] 检查项目结构...
if not exist "backend" (
    echo ❌ 错误：请在项目根目录运行此脚本！
    echo    当前目录: %cd%
    pause
    exit /b 1
)

REM 2. 激活 Python 虚拟环境
echo [2] 激活 Python 虚拟环境...
if exist "backend\venv\Scripts\activate.bat" (
    call backend\venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else (
    echo ⚠️  未找到虚拟环境，正在创建...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已创建
    cd ..
)

REM 3. 安装后端依赖
echo [3] 安装后端依赖...
cd backend
if exist "requirements.txt" (
    echo   安装 requirements.txt 中的包...
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo   安装基础依赖包...
    pip install flask flask-sqlalchemy flask-cors pymysql opendigger-pycli requests
)
cd ..

REM 4. 初始化数据库
echo [4] 初始化数据库...
python scripts\database\test_mysql.py
if errorlevel 1 (
    echo ⚠️  数据库连接失败，使用 SQLite 作为后备...
    REM 这里可以添加切换到 SQLite 的逻辑
)

REM 5. 创建必要目录
echo [5] 创建必要目录...
mkdir backend\logs 2>nul
mkdir backend\data 2>nul
mkdir frontend\dist 2>nul 2>nul

REM 6. 启动后端服务
echo [6] 启动后端服务...
echo    后端将在新窗口中启动...
start cmd /k "cd /d backend && venv\Scripts\activate && python run.py"
echo    ✅ 后端已启动 (http://localhost:5000)

REM 7. 启动前端服务（如果存在）
echo [7] 检查并启动前端...
if exist "frontend\package.json" (
    echo    前端将在新窗口中启动...
    start cmd /k "cd /d frontend && npm run dev"
    echo    ✅ 前端已启动 (http://localhost:3000)
) else (
    echo    ⚠️  未找到前端项目，跳过前端启动
)

echo.
echo ====================================
echo   🎉 部署完成！
echo ====================================
echo.
echo 访问地址：
echo   - 后端 API: http://localhost:5000
echo   - 后端管理: http://localhost:5000/admin
if exist "frontend\package.json" (
echo   - 前端页面: http://localhost:3000
)
echo.
echo 日志文件：
echo   - 后端日志: backend\logs\flask.log
echo   - 定时任务: backend\logs\cron.log
echo.
pause