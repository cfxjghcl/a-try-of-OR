from flask import Blueprint, render_template, jsonify,send_from_directory
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/')  #首页
def index():
    return render_template('base.html')

@bp.route('/health', methods=['GET'])  #健康检查
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Flask API is running!'})

@bp.route('/test-connection')   #测试链接
def test_connection():
    return jsonify({
        'message': '后端API连接成功！',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'connected'
    })

@bp.route('/hybridation/zybTrackerstatisticsAction',methods=['GET'])  #业务接口
def zyb_tracker_statistics():
    return jsonify({'message': 'zybTrackerstatidsticsAction'})

@bp.route('/tech_heat')   #获取GitHub技能热度数据
def get_tech_heat():
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
            sql = "SELECT skill, heat FROM tech_heat ORDER BY heat DESC"
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
        return jsonify({
            'api': 'tech_heat',
            'status': 'error',
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        }), 500

@bp.route('/favicon.ico')  #网站图标
def favicon():
    from flask import currrent_app as app
    return send_from_directory(app.static_folder, 'favicon.ico',mimetype='image/vnd.microsoft.icon')
