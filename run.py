import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()
with app.app_context():
    pass  # 空操作即可，仅为激活上下文

if __name__ == '__main__':
    print("=" * 60)
    print("计算机科学与技术就业可视化平台")
    print("=" * 60)
    print("后端首页: http://127.0.0.1:5000")
    print("前端首页: http://127.0.0.1:5000/view")
    print("用户注册: POST /api/auth/register")
    print("用户登录: POST /api/auth/login")
    print("API测试: http://127.0.0.1:5000/api/")
    print("健康检查: http://127.0.0.1:5000/api/health")
    print("技术热度: http://127.0.0.1:5000/api/tech_heat")
    print("=" * 60)
    print("\n📡 已注册的路由:")#显示路由
    print("\n 用户相关路由:")
    user_routes = [('POST /api/auth/register',"用户注册"),
                   ('POST /api/auth/login',"用户登录"),
                   ('GET /api/auth/profile',"获取用户资料"),
                   ('PUT /api/auth/profile',"更新用户资料"),
                   ('GET /api/auth/recommendations',"获取职业推荐"),
                   ('GET /api/auth/learning_path',"获取学习路径"),
                   ('GET /api/favorites/careers',"获取收藏的职业"),
                   ('POST /api/favorites/careers',"添加收藏的职业"),
                   ('DELETE /api/favorites/careers/<int:career_id>',"删除收藏的职业"),
                   ]
    

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
            host='127.0.0.1',  # 关键修改：改为127.0.0.1，和前端baseURL匹配
            port=5000,       # 端口号
            debug=True,      # 调试模式
            threaded=True,   # 支持多线程
            use_reloader=True  # 自动重载
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")