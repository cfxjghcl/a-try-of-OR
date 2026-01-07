from flask import Blueprint, render_template, jsonify, send_from_directory, request
from datetime import datetime
import json

# 创建两个蓝图：一个用于主页面，一个用于API
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# ========== 主页面路由（main_bp）===========

@main_bp.route('/')
def index():
    """首页 - 显示可视化图表"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>计算机科学与技术就业可视化平台</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body { font-family: 'Arial', sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f7fa; }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
        .chart-box { background: white; border-radius: 10px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .chart { width: 100%; height: 400px; }
        .status { background: #e3f2fd; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .api-list { background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .api-list code { background: #eee; padding: 2px 5px; border-radius: 3px; }
        .nav { text-align: center; margin: 20px 0; }
        .nav a { margin: 0 10px; color: #3498db; text-decoration: none; }
        .nav a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>计算机科学与技术专业就业可视化平台</h1>
    
    <div class="nav">
        <a href=" ">首页</a > | 
        <a href="/api/test-connection">测试连接</a > | 
        <a href="/api/health">健康检查</a > | 
        <a href="/api/tech_heat">技术热度</a >
    </div>
    
    <div class="status">📊 正在加载数据...</div>
    
    <div class="api-list">
        <h3>可用API接口：</h3>
        <ul>
            <li><code>GET /api/employment-trend</code> - 就业趋势数据</li>  <!-- 修正拼写 -->
            <li><code>GET /api/salary-trend</code> - 薪资趋势数据</li>
            <li><code>GET /api/wordcloud</code> - 技术栈词云数据</li>      <!-- 修正拼写 -->
            <li><code>GET /api/tech_heat</code> - GitHub技术热度</li>
            <li><code>GET /api/test-connection</code> - 测试连接</li>
            <li><code>GET /api/health</code> - 健康检查</li>
        </ul>
    </div>
    
    <div class="chart-box">
        <h3>就业率趋势 (2020-2024)</h3>
        <div id="employmentChart" class="chart"></div>
    </div>
    
    <div class="chart-box">
        <h3>平均薪资趋势 (2020-2024)</h3>
        <div id="salaryChart" class="chart"></div>
    </div>
    
    <div class="chart-box">
        <h3>热门技术栈词云</h3>
        <div id="wordcloudChart" class="chart"></div>
    </div>
    
    <div class="chart-box">
        <h3>GitHub技术热度排行</h3>
        <div id="techHeatChart" class="chart"></div>
    </div>
    
    <script>
        const API_BASE = window.location.origin;
        
        console.log('当前API地址:', API_BASE);
        
        // 1. 获取就业数据 - 修正URL拼写
        fetch(API_BASE + '/api/employment-trend')  // 原来是 /api/emp/opment-trend
            .then(res => {
                console.log('就业API状态码:', res.status);
                if (!res.ok) {
                    throw new Error('就业API请求失败: ' + res.status);
                }
                return res.json();
            })
            .then(data => {
                console.log('就业数据:', data);
                const chart = echarts.init(document.getElementById('employmentChart'));
                chart.setOption({
                    title: { text: '就业率趋势 (%)' },
                    tooltip: { trigger: 'axis' },
                    xAxis: { type: 'category', data: data.years },
                    yAxis: { type: 'value', min: 80, max: 100, name: '就业率(%)' },
                    legend: { data: ['后端开发', '前端开发', '全栈开发', '数据科学', 'AI工程师'] },
                    series: [
                        { name: '后端开发', type: 'line', data: data.backend },
                        { name: '前端开发', type: 'line', data: data.frontend },
                        { name: '全栈开发', type: 'line', data: data.fullstack },
                        { name: '数据科学', type: 'line', data: data.data_science },
                        { name: 'AI工程师', type: 'line', data: data.ai_engineer }
                    ]
                });
                document.querySelector('.status').innerHTML = '✅ 就业数据加载完成';
            })
            .catch(error => {
                console.error('获取就业数据失败:', error);
                document.querySelector('.status').innerHTML = '❌ 就业数据加载失败: ' + error.message;
            });
        
        // 2. 获取薪资数据
        fetch(API_BASE + '/api/salary-trend')
            .then(res => {
                console.log('薪资API状态码:', res.status);
                if (!res.ok) {
                    throw new Error('薪资API请求失败: ' + res.status);
                }
                return res.json();
            })
            .then(data => {
                console.log('薪资数据:', data);
                const chart = echarts.init(document.getElementById('salaryChart'));
                chart.setOption({
                    title: { text: '平均月薪 (元)' },
                    tooltip: { trigger: 'axis' },
                    xAxis: { type: 'category', data: data.years },
                    yAxis: { type: 'value', name: '月薪(元)' },
                    legend: { data: ['后端开发', '前端开发', '全栈开发', '数据科学', 'AI工程师'] },
                    series: [
                        { name: '后端开发', type: 'bar', data: data.backend },
                        { name: '前端开发', type: 'bar', data: data.frontend },
                        { name: '全栈开发', type: 'bar', data: data.fullstack },
                        { name: '数据科学', type: 'bar', data: data.data_science },
                        { name: 'AI工程师', type: 'bar', data: data.ai_engineer }
                    ]
                });
                document.querySelector('.status').innerHTML += '<br>✅ 薪资数据加载完成';
            })
            .catch(error => {
                console.error('获取薪资数据失败:', error);
                document.querySelector('.status').innerHTML += '<br>❌ 薪资数据加载失败: ' + error.message;
            });
        
        // 3. 获取词云数据 - 修正URL拼写
        fetch(API_BASE + '/api/wordcloud')  // 原来是 /api/worldoud
            .then(res => {
                console.log('词云API状态码:', res.status);
                if (!res.ok) {
                    throw new Error('词云API请求失败: ' + res.status);
                }
                return res.json();
            })
            .then(data => {
                console.log('词云数据:', data);
                const chart = echarts.init(document.getElementById('wordcloudChart'));
                chart.setOption({
                    title: { text: '热门技术栈词云', left: 'center' },
                    tooltip: { show: true },
                    series: [{
                        type: 'wordCloud',
                        shape: 'circle',
                        sizeRange: [20, 80],
                        rotationRange: [-45, 45],
                        gridSize: 8,
                        drawOutOfBound: false,
                        textStyle: {
                            fontFamily: 'sans-serif',
                            fontWeight: 'bold',
                            color: function () {
                                return 'rgb(' + [
                                    Math.round(Math.random() * 160 + 50),
                                    Math.round(Math.random() * 160 + 50),
                                    Math.round(Math.random() * 160 + 50)
                                ].join(',') + ')';
                            }
                        },
                        data: data.data
                    }]
                });
                document.querySelector('.status').innerHTML += '<br>✅ 词云数据加载完成';
            })
            .catch(error => {
                console.error('获取词云数据失败:', error);
                document.querySelector('.status').innerHTML += '<br>❌ 词云数据加载失败: ' + error.message;
            });
        
        // 4. 获取GitHub技术热度数据
        fetch(API_BASE + '/api/tech_heat')
            .then(res => {
                console.log('技术热度API状态码:', res.status);
                if (!res.ok) {
                    throw new Error('技术热度API请求失败: ' + res.status);
                }
                return res.json();
            })
            .then(data => {
                console.log('技术热度数据:', data);
                const chart = echarts.init(document.getElementById('techHeatChart'));
                
                // 处理数据
                const skills = data.data.map(item => item.skill);
                const heats = data.data.map(item => item.heat);
                
                chart.setOption({
                    title: { text: 'GitHub技术热度排行', left: 'center' },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: { type: 'shadow' }
                    },
                    xAxis: {
                        type: 'category',
                        data: skills,
                        axisLabel: {
                            rotate: 45,
                            interval: 0
                        }
                    },
                    yAxis: {
                        type: 'value',
                        name: '热度'
                    },
                    series: [{
                        name: '热度',
                        type: 'bar',
                        data: heats,
                        itemStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: '#83bff6' },
                                { offset: 0.5, color: '#188df0' },
                                { offset: 1, color: '#188df0' }
                            ])
                        }
                    }]
                });
                document.querySelector('.status').innerHTML += '<br>✅ 技术热度数据加载完成';
            })
            .catch(error => {
                console.error('获取技术热度数据失败:', error);
                document.querySelector('.status').innerHTML += '<br>❌ 技术热度数据加载失败: ' + error.message;
            });
    </script>
</body>
</html>
'''

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
