import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("计算机科学与技术就业可视化平台")
    print("=" * 60)
    print("启动地址: http://127.0.0.1:5000")
    print("API测试: http://127.0.0.1:5000/api/")
    print("健康检查: http://127.0.0.1:5000/api/health")
    print("技术热度: http://127.0.0.1:5000/api/tech_heat")
    print("=" * 60)
    print("\n📡 已注册的路由:")#显示路由

    url_rules = list(app.url_map.iter_rules())
    url_rules.sort(key=lambda x: x.rule)
    
    for rule in url_rules:
        methods = ','.join(sorted([m for m in rule.methods if m not in ['OPTIONS', 'HEAD']]))
        if methods:
            print(f"  {rule.rule} [{methods}]")
    
    print("\n" + "=" * 60)
    print(" 正在启动服务器...")
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    # 启动Flask应用
    try:
        app.run(
            host='0.0.0.0',  # 允许所有IP访问
            port=5000,       # 端口号
            debug=True,      # 调试模式
            threaded=True,   # 支持多线程
            use_reloader=True  # 自动重载
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")