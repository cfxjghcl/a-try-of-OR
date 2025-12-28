#生产环境部署脚本,windows的

@echo off
REM 必须以管理员身份运行
echo ====================================
echo   OR 项目生产环境部署脚本
echo ====================================
echo.
echo 注意：此脚本需要管理员权限！
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 请以管理员身份运行此脚本！
    pause
    exit /b 1
)

echo [1] 停止现有服务...
net stop "OR-Flask-Service" 2>nul
sc delete "OR-Flask-Service" 2>nul
timeout /t 3 /nobreak >nul

echo [2] 安装 Python 依赖...
cd backend
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
pip install waitress  REM Windows 生产环境 WSGI 服务器
cd ..

echo [3] 创建应用目录（如果不存在）...
set "APP_DIR=C:\Program Files\OR-App"
if not exist "%APP_DIR%" (
    mkdir "%APP_DIR%"
    echo ✅ 应用目录已创建: %APP_DIR%
)

echo [4] 复制文件到应用目录...
xcopy /E /I /Y "backend\*" "%APP_DIR%\backend\"
xcopy /E /I /Y "frontend\dist\*" "%APP_DIR%\frontend\" 2>nul
copy "scripts\deployment\or-service.xml" "%APP_DIR%\" 2>nul

echo [5] 创建 Windows 服务...
set "PYTHON_PATH=%APP_DIR%\backend\venv\Scripts\python.exe"
set "SCRIPT_PATH=%APP_DIR%\backend\run_prod.py"

REM 创建生产启动脚本
echo from waitress import serve > "%APP_DIR%\backend\run_prod.py"
echo from app import create_app >> "%APP_DIR%\backend\run_prod.py"
echo. >> "%APP_DIR%\backend\run_prod.py"
echo app = create_app() >> "%APP_DIR%\backend\run_prod.py"
echo if __name__ == '__main__': >> "%APP_DIR%\backend\run_prod.py"
echo     serve(app, host='0.0.0.0', port=5000) >> "%APP_DIR%\backend\run_prod.py"

REM 创建 NSSM 服务（需要先下载 nssm.exe）
echo [6] 设置 Windows 服务（使用 NSSM）...
if not exist "nssm.exe" (
    echo   下载 NSSM 工具...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'"
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath '.'"
    move "nssm-2.24\win64\nssm.exe" . 2>nul
    rmdir /s /q "nssm-2.24" 2>nul
    del "nssm.zip" 2>nul
)

REM 创建服务
nssm install "OR-Flask-Service" "%PYTHON_PATH%" "%SCRIPT_PATH%"
nssm set "OR-Flask-Service" AppDirectory "%APP_DIR%\backend"
nssm set "OR-Flask-Service" DisplayName "OR Flask Application"
nssm set "OR-Flask-Service" Description "开源项目技术栈热度可视化系统"
nssm set "OR-Flask-Service" Start SERVICE_AUTO_START
nssm set "OR-Flask-Service" AppStdout "%APP_DIR%\backend\logs\service.log"
nssm set "OR-Flask-Service" AppStderr "%APP_DIR%\backend\logs\error.log"

echo [7] 启动服务...
net start "OR-Flask-Service"

echo.
echo ====================================
echo   ✅ 生产环境部署完成！
echo ====================================
echo.
echo 服务信息：
echo   - 服务名称: OR-Flask-Service
echo   - 安装目录: %APP_DIR%
echo   - 访问地址: http://localhost:5000
echo.
echo 管理命令：
echo   - 启动服务: net start OR-Flask-Service
echo   - 停止服务: net stop OR-Flask-Service
echo   - 重启服务: net stop OR-Flask-Service && net start OR-Flask-Service
echo.
echo 日志文件：
echo   - 服务日志: %APP_DIR%\backend\logs\service.log
echo   - 错误日志: %APP_DIR%\backend\logs\error.log
echo.
pause