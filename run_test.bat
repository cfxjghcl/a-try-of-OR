@echo off
echo ====================================
echo   项目测试套件
echo ====================================
echo.

:menu
echo 请选择测试类型：
echo 1. 数据库连接测试
echo 2. API 接口测试
echo 3. 完整测试（数据库 + API）
echo 4. 查看项目信息
echo 5. 退出
echo.

set /p choice="请输入选项 (1-5): "

if "%choice%"=="1" goto test_db
if "%choice%"=="2" goto test_api
if "%choice%"=="3" goto test_all
if "%choice%"=="4" goto project_info
if "%choice%"=="5" goto exit

echo 无效选项，请重新输入
goto menu

:test_db
echo 运行数据库测试...
python scripts\database\test_mysql.py
goto menu

:test_api
echo 运行 API 测试...
python scripts\testing\test_api.py
goto menu

:test_all
echo 运行完整测试...
echo.
echo [1] 数据库测试
python scripts\database\test_mysql.py
echo.
echo [2] API 测试
python scripts\testing\test_api.py
goto menu

:project_info
echo 查看项目信息...
python scripts\utils\project_info.py
goto menu

:exit
echo 退出测试套件
pause