

@echo off
echo ====================================
echo   OR 项目一键部署
echo ====================================
echo.

:menu
echo 请选择部署方式：
echo   1. 开发环境部署（本地运行）
echo   2. 生产环境部署（Windows 服务）
echo   3. 仅部署后端
echo   4. 仅部署前端
echo   5. 卸载服务
echo   6. 退出
echo.

set /p choice="请输入选项 (1-6): "

if "%choice%"=="1" goto dev
if "%choice%"=="2" goto prod
if "%choice%"=="3" goto backend
if "%choice%"=="4" goto frontend
if "%choice%"=="5" goto uninstall
if "%choice%"=="6" goto exit

echo ❌ 无效选项！
goto menu

:dev
echo 启动开发环境部署...
call scripts\deployment\deploy.bat
goto menu

:prod
echo 启动生产环境部署...
call scripts\deployment\deploy_prod.bat
goto menu

:backend
echo 仅部署后端...
cd backend
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else (
    python -m venv venv
    call venv\Scripts\activate.bat
)
pip install -r requirements.txt
echo 🚀 启动后端服务...
start cmd /k "venv\Scripts\activate && python run.py"
cd ..
echo ✅ 后端已启动: http://localhost:5000
goto menu

:frontend
echo 仅部署前端...
if exist "frontend\package.json" (
    cd frontend
    npm install
    echo 🚀 启动前端服务...
    start cmd /k "npm run dev"
    cd ..
    echo ✅ 前端已启动: http://localhost:3000
) else (
    echo ❌ 未找到前端项目！
)
goto menu

:uninstall
echo 卸载服务...
net stop "OR-Flask-Service" 2>nul
sc delete "OR-Flask-Service" 2>nul
echo ✅ 服务已卸载
goto menu

:exit
echo 退出部署脚本
pause