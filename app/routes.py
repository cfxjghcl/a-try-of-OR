from flask import Blueprint, render_template, jsonify, send_from_directory, request, g, current_app
from datetime import datetime
from flask_cors import cross_origin  # 替换全局CORS，避免重复配置
from app import db  # 仅保留db，app通过current_app获取
from app.models import User, Career, UserFavorite, EmploymentRate, SalaryTrend, Skill, TechHeat, EmploymentTrend, WordCloud
import pymysql
import json
import os
import sys

# ========== 补充缺失的认证装饰器（关键修复） ==========
def token_required(f):
    """Token验证装饰器（适配models.py的verify_token方法）"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 从请求头获取token
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace('Bearer ', '')
        if not token:
            return jsonify({"code":401,"msg":"Token is missing!"}), 401
        
        try:
            # 调用User模型的验证方法
            user = User.verify_token(token)
            if not user:
                return jsonify({"code":401,"msg":"Token is invalid!"}), 401
            g.current_user = user  # 存入g对象
        except Exception as e:
            return jsonify({"code":401,"msg":f"Token error: {str(e)}"}), 401
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    """获取当前登录用户"""
    return getattr(g, 'current_user', None)

# ========== 蓝图初始化（优化命名和前缀） ==========
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# ========== 统一响应函数（保留核心逻辑） ==========
def api_response(code=200, msg="success", data=None):
    return jsonify({
        "code": code,
        "msg": msg,
        "data": data if data is not None else {}
    })

# ========== 主页面路由 ==========
@main_bp.route('/')
def index():
    """后端首页 - 重定向到前端页面"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>就业可视化平台 - 后端API</title>
        <style>
            body { font-family: Arial; padding: 40px; text-align: center; }
            .box { max-width: 800px; margin: 0 auto; padding: 30px; background: #f5f7fa; border-radius: 10px; }
            a { color: #3498db; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>📊 计算机科学与技术就业可视化平台</h1>
            <p>后端API服务运行正常！</p >
            <p>请访问前端页面查看可视化图表：</p >
            <p><a href="/view" target="_blank">👉 点击这里打开前端页面</a ></p >
            <hr>
            <h3>API接口列表：</h3>
            <ul style="text-align: left; display: inline-block;">
                <li><a href="/api/employment-trend" target="_blank">/api/employment-trend</a > - 就业趋势</li>
                <li><a href="/api/salary-trend" target="_blank">/api/salary-trend</a > - 薪资趋势</li>
                <li><a href="/api/wordcloud" target="_blank">/api/wordcloud</a > - 技术词云</li>
                <li><a href="/api/tech_heat" target="_blank">/api/tech_heat</a > - GitHub技术热度</li>
                <li><a href="/api/careers" target="_blank">/api/careers</a > - 职业列表</li>
                <li><a href="/api/health" target="_blank">/api/health</a > - 健康检查</li>
            </ul>
        </div>
    </body>
    </html>
    '''

@main_bp.route('/view')
def view_frontend():
    """直接访问前端页面（优化路径逻辑）"""
    # 定义前端目录（项目根目录下的frontend文件夹）
    frontend_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'frontend'
    )
    frontend_dir = os.path.normpath(frontend_dir)
    index_path = os.path.join(frontend_dir, 'index.html')
    
    if os.path.exists(index_path):
        return send_from_directory(frontend_dir, 'index.html')
    return "前端页面未找到，请在项目根目录创建frontend文件夹并放入index.html", 404

@main_bp.route('/hybridaction/zybTrackerStatisticsAction')
def handle_old_api():
    """兼容旧API请求"""
    callback = request.args.get('__callback__', '')
    response_data = {
        "success": True,
        "data": [],
        "message": "此API已更新，请使用新API：/api/employment-trend, /api/salary-trend, /api/wordcloud"
    }
    
    if callback:
        return f"{callback}({json.dumps(response_data)})", 200, {'Content-Type': 'application/javascript'}
    return jsonify(response_data)

@main_bp.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools():
    return jsonify({"status": "ok"}), 200

@main_bp.route('/favicon.ico')
def favicon():
    """网站图标（返回空响应避免404）"""
    return '', 204

# ========== API基础接口 ==========
@api_bp.route('/')
def api_index():
    """API首页"""
    return api_response(data={
        'message': 'Flask API运行正常',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': [
            '/api/health',
            '/api/test-connection',
            '/api/employment-trend',
            '/api/salary-trend',
            '/api/wordcloud',
            '/api/tech_heat'
        ]
    })

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return api_response(data={
        'status': 'healthy',
        'message': 'Flask API is running!',
        'timestamp': datetime.now().isoformat()
    })

@api_bp.route('/test-connection')
def test_connection():
    """测试前后端连接"""
    return api_response(data={
        'message': '后端API连接成功！',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'connected'
    })

@api_bp.route('/hybridation/zybTrackerstatisticsAction', methods=['GET'])
def zyb_tracker_statistics():
    """兼容旧业务接口"""
    return api_response(
        code=200,
        msg="此接口已废弃",
        data={
            'message': 'zybTrackerstatisticsAction',
            'status': 'deprecated',
            'suggestion': '请使用新的API接口'
        }
    )

# ========== 数据可视化API ==========
@api_bp.route('/employment-trend')
def get_employment_trend_route():
    """获取就业趋势数据（返回结构化数据）"""
    data = {
        "years": [2020, 2021, 2022, 2023, 2024],
        "backend": [85.2, 86.5, 88.1, 87.8, 89.5],
        "frontend": [88.1, 89.3, 90.2, 89.7, 91.1],
        "fullstack": [82.4, 84.2, 86.3, 87.1, 89.0],
        "data_science": [90.5, 91.2, 92.3, 91.8, 93.1],
        "ai_engineer": [92.1, 93.4, 94.2, 93.8, 95.0]
    }
    return api_response(data=data)

@api_bp.route('/salary-trend')
def get_salary_trend_route():
    """获取薪资趋势数据"""
    data = {
        "years": [2020, 2021, 2022, 2023, 2024],
        "backend": [15200, 16500, 18500, 19500, 21000],
        "frontend": [14500, 15800, 17500, 18800, 20000],
        "fullstack": [18500, 19500, 21500, 23000, 25000],
        "data_science": [20500, 22500, 25500, 28000, 31000],
        "ai_engineer": [22500, 25500, 28500, 32500, 36000]
    }
    return api_response(data=data)

@api_bp.route('/wordcloud')
def get_wordcloud():
    """获取技术栈词云数据（优先从数据库读取）"""
    try:
        # 从数据库读取词云数据
        wordcloud_data = WordCloud.query.all()
        db_data = [{"name": item.word, "value": item.count} for item in wordcloud_data]
        
        return api_response(data={
            "data": db_data if db_data else [
                {"name": "Python", "value": 100},
                {"name": "Java", "value": 85},
                {"name": "JavaScript", "value": 95},
                {"name": "Vue.js", "value": 75},
                {"name": "React", "value": 80},
                {"name": "MySQL", "value": 90},
                {"name": "Redis", "value": 70},
                {"name": "Docker", "value": 65},
                {"name": "Kubernetes", "value": 55},
                {"name": "AWS", "value": 60},
                {"name": "微服务", "value": 75},
                {"name": "Spring Boot", "value": 85},
                {"name": "Flask", "value": 70},
                {"name": "FastAPI", "value": 60},
                {"name": "Git", "value": 95},
                {"name": "Linux", "value": 80},
                {"name": "TypeScript", "value": 75},
                {"name": "MongoDB", "value": 65},
                {"name": "PostgreSQL", "value": 70},
                {"name": "Elasticsearch", "value": 55}
            ],
            "updated_at": datetime.now().isoformat(),
            "count": len(db_data) if db_data else 20
        })
    except Exception as e:
        current_app.logger.error(f"读取词云数据失败: {e}")
        # 返回模拟数据
        mock_data = [
            {"name": "Python", "value": 100},
            {"name": "Java", "value": 85},
            {"name": "JavaScript", "value": 95},
            {"name": "Vue.js", "value": 75},
            {"name": "React", "value": 80},
            {"name": "MySQL", "value": 90},
            {"name": "Redis", "value": 70},
            {"name": "Docker", "value": 65},
            {"name": "Kubernetes", "value": 55},
            {"name": "AWS", "value": 60},
            {"name": "微服务", "value": 75},
            {"name": "Spring Boot", "value": 85},
            {"name": "Flask", "value": 70},
            {"name": "FastAPI", "value": 60},
            {"name": "Git", "value": 95},
            {"name": "Linux", "value": 80},
            {"name": "TypeScript", "value": 75},
            {"name": "MongoDB", "value": 65},
            {"name": "PostgreSQL", "value": 70},
            {"name": "Elasticsearch", "value": 55}
        ]
        return api_response(data={
            "data": mock_data,
            "updated_at": datetime.now().isoformat(),
            "count": 20,
            "note": "使用模拟数据"
        })

@api_bp.route('/employment_trends')
def get_employment_trends():
    """兼容旧就业趋势接口"""
    return api_response(data={
        "years": [2018, 2019, 2020, 2021, 2022, 2023],
        "rate": [5.2, 4.8, 4.5, 4.3, 4.0, 3.8]
    })

@api_bp.route('/tech_heat')
def tech_heat():
    """获取GitHub技能热度数据（优先读取SQLite数据库）"""
    try:
        # 优先从SQLite读取TechHeat数据
        tech_heat_data = TechHeat.query.order_by(TechHeat.heat.desc()).all()
        db_data = [{"skill": item.skill, "heat": item.heat, "updated_at": item.created_at.isoformat() if hasattr(item, 'created_at') else datetime.now().isoformat()} for item in tech_heat_data]
        
        return api_response(data={
            'api': 'tech_heat',
            'version': '1.0',
            'data_source': 'GitHub OpenDigger',
            'record_count': len(db_data),
            'data': db_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"读取技术热度数据失败，使用模拟数据：{e}")
        # 模拟数据（兼容原逻辑）
        mock_data = [
            {"skill": "Python", "heat": 95, "updated_at": "2024-01-01 10:00:00"},
            {"skill": "JavaScript", "heat": 88, "updated_at": "2024-01-01 10:00:00"},
            {"skill": "Java", "heat": 76, "updated_at": "2024-01-01 10:00:00"},
            {"skill": "C++", "heat": 65, "updated_at": "2024-01-01 10:00:00"},
            {"skill": "Go", "heat": 50, "updated_at": "2024-01-01 10:00:00"},
            {"skill": "TypeScript", "heat": 85, "updated_at": "2024-01-01 10:00:00"},
            {"skill": "Rust", "heat": 45, "updated_at": "2024-01-01 10:00:00"},
            {"skill": "Kotlin", "heat": 40, "updated_at": "2024-01-01 10:00:00"}
        ]
        return api_response(data={
            'api': 'tech_heat',
            'version': '1.0',
            'data_source': 'GitHub OpenDigger',
            'record_count': len(mock_data),
            'data': mock_data,
            'timestamp': datetime.now().isoformat(),
            'note': '使用模拟数据'
        })

# ========== 职业相关API ==========
@api_bp.route('/careers')
def get_careers():
    """获取所有职业信息（优先从SQLite读取）"""
    try:
        careers = Career.query.order_by(Career.avg_entry_salary.desc()).all()
        db_data = [
            {
                "id": career.id,
                "name": career.name,
                "category": career.category,
                "avg_entry_salary": career.avg_entry_salary,
                "demand_level": career.demand_level,
                "description": career.description[:100] + '...' if career.description else ''
            } for career in careers
        ]
        
        return api_response(data={
            'count': len(db_data),
            'careers': db_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"获取职业数据失败: {e}")
        # 模拟数据
        mock_careers = [
            {"id": 1, "name": "后端开发", "category": "开发", "avg_entry_salary": 15000},
            {"id": 2, "name": "前端开发", "category": "开发", "avg_entry_salary": 14000},
            {"id": 3, "name": "全栈开发", "category": "开发", "avg_entry_salary": 18000},
            {"id": 4, "name": "数据科学", "category": "数据", "avg_entry_salary": 20000},
            {"id": 5, "name": "AI工程师", "category": "人工智能", "avg_entry_salary": 25000},
            {"id": 6, "name": "运维工程师", "category": "运维", "avg_entry_salary": 16000},
            {"id": 7, "name": "测试开发", "category": "测试", "avg_entry_salary": 13000}
        ]
        return api_response(data={
            'count': len(mock_careers),
            'careers': mock_careers,
            'note': '使用模拟数据'
        })

@api_bp.route('/career/<int:career_id>')
def get_career_detail(career_id):
    """获取特定职业详情"""
    try:
        career = Career.query.get(career_id)
        if not career:
            return api_response(code=404, msg="职业不存在")
        
        # 获取职业关联的技能
        skills = Skill.query.filter_by(career_id=career_id).all()
        skill_list = [{"name": s.skill_name, "importance": s.importance_level} for s in skills]
        
        return api_response(data={
            'career': {
                'id': career.id,
                'name': career.name,
                'category': career.category,
                'description': career.description,
                'avg_entry_salary': career.avg_entry_salary,
                'demand_level': career.demand_level,
                'in_demand': career.in_demand
            },
            'skills': skill_list,
            'trend_data': {
                'years': [2020, 2021, 2022, 2023, 2024],
                'employment_rate': [85, 87, 89, 88, 90],
                'salary': [15000, 16500, 18500, 19500, 21000]
            }
        })
    except Exception as e:
        current_app.logger.error(f"获取职业详情失败: {e}")
        return api_response(code=500, msg="获取职业详情失败", data={'error': str(e)})

@api_bp.route('/update-wordcloud', methods=['POST', 'GET'])
def update_wordcloud():
    """手动更新词云数据（兼容无tasks模块的情况）"""
    try:
        # 模拟词云数据更新
        mock_result = {
            'data': [{"name": "Python", "value": 100}, {"name": "Java", "value": 85}, {"name": "JavaScript", "value": 95}],
            'updated_at': datetime.now().isoformat()
        }
        return api_response(data={
            'success': True,
            'message': f'词云数据已更新，共 {len(mock_result["data"])} 个词条',
            'updated_at': mock_result['updated_at'],
            'sample_data': mock_result['data'][:5]
        })
    except Exception as e:
        current_app.logger.error(f"更新词云失败: {e}")
        return api_response(code=500, msg="词云更新失败（无tasks模块）", data={
            'success': False,
            'error': str(e),
            'message': '已使用模拟数据更新，如需真实更新请创建tasks/wordcloud_task.py'
        })

# ========== 用户认证API ==========
@api_bp.route('/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json(silent=True) or {}
    # 验证必填字段
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return api_response(code=400, msg=f'缺少必填字段: {field}')
    
    # 检查用户名/邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return api_response(code=400, msg='用户名已存在')
    if User.query.filter_by(email=data['email']).first():
        return api_response(code=400, msg='邮箱已存在')
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        major=data.get('major', ''), 
        target_career=data.get('target_career', '')  
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        token = user.generate_token()
        
        return api_response(code=201, msg="用户注册成功", data={
            'user': user.to_dict(),
            'token': token,
            'expires_in': 86400
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"用户注册失败: {e}")
        return api_response(code=500, msg="注册失败", data={'error': str(e)})

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json(silent=True) or {}
    
    # 验证参数
    if 'username' not in data or 'password' not in data:
        return api_response(code=400, msg='用户名或密码不能为空')
    
    # 支持用户名/邮箱登录
    user = User.query.filter(
        (User.username == data['username']) | (User.email == data['username'])
    ).first()
    
    if not user:
        return api_response(code=404, msg='该用户不存在')
    if not user.check_password(data['password']):
        return api_response(code=401, msg='密码或用户名错误')
    
    token = user.generate_token()
    return api_response(data={
        'message': '登录成功',
        'user': user.to_dict(),
        'token': token,
        'expires_in': 86400
    })

@api_bp.route('/auth/profile', methods=['GET'])
@token_required
def get_profile():
    """获取用户个人资料"""
    user = get_current_user()
    return api_response(data={'user': user.to_dict()})

@api_bp.route('/auth/profile', methods=['PUT'])
@token_required
def update_profile():
    """更新用户个人资料"""
    user = get_current_user()
    data = request.json or {}
    
    allowed_fields = ['email', 'major', 'target_career']
    for field in allowed_fields:
        if field in data and data[field]:
            setattr(user, field, data[field])
    
    # 更新密码
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    user.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return api_response(data={
            'message': '资料更新成功',
            'user': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新用户资料失败: {e}")
        return api_response(code=500, msg="更新失败", data={'error': str(e)})

@api_bp.route('/auth/validate', methods=['GET'])
@token_required
def validate_token():
    """验证token是否有效"""
    user = get_current_user()
    return api_response(data={
        'valid': True,
        'user': user.to_dict()
    })

# ========== 个性化推荐API ==========
@api_bp.route('/recommend/careers', methods=['GET'])
@token_required
def recommend_careers():
    """基于用户信息推荐职业"""
    user = get_current_user()
    careers = []
    
    if not user.major and not user.target_career:
        careers = Career.query.order_by(Career.avg_entry_salary.desc()).limit(5).all()
    else:
        if user.target_career:
            target_career = Career.query.filter(
                Career.name.ilike(f"%{user.target_career}%")
            ).first()
            if target_career:
                # 推荐同类别/相似薪资职业
                careers = Career.query.filter(
                    (Career.category == target_career.category) |
                    (Career.avg_entry_salary.between(
                        target_career.avg_entry_salary * 0.8,
                        target_career.avg_entry_salary * 1.2
                    ))
                ).limit(5).all()
            else:
                careers = Career.query.order_by(Career.avg_entry_salary.desc()).limit(5).all()
        else:
            careers = Career.query.order_by(Career.avg_entry_salary.desc()).limit(5).all()
    
    return api_response(data={
        'recommendations': [
            {
                'id': career.id,
                'name': career.name,
                'category': career.category,
                'description': career.description[:100] + '...' if career.description else '',
                'avg_entry_salary': career.avg_entry_salary,
                'demand_level': career.demand_level,
                'match_reason': '根据您的专业和目标职业推荐'
            }
            for career in careers
        ]
    })

@api_bp.route('/recommend/learning-path', methods=['GET'])
@token_required
def learning_path_recommendation():
    """推荐学习路径"""
    user = get_current_user()
    learning_paths = {
        '后端开发': {
            'title': '后端开发工程师学习路径',
            'steps': [
                '1. 学习Python/Java基础语法',
                '2. 掌握数据库设计（MySQL, Redis）',
                '3. 学习Web框架（Django/Spring Boot）',
                '4. 掌握Linux和服务器部署',
                '5. 学习微服务和分布式系统',
                '6. 项目实战：电商系统/社交平台'
            ],
            'duration': '6-12个月',
            'resources': ['慕课网', '极客时间', '官方文档']
        },
        '前端开发': {
            'title': '前端开发工程师学习路径',
            'steps': [
                '1. 学习HTML/CSS/JavaScript基础',
                '2. 掌握Vue.js或React框架',
                '3. 学习TypeScript和ES6+',
                '4. 掌握Webpack/Vite等构建工具',
                '5. 学习移动端开发和响应式设计',
                '6. 项目实战：管理系统/移动应用'
            ],
            'duration': '4-8个月',
            'resources': ['MDN文档', 'Vue官方文档', 'React官方文档']
        },
        '数据科学': {
            'title': '数据科学工程师学习路径',
            'steps': [
                '1. 学习Python基础（NumPy/Pandas）',
                '2. 掌握数据清洗和可视化',
                '3. 学习机器学习算法',
                '4. 掌握SQL和大数据工具',
                '5. 学习深度学习框架（TensorFlow/PyTorch）',
                '6. 项目实战：数据分析/推荐系统'
            ],
            'duration': '8-12个月',
            'resources': ['Kaggle', 'Coursera', '李沐动手学深度学习']
        },
        'AI工程师': {
            'title': 'AI工程师学习路径',
            'steps': [
                '1. 数学基础（线性代数/概率论）',
                '2. Python和深度学习框架',
                '3. 计算机视觉/NLP基础',
                '4. 模型训练和部署',
                '5. 大模型应用开发',
                '6. 项目实战：AI助手/图像识别'
            ],
            'duration': '10-18个月',
            'resources': ['OpenAI文档', 'HuggingFace', '斯坦福CS231n']
        }
    }
    
    target = user.target_career or '后端开发'
    # 匹配最接近的职业路径
    matched_path = None
    for career_name, path in learning_paths.items():
        if career_name in target or target in career_name:
            matched_path = path
            break
    if not matched_path:
        matched_path = learning_paths['后端开发']
    
    return api_response(data={
        'target_career': target,
        'learning_path': matched_path
    })

# ========== 收藏功能API ==========
@api_bp.route('/favorites/careers', methods=['GET'])
@token_required
def get_favorite_careers():
    """获取用户收藏的职业"""
    user = get_current_user()    
    favorites = user.favorites.all()  # 修复：添加.all()获取列表
    
    return api_response(data={
        'favorites': [
            {
                'id': career.id,
                'name': career.name,
                'category': career.category,
                'avg_entry_salary': career.avg_entry_salary
            }
            for career in favorites
        ],
        'count': len(favorites)
    })

@api_bp.route('/favorites/careers/<int:career_id>', methods=['POST'])
@token_required
def add_favorite_career(career_id):
    """添加职业到收藏"""
    user = get_current_user()
    career = Career.query.get(career_id)
    
    if not career:
        return api_response(code=404, msg='职业不存在')
    # 检查是否已收藏
    existing = UserFavorite.query.filter_by(
        user_id=user.id, 
        career_id=career_id
    ).first()
    if existing:
        return api_response(code=400, msg='已收藏该职业')
    
    favorite = UserFavorite(user_id=user.id, career_id=career_id)
    try:
        db.session.add(favorite)
        db.session.commit()
        return api_response(code=201, msg='收藏成功')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"添加收藏失败: {e}")
        return api_response(code=500, msg='添加失败', data={'error': str(e)})

@api_bp.route('/favorites/careers/<int:career_id>', methods=['DELETE'])
@token_required
def remove_favorite_career(career_id):
    """移除收藏的职业"""
    user = get_current_user()
    favorite = UserFavorite.query.filter_by(
        user_id=user.id, 
        career_id=career_id
    ).first()
    
    if not favorite:
        return api_response(code=404, msg='未收藏该职业')
    
    try:
        db.session.delete(favorite)
        db.session.commit()
        return api_response(msg='取消收藏成功')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"移除收藏失败: {e}")
        return api_response(code=500, msg='移除失败', data={'error': str(e)})

# ========== 搜索功能API ==========
def get_employment_trend(career_id, year):
    """获取职业就业率趋势"""
    try:
        trend = EmploymentRate.query.filter_by(career_id=career_id, year=int(year)).first()
        return trend.employment_rate if trend else None
    except Exception as e:
        current_app.logger.error(f"获取就业趋势失败：{e}")
        return None

def get_salary_trend(career_id, year):
    """获取薪资趋势"""
    try:
        trend = SalaryTrend.query.filter_by(career_id=career_id, year=int(year)).first()
        if trend:
            return {
                'avg': trend.avg_salary, 
                'min': trend.min_salary,
                'max': trend.max_salary
            } 
        return None
    except Exception as e:
        current_app.logger.error(f"获取薪资趋势失败：{e}")
        return None

def calculate_hot_index(career_id):
    """计算职业热度指数"""
    try:
        career = Career.query.get(career_id)
        if not career:
            return 50
        
        base_score = 50
        if getattr(career, 'in_demand', False):
            base_score += 20
        if career.avg_entry_salary > 20000:
            base_score += 15
        elif career.avg_entry_salary > 15000:
            base_score += 10
        elif career.avg_entry_salary > 10000:
            base_score += 5
        
        return min(max(base_score, 0), 100)
    except Exception as e:
        current_app.logger.error(f"计算热度指数失败: {e}")
        return 50

@api_bp.route('/search/careers', methods=['GET'])
def search_careers():
    """高级职业搜索"""
    keyword = request.args.get('q', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    sort_by = request.args.get('sort_by', 'salary') 
    order = request.args.get('order', 'desc') 
    category = request.args.get('category', None)
    min_salary = request.args.get('min_salary', None)
    max_salary = request.args.get('max_salary', None)
    year = request.args.get('year', None)

    # 边界值校验
    page = max(1, page)
    per_page = max(1, min(per_page, 100))

    try:
        query = Career.query
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                Career.name.ilike(f"%{keyword}%") | 
                (Career.description.ilike(f"%{keyword}%") if Career.description else False)
            )
        
        # 分类筛选
        if category:
            query = query.filter(Career.category == category)
        
        # 薪资筛选
        if min_salary:
            try:
                min_salary_int = int(min_salary)
                query = query.filter(Career.avg_entry_salary >= min_salary_int)
            except ValueError:
                return api_response(code=400, msg='最低薪资格式错误（需为数字）')
        
        if max_salary:
            try:
                max_salary_int = int(max_salary)
                query = query.filter(Career.avg_entry_salary <= max_salary_int)
            except ValueError:
                return api_response(code=400, msg='最高薪资格式错误（需为数字）')
        
        # 年份筛选
        if year:
            try:
                year_int = int(year)
                if year_int < 2020 or year_int > 2026:
                    return api_response(code=400, msg='年份必须在2020-2026之间')
                subquery = db.session.query(EmploymentRate.career_id).filter(
                    EmploymentRate.year == year_int
                ).distinct().subquery()
                query = query.filter(Career.id.in_(subquery))
            except ValueError:
                return api_response(code=400, msg='年份格式错误（需为数字）')
            except Exception as e:
                current_app.logger.error(f"年份筛选异常: {e}")
                return api_response(code=500, msg='年份筛选异常')
        
        # 排序处理
        order_column = Career.avg_entry_salary
        if sort_by == 'name':
            order_column = Career.name

        if order == 'asc':
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())

        # 分页处理
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        careers = pagination.items 
   
        # 构建响应信息
        message_parts = []
        if keyword:
            message_parts.append(f"关键词：{keyword}")
        if category:
            message_parts.append(f"类别:{category}")
        if year:
            message_parts.append(f"年份:{year}")
        if min_salary or max_salary:
            salary_range = []
            if min_salary:
                salary_range.append(f"最低:{min_salary}") 
            if max_salary:
                salary_range.append(f"最高:{max_salary}") 
            message_parts.append(f"薪资：{' | '.join(salary_range)}")
        
        message = '搜索成功' if not message_parts else ' | '.join(message_parts)

        # 构建返回数据
        result_data = []
        for career in careers:
            career_info = {
                'id': career.id,
                'name': career.name,
                'category': career.category,
                'avg_entry_salary': career.avg_entry_salary,
                'employment_trend': get_employment_trend(career.id, year) if year else None,
                'salary_trend': get_salary_trend(career.id, year) if year else None,
                'hot_index': calculate_hot_index(career.id),
                'skills_required': getattr(career, 'skills_required', ''),
                'in_demand': getattr(career, 'in_demand', False),
                'description': career.description[:100] + '...' if (career.description and len(career.description) > 100) else career.description or ''
            }
            result_data.append(career_info)

        return api_response(data={
            'message': message,
            'result': result_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'total_pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters': {
                'keyword': keyword,
                'category': category,
                'min_salary': min_salary,
                'max_salary': max_salary,
                'year': year,
                'sort_by': sort_by,
                'order': order
            }
        })
    except Exception as e:
        current_app.logger.error(f"搜索失败：{str(e)}")
        return api_response(code=500, msg="搜索失败", data={'error': str(e)})

@api_bp.route('/search/careers/simple', methods=['GET'])
def simple_search_careers():
    """简易职业搜索接口"""
    query = request.args.get('q', '').strip()
    limit = int(request.args.get('limit', 10))
    limit = max(1, min(limit, 50))

    careers = Career.query.filter(Career.name.ilike(f"%{query}%")).limit(limit).all()
    
    return api_response(data={
        'results': [
            {
                'id': career.id,
                'name': career.name,
                'category': career.category,
                'avg_entry_salary': career.avg_entry_salary
            }
            for career in careers
        ],
        'count': len(careers)
    })