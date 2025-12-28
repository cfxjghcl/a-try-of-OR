#测试后端api
#!/usr/bin/env python3
"""
API 测试脚本
位置: scripts/testing/test_api.py
使用方法: python scripts/testing/test_api.py
"""

import requests
import json
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def test_backend_api():
    """测试后端 API"""
    print("🌐 后端 API 测试")
    print("-" * 50)
    
    base_url = "http://localhost:5000"
    endpoints = [
        "/api/tech_heat",
        "/",
        "/api/skill_market"
    ]
    
    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\n测试: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ 请求成功")
                
                # 尝试解析 JSON
                if response.headers.get('Content-Type', '').startswith('application/json'):
                    data = response.json()
                    if isinstance(data, list):
                        print(f"  返回数据条数: {len(data)}")
                        if len(data) > 0:
                            print(f"  第一条数据: {json.dumps(data[0], ensure_ascii=False)[:100]}...")
                    else:
                        print(f"  返回数据: {json.dumps(data, ensure_ascii=False)[:200]}...")
                else:
                    print(f"  返回内容: {response.text[:200]}...")
            else:
                print(f"  ❌ 请求失败")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ 无法连接到后端服务")
            print(f"     请确保 Flask 应用正在运行 (python run.py)")
        except requests.exceptions.Timeout:
            print(f"  ⏱️  请求超时")
        except Exception as e:
            print(f"  ❌ 测试出错: {e}")
    
    print("\n" + "-" * 50)
    print("📋 API 测试完成")

def test_flask_health():
    """测试 Flask 应用健康状态"""
    print("\n🏥 Flask 健康检查")
    print("-" * 50)
    
    try:
        # 尝试导入 Flask 应用
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
        
        # 尝试从 backend 导入
        try:
            from backend.app import create_app
            app = create_app()
            print("✅ Flask 应用可以正常导入")
            
            # 检查配置
            with app.app_context():
                print(f"   数据库 URI: {app.config.get('SQLALCHEMY_DATABASE_URI', '未设置')}")
                
        except ImportError as e:
            print(f"❌ 无法导入 Flask 应用: {e}")
            
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")

if __name__ == "__main__":
    print("🚀 启动 API 测试脚本")
    print("=" * 60)
    
    test_flask_health()
    test_backend_api()
    
    print("\n📋 下一步建议:")
    print("1. 如果无法连接，请启动后端: cd backend && python run.py")
    print("2. 检查数据库配置是否正确")
    print("3. 运行数据库测试: python scripts/database/test_mysql.py")
    
    input("\n按 Enter 键退出...")