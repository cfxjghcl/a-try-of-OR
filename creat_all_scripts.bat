@echo off
echo 创建项目脚本目录结构...
echo.

REM 创建目录
mkdir scripts 2>nul
mkdir scripts\database 2>nul
mkdir scripts\testing 2>nul
mkdir scripts\deployment 2>nul
mkdir scripts\utils 2>nul

echo ✅ 目录结构创建完成
echo.
echo 请将相应的Python脚本文件复制到对应目录：
echo.
echo scripts\database\test_mysql.py    - 测试MySQL连接
echo scripts\database\fix_mysql.py     - 修复MySQL问题
echo scripts\testing\test_api.py       - 测试API接口
echo scripts\utils\project_info.py     - 查看项目信息
echo.
echo 然后运行 run_tests.bat 进行测试
echo.

pause