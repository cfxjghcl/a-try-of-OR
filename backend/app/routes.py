from flask import Blueprint, render_template, jsonify
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/')
def index():
    return render_template('base.html')

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Flask API is running!'})

@bp.route('/test-connection')
def test_connection():
    return jsonify({
        'message': '后端API连接成功！',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'connected'
    })