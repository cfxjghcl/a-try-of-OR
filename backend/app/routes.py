from flask import Blueprint, render_template, jsonify, send_from_directory, request
from datetime import datetime
import json

# 创建两个蓝图：一个用于主页面，一个用于API
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# ========== 主页面路由（main_bp）===========

@main_bp.route('/')

# ========== 处理旧的API请求（避免404错误）===========
@main_bp.route('/hybridaction/zybTrackerStatisticsAction')
def handle_old_api():
    """处理旧的API请求，避免404错误"""
    callback = request.args.get('__callback__', '')
    response_data = {
        "success": True,
        "data": [],
        "message": "此API已更新，请使用新API：/api/employment-trend, /api/salary-trend, /api/wordcloud"
    }
    
    if callback:
        # JSONP格式响应
        response = f"{callback}({json.dumps(response_data)})"
        return response, 200, {'Content-Type': 'application/javascript'}
    
    return jsonify(response_data)

@main_bp.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools():
    """处理Chrome开发工具请求"""
    return jsonify({"status": "ok"}), 200

@main_bp.route('/favicon.ico')
def favicon():
    """网站图标"""
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ========== API路由（api_bp）===========

@api_bp.route('/')
def api_index():
    """API首页"""
    return jsonify({
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
    return jsonify({
        'status': 'healthy',
        'message': 'Flask API is running!',
        'timestamp': datetime.now().isoformat()
    })

@api_bp.route('/test-connection')
def test_connection():
    """测试链接"""
    return jsonify({
        'message': '后端API连接成功！',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'connected'
    })

@api_bp.route('/hybridation/zybTrackerstatisticsAction', methods=['GET'])
def zyb_tracker_statistics():
    """业务接口（保留原接口）"""
    return jsonify({
        'message': 'zybTrackerstatisticsAction',
        'status': 'deprecated',
        'suggestion': '请使用新的API接口'
    })

# ========== 数据API接口 ==========

@api_bp.route('/employment-trend')
def get_employment_trend():
    """获取就业趋势数据"""
    data = {
        "years": [2020, 2021, 2022, 2023, 2024],
        "backend": [85.2, 86.5, 88.1, 87.8, 89.5],
        "frontend": [88.1, 89.3, 90.2, 89.7, 91.1],
        "fullstack": [82.4, 84.2, 86.3, 87.1, 89.0],
        "data_science": [90.5, 91.2, 92.3, 91.8, 93.1],
        "ai_engineer": [92.1, 93.4, 94.2, 93.8, 95.0]
    }
    return jsonify(data)

@api_bp.route('/salary-trend')
def get_salary_trend():
    """获取薪资趋势数据"""
    data = {
        "years": [2020, 2021, 2022, 2023, 2024],
        "backend": [15200, 16500, 18500, 19500, 21000],
        "frontend": [14500, 15800, 17500, 18800, 20000],
        "fullstack": [18500, 19500, 21500, 23000, 25000],
        "data_science": [20500, 22500, 25500, 28000, 31000],
        "ai_engineer": [22500, 25500, 28500, 32500, 36000]
    }
    return jsonify(data)

@api_bp.route('/wordcloud')
def get_wordcloud():
    """获取技术栈词云数据"""
    data = {
        "data": [
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
        "count": 20
    }
    return jsonify(data)

@api_bp.route('/employment_trends')
def get_employment_trends():
    """获取就业趋势数据（旧接口，兼容性）"""
    return jsonify({
        "years": [2018, 2019, 2020, 2021, 2022, 2023],
        "rate": [5.2, 4.8, 4.5, 4.3, 4.0, 3.8]
    })

@api_bp.route('/tech_heat')
def tech_heat():
    """获取GitHub技能热度数据"""
    try:
        # 数据库连接
        import pymysql

        connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='123456',
            database='jobviz',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            sql = "SELECT skill, heat, updated_at FROM tech_heat ORDER BY heat DESC"
            cursor.execute(sql)
            rows = cursor.fetchall()
        
        connection.close()
        
        return jsonify({
            'api': 'tech_heat',
            'version': '1.0',
            'data_source': 'GitHub OpenDigger',
            'record_count': len(rows),
            'data': rows,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as error:
        print(f"数据库链接失败，使用模拟数据：{error}")
        
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
        return jsonify({
            'api': 'tech_heat',
            'version': '1.0',
            'data_source': 'GitHub OpenDigger',
            'record_count': len(mock_data),
            'data': mock_data,
            'timestamp': datetime.now().isoformat(),
            'note': '使用模拟数据'
        })
#========= 职业相关API==========
@api_bp.route('/careers')
def get_careers():
    """获取所有职业信息"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='123456',
            database='jobviz',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            sql = "SELECT * FROM careers ORDER BY avg_entry_salary DESC"
            cursor.execute(sql)
            careers = cursor.fetchall()
        
        connection.close()
        
        return jsonify({
            'count': len(careers),
            'careers': careers,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"获取职业数据失败: {e}")
        # 返回模拟数据
        mock_careers = [
            {"id": 1, "name": "后端开发", "category": "开发", "avg_entry_salary": 15000},
            {"id": 2, "name": "前端开发", "category": "开发", "avg_entry_salary": 14000},
            {"id": 3, "name": "全栈开发", "category": "开发", "avg_entry_salary": 18000},
            {"id": 4, "name": "数据科学", "category": "数据", "avg_entry_salary": 20000},
            {"id": 5, "name": "AI工程师", "category": "人工智能", "avg_entry_salary": 25000},
            {"id": 6, "name": "运维工程师", "category": "运维", "avg_entry_salary": 16000},
            {"id": 7, "name": "测试开发", "category": "测试", "avg_entry_salary": 13000}
        ]
        return jsonify({
            'count': len(mock_careers),
            'careers': mock_careers,
            'note': '使用模拟数据'
        })

@api_bp.route('/career/<int:career_id>')
def get_career_detail(career_id):
    """获取特定职业详情"""
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='123456',
            database='jobviz',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # 获取职业基本信息
            sql = "SELECT * FROM careers WHERE id = %s"
            cursor.execute(sql, (career_id,))
            career = cursor.fetchone()
            
            if not career:
                return jsonify({'error': '职业不存在'}), 404
            
            # 这里可以添加获取该职业的趋势数据等
            
        connection.close()
        
        return jsonify({
            'career': career,
            'trend_data': {
                'years': [2020, 2021, 2022, 2023, 2024],
                'employment_rate': [85, 87, 89, 88, 90],
                'salary': [15000, 16500, 18500, 19500, 21000]
            }
        })
        
    except Exception as e:
        print(f"获取职业详情失败: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/update-wordcloud', methods=['POST', 'GET'])
def update_wordcloud():
    """手动更新词云数据"""
    try:
        # 导入词云生成函数
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from tasks.wordcloud_task import generate_wordcloud_data
        
        result = generate_wordcloud_data()
        
        return jsonify({
            'success': True,
            'message': f'词云数据已更新，共 {len(result["data"])} 个词条',
            'updated_at': result['updated_at'],
            'sample_data': result['data'][:5]  # 显示前5个词条作为示例
        })
        
    except Exception as e:
        print(f"更新词云失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '词云更新失败，请检查tasks模块'
        }), 500
