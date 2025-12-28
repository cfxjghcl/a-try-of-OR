#用于查看项目信息
#!/usr/bin/env python3
"""
项目信息查看脚本
位置: scripts/utils/project_info.py
使用方法: python scripts/utils/project_info.py
"""

import os
import sys
import subprocess
from pathlib import Path

def get_project_info():
    """获取项目信息"""
    print("📁 项目结构信息")
    print("=" * 60)
    
    # 获取当前脚本所在目录（项目根目录）
    project_root = Path(__file__).parent.parent.parent
    print(f"项目根目录: {project_root}")
    
    # 列出目录结构
    print("\n📂 目录结构:")
    for item in project_root.iterdir():
        if item.is_dir():
            # 统计子目录中的文件数量
            file_count = len(list(item.rglob("*.*")))
            print(f"  {item.name}/ - {file_count} 个文件")
    
    # 检查关键文件
    print("\n🔍 关键文件检查:")
    key_files = [
        ("backend/run.py", "后端启动文件"),
        ("backend/requirements.txt", "Python依赖"),
        ("frontend/package.json", "前端配置"),
        ("README.md", "项目说明"),
        ("scripts/setup.bat", "初始化脚本"),
    ]
    
    for file_path, description in key_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path} - {description}")
        else:
            print(f"  ❌ {file_path} - {description} (缺失)")
    
    # 检查 Python 环境
    print("\n🐍 Python 环境:")
    python_exe = sys.executable
    print(f"  解释器: {python_exe}")
    
    try:
        result = subprocess.run([python_exe, "--version"], capture_output=True, text=True)
        print(f"  版本: {result.stdout.strip()}")
    except:
        print("  无法获取版本信息")
    
    # 检查虚拟环境
    venv_path = project_root / "backend" / "venv"
    if venv_path.exists():
        print(f"  虚拟环境: {venv_path}")
    else:
        print("  虚拟环境: 未找到")

def main():
    get_project_info()
    
    print("\n" + "=" * 60)
    print("🛠️  可用脚本:")
    print("  1. 初始化项目: python scripts/setup.bat")
    print("  2. 测试数据库: python scripts/database/test_mysql.py")
    print("  3. 修复 MySQL: python scripts/database/fix_mysql.py")
    print("  4. 测试 API: python scripts/testing/test_api.py")
    
    input("\n按 Enter 键退出...")

if __name__ == "__main__":
    main()