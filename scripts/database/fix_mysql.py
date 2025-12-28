#程序有时会启用两个sql，下脚本用于修复
#!/usr/bin/env python3
"""
MySQL 问题修复脚本
位置: scripts/database/fix_mysql.py
使用方法: python scripts/database/fix_mysql.py
"""

import subprocess
import sys
import os
import time

def run_command(cmd):
    """运行命令并打印输出"""
    print(f"运行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(f"输出: {result.stdout}")
    if result.stderr:
        print(f"错误: {result.stderr}")
    return result.returncode

def fix_mysql_windows():
    """修复 Windows 上的 MySQL 问题"""
    print("🔧 修复 Windows MySQL 服务问题")
    print("-" * 50)
    
    # 1. 停止 MySQL 服务
    print("\n[1] 停止 MySQL 服务...")
    run_command("net stop MySQL80")
    
    # 2. 强制结束 mysqld 进程
    print("\n[2] 结束所有 MySQL 进程...")
    run_command("taskkill /F /IM mysqld.exe")
    time.sleep(2)
    
    # 3. 清理锁文件
    print("\n[3] 清理锁文件...")
    mysql_path = "D:\\MySQL\\MySQL Server 8.0"
    if os.path.exists(mysql_path):
        data_dir = os.path.join(mysql_path, "Data")
        if os.path.exists(data_dir):
            for file in ["*.pid", "*.err", "*.lock"]:
                run_command(f'del /F /Q "{data_dir}\\{file}" 2>nul')
    
    # 4. 重新配置服务
    print("\n[4] 重新配置服务...")
    run_command('sc config MySQL80 start= delayed-auto')
    
    # 5. 启动服务
    print("\n[5] 启动 MySQL 服务...")
    run_command("net start MySQL80")
    time.sleep(5)
    
    # 6. 检查服务状态
    print("\n[6] 检查服务状态...")
    run_command("sc query MySQL80")
    
    print("\n✅ MySQL 修复完成")

def check_mysql_status():
    """检查 MySQL 状态"""
    print("📊 检查 MySQL 状态")
    print("-" * 50)
    
    # 检查服务
    result = subprocess.run("sc query MySQL80", shell=True, capture_output=True, text=True)
    print("服务状态:")
    print(result.stdout if result.stdout else result.stderr)
    
    # 检查进程
    result = subprocess.run("tasklist | findstr mysqld", shell=True, capture_output=True, text=True)
    print("进程状态:")
    print(result.stdout if result.stdout else "未找到 mysqld 进程")
    
    # 检查端口
    result = subprocess.run("netstat -ano | findstr :3306", shell=True, capture_output=True, text=True)
    print("端口监听:")
    print(result.stdout if result.stdout else "端口 3306 未监听")

def main():
    print("🚀 MySQL 问题修复工具")
    print("=" * 60)
    
    # 显示当前问题
    check_mysql_status()
    
    print("\n" + "=" * 60)
    print("请选择修复选项:")
    print("1. 修复 MySQL 服务（停止、清理、重启）")
    print("2. 仅检查状态")
    print("3. 创建测试数据库")
    print("4. 退出")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == "1":
        fix_mysql_windows()
    elif choice == "2":
        check_mysql_status()
    elif choice == "3":
        # 创建测试数据库
        print("\n创建测试数据库...")
        # 这里可以调用 test_mysql.py 中的函数
        sys.path.append(os.path.dirname(__file__))
        from test_mysql import create_database_if_needed
        create_database_if_needed()
    elif choice == "4":
        print("退出")
    else:
        print("无效选项")
    
    input("\n按 Enter 键退出...")

if __name__ == "__main__":
    main()