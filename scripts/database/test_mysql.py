#测试数据库连接
#!/usr/bin/env python3
"""
MySQL 连接测试脚本
位置: scripts/database/test_mysql.py
使用方法: python scripts/database/test_mysql.py
"""

import sys
import os

# 添加项目根目录到 Python 路径，以便导入项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def test_mysql_connection():
    """测试 MySQL 数据库连接"""
    print("🔍 MySQL 连接测试")
    print("-" * 50)
    
    # 连接配置列表
    test_cases = [
        {
            "name": "本地连接（127.0.0.1）",
            "config": {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": "123456",
                "database": "jobviz"
            }
        },
        {
            "name": "本地连接（localhost）",
            "config": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "123456",
                "database": "jobviz"
            }
        },
        {
            "name": "无密码连接",
            "config": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "",
                "database": "jobviz"
            }
        }
    ]
    
    try:
        import pymysql
        print("✅ pymysql 模块已安装")
    except ImportError:
        print("❌ pymysql 模块未安装")
        print("运行: pip install pymysql")
        return False
    
    success = False
    for test in test_cases:
        print(f"\n📊 测试: {test['name']}")
        print(f"   配置: {test['config']}")
        
        try:
            conn = pymysql.connect(**test['config'])
            
            with conn.cursor() as cursor:
                # 测试基本查询
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                print(f"   ✅ 连接成功 - MySQL版本: {version}")
                
                # 检查数据库
                cursor.execute("SELECT DATABASE()")
                db_name = cursor.fetchone()[0]
                print(f"   当前数据库: {db_name}")
                
                # 列出所有表
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print(f"   表数量: {len(tables)}")
                for table in tables[:5]:  # 只显示前5个
                    print(f"     - {table[0]}")
                if len(tables) > 5:
                    print(f"     ... 还有 {len(tables)-5} 个表")
            
            conn.close()
            success = True
            print(f"   ✅ 测试通过!")
            break
            
        except pymysql.err.OperationalError as e:
            error_code = e.args[0]
            if error_code == 1045:
                print(f"   ❌ 权限被拒绝（密码错误）")
            elif error_code == 1049:
                print(f"   ❌ 数据库不存在")
            elif error_code == 2003:
                print(f"   ❌ 无法连接到 MySQL 服务器")
            else:
                print(f"   ❌ 连接失败: {e}")
        except Exception as e:
            print(f"   ❌ 其他错误: {e}")
    
    print("\n" + "-" * 50)
    if success:
        print("🎉 MySQL 连接测试完成！")
    else:
        print("❌ 所有连接测试都失败")
    
    return success

def create_database_if_needed():
    """如果数据库不存在，则创建"""
    print("\n🔧 检查并创建数据库...")
    
    try:
        import pymysql
        
        # 连接到 MySQL（不指定数据库）
        conn = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="123456"
        )
        
        with conn.cursor() as cursor:
            # 检查数据库是否存在
            cursor.execute("SHOW DATABASES LIKE 'jobviz'")
            if cursor.fetchone():
                print("✅ 数据库 'jobviz' 已存在")
            else:
                print("创建数据库 'jobviz'...")
                cursor.execute("CREATE DATABASE jobviz CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                conn.commit()
                print("✅ 数据库 'jobviz' 已创建")
                
                # 创建表
                cursor.execute("USE jobviz")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tech_heat (
                        skill VARCHAR(40) PRIMARY KEY,
                        heat INT,
                        updated_at DATETIME
                    )
                """)
                conn.commit()
                print("✅ 表 'tech_heat' 已创建")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 启动数据库测试脚本")
    print("=" * 60)
    
    if test_mysql_connection():
        print("\n是否需要创建/初始化数据库？")
        choice = input("(y/n): ").strip().lower()
        if choice == 'y':
            create_database_if_needed()
    
    print("\n📋 下一步建议：")
    print("1. 如果连接成功，可以启动后端服务")
    print("2. 如果连接失败，检查 MySQL 服务是否启动")
    print("3. 运行 'scripts/database/fix_mysql.py' 进行修复")
    
    input("\n按 Enter 键退出...")