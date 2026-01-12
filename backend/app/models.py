from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import time
import os
from flask import current_app

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    major = db.Column(db.String(100))  # 专业
    target_career = db.Column(db.String(100))  # 目标职业
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 用户收藏的职业关系
    favorites = db.relationship('Career', secondary='user_favorites', backref='favorited_by')
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self, expires_in=86400):  # 24小时
        """生成JWT token"""
        try:
            import jwt as pyjwt
        except ImportError:
            raise ImportError("PyJwt库未安装，请安装它以使用JWT功能。")
        payload = {
            'user_id': self.id,
            'username': self.username,
            'exp': datetime.utcnow().timestamp() + expires_in
        }
        token_bytes = pyjwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        if isinstance(token_bytes, bytes):
            return token_bytes.decode('utf-8')
        return token_bytes
    
    @staticmethod
    def verify_token(token):
        try:
            import jwt as pyjwt
        except ImportError:
            raise ImportError("PyJwt库未安装，请安装它以使用JWT功能。")
        try:
            payload = pyjwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('user_id')
            if not user_id:
                return None
            return User.query.get(user_id)
        except pyjwt.ExpiredSignatureError:
            return None
    
    def to_dict(self):
        """转换为字典（不包含敏感信息）"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'major': self.major,
            'target_career': self.target_career,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 用户收藏关联表
class UserFavorite(db.Model):
    __tablename__ = 'user_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    career_id = db.Column(db.Integer, db.ForeignKey('careers.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 职业模型
class Career(db.Model):
    __tablename__ = 'careers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    required_skills = db.Column(db.Text)
    avg_entry_salary = db.Column(db.Integer)
    demand_level = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    favorite_by = db.relationship('User', secondary='user_favorites', backref='favorite_careers')

#就业趋势表
class EmploymentRate(db.Model):
    __tablename__ = 'employment_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey('careers.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    quarter = db.Column(db.Integer)
    employment_rate = db.Column(db.Float)  # 百分比值
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    career = db.relationship('Career', backref=db.backref('employment_trends', lazy=True))

#薪资趋势表
class SalaryTrend(db.Model):
    __tablename__ = 'salary_trends'
    
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey('careers.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    avg_salary = db.Column(db.Float)
    min_salary = db.Column(db.Float)
    max_salary = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    career = db.relationship('Career', backref=db.backref('salary_trends', lazy=True))

#技能要求表
class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey('careers.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    importance_level = db.Column(db.Integer, default=3)  
    is_required = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    career = db.relationship('Career', backref=db.backref('skills', lazy=True))