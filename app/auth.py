# backend/app/auth.py
from functools import wraps
from flask import request, jsonify, g
from .models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        user = User.verify_token(token)
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        
        # 将用户信息存储到g对象中
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated

def get_current_user():
    """获取当前登录用户"""
    return getattr(g, 'current_user', None)