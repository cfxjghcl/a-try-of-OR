@echo off
cd /d "C:\Users\荃\Desktop\A-TRY-OF-OR"

:: 1. 确保logs目录存在
if not exist "logs" (
    echo [%date% %time%] 创建logs目录
    mkdir logs
)

:: 2. 记录开始时间
echo ======================================== >> logs\sync.log
echo 开始同步: %date% %time% >> logs\sync.log
echo ======================================== >> logs\sync.log

:: 3. 执行同步并记录所有输出
echo 执行数据同步... >> logs\sync.log
python scripts\first_sync.py >> logs\sync.log 2>&1

:: 4. 检查是否成功
if %errorlevel% equ 0 (
    echo [SUCCESS] 同步完成: %date% %time% >> logs\sync.log
    echo 状态: 成功 >> logs\sync.log
) else (
    echo [ERROR] 同步失败: %date% %time% >> logs\sync.log
    echo 错误代码: %errorlevel% >> logs\sync.log
)

:: 5. 添加空行分隔
echo. >> logs\sync.log
echo. >> logs\sync.log

:: 6. 在窗口也显示提示
echo 同步完成！查看日志: logs\sync.log
