@echo off
echo ========================================
echo   GitHub技能数据同步工具
echo ========================================
echo 开始时间: %date% %time%

cd /d "C:\Users\荃\Desktop\A-TRY-OF-OR"

echo 正在同步数据...
python scripts\first_sync.py

echo.
echo 完成时间: %date% %time%
echo ========================================
timeout /t 3 > nul