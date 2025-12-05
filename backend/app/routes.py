from flask import Blueprint, render_template, jsonify

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('base.html')

@bp.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Flask API is running!'})
