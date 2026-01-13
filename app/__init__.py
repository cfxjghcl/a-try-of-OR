from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import sys
import os
from datetime import datetime, timedelta

# ========== 全局扩展初始化 ==========
# 数据库对象（全局唯一，所有模型共享）
db = SQLAlchemy()

def create_app():
    # 1. 创建Flask应用实例
    app = Flask(__name__)
    
    # ========== 核心配置 ==========
    # 数据库配置（SQLite，路径指向项目根目录）
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭修改追踪，减少开销
    app.config['JSON_AS_ASCII'] = False  # 支持中文返回
    app.config['SECRET_KEY'] = 'your-secret-key-123'  # JWT/会话加密必备
    
    # 跨域配置（开发环境允许所有来源，生产环境需限制）
    CORS(app, supports_credentials=True)
    
    # ========== 扩展绑定 ==========
    db.init_app(app)  # 将db绑定到当前应用
    
    # ========== 导入外部模型（已修复重复定义/字段问题） ==========
    try:
        # 将项目根目录加入Python路径，确保能导入app.models
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.models import (
            User, TechHeat, EmploymentTrend, 
            SalaryTrend, WordCloud, Career
        )
        print("✅ 外部模型导入成功（models.py）")
    except ImportError as e:
        print(f"❌ 外部模型导入失败：{e}，请检查models.py是否完整")
        raise  # 导入失败直接终止，避免连锁异常
    
    # ========== 注册蓝图（优先使用蓝图管理路由） ==========
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from routes import api_bp, main_bp
        # 给API蓝图统一加/api前缀，避免路由冲突
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(main_bp)
        print("✅ 蓝图注册成功：api_bp、main_bp")
    except ImportError as e:
        print(f"⚠️  蓝图导入失败：{e}，将使用内置临时路由")
        
        # ========== 内置临时路由（蓝图失效时备用） ==========
        # 技术热度接口
        @app.route('/api/tech_heat')
        def tech_heat():
            try:
                data = TechHeat.query.all()
                return {"code": 200, "data": [{"skill": d.skill, "heat": d.heat} for d in data]}
            except Exception as e:
                return {"code": 500, "msg": str(e)}, 500

        # 就业趋势接口
        @app.route('/api/employment-trend')
        def employment_trend():
            try:
                data = EmploymentTrend.query.all()
                return {"code": 200, "data": [{"year": d.year, "profession": d.profession, "number": d.number} for d in data]}
            except Exception as e:
                return {"code": 500, "msg": str(e)}, 500

        # 薪资趋势接口（适配修复后的SalaryTrend模型）
        @app.route('/api/salary-trend')
        def salary_trend():
            try:
                data = SalaryTrend.query.join(Career).all()
                return {
                    "code": 200,
                    "data": [
                        {
                            "year": d.year,
                            "profession": d.career.name,  # 关联Career表获取职业名称
                            "avg_salary": d.avg_salary,
                            "min_salary": d.min_salary,
                            "max_salary": d.max_salary
                        } for d in data
                    ]
                }
            except Exception as e:
                return {"code": 500, "msg": str(e)}, 500

        # 词云数据接口
        @app.route('/api/wordcloud')
        def wordcloud():
            try:
                data = WordCloud.query.all()
                return {"code": 200, "data": [{"word": d.word, "count": d.count} for d in data]}
            except Exception as e:
                return {"code": 500, "msg": str(e)}, 500

    # ========== 通用基础接口（所有环境保留） ==========
    # 健康检查接口
    @app.route('/api/health')
    def health():
        return {"code": 200, "msg": "服务器正常运行"}

    # 测试连接接口
    @app.route('/api/test-connection')
    def test_connection():
        return {"code": 200, "msg": "前后端连接成功"}

    # ========== 数据库初始化（修复字段不匹配/重复数据问题） ==========
    with app.app_context():
        # 创建所有表（仅首次运行创建，已有表不会覆盖）
        db.create_all()
        
        # 1. 插入Career测试数据（为SalaryTrend提供career_id）
        if not Career.query.first():
            career_list = [
                Career(name='后端开发', category='开发', avg_entry_salary=15000, demand_level='高'),
                Career(name='前端开发', category='开发', avg_entry_salary=14000, demand_level='中')
            ]
            db.session.add_all(career_list)
            db.session.commit()
            print("✅ Career测试数据插入完成")
        
        # 2. 插入TechHeat测试数据
        if not TechHeat.query.first():
            tech_heat_list = [
                TechHeat(skill='Python', heat=95),
                TechHeat(skill='JavaScript', heat=88),
                TechHeat(skill='Java', heat=85)
            ]
            db.session.add_all(tech_heat_list)
            db.session.commit()
            print("✅ TechHeat测试数据插入完成")
        
        # 3. 插入EmploymentTrend测试数据
        if not EmploymentTrend.query.first():
            employment_list = [
                EmploymentTrend(year=2020, profession='后端开发', number=1000),
                EmploymentTrend(year=2021, profession='前端开发', number=900)
            ]
            db.session.add_all(employment_list)
            db.session.commit()
            print("✅ EmploymentTrend测试数据插入完成")
        
        # 4. 插入SalaryTrend测试数据（适配career_id字段）
        if not SalaryTrend.query.first():
            backend_career = Career.query.filter_by(name='后端开发').first()
            frontend_career = Career.query.filter_by(name='前端开发').first()
            
            salary_list = [
                SalaryTrend(
                    year=2020, career_id=backend_career.id,
                    avg_salary=15000, min_salary=12000, max_salary=18000
                ),
                SalaryTrend(
                    year=2021, career_id=frontend_career.id,
                    avg_salary=14000, min_salary=11000, max_salary=17000
                )
            ]
            db.session.add_all(salary_list)
            db.session.commit()
            print("✅ SalaryTrend测试数据插入完成")
        
        # 5. 插入WordCloud测试数据
        if not WordCloud.query.first():
            word_cloud_list = [
                WordCloud(word='Python', count=100),
                WordCloud(word='Java', count=90),
                WordCloud(word='JavaScript', count=85)
            ]
            db.session.add_all(word_cloud_list)
            db.session.commit()
            print("✅ WordCloud测试数据插入完成")
        
        print("✅ 数据库初始化完成（所有表已创建，测试数据插入完毕）")

    return app

# ========== 调试启动入口 ==========
if __name__ == '__main__':
    app = create_app()
    # 启动服务器（0.0.0.0允许外部访问，debug=True方便开发调试）
    app.run(debug=True, host='0.0.0.0', port=5000)