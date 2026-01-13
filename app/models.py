# app/models.py 完整代码（添加缺失模型）
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask import current_app

# 提前导入JWT
try:
    import jwt
except ImportError:
    jwt = None

# User模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    major = db.Column(db.String(100))
    target_career = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    favorites = db.relationship(
        'Career', 
        secondary='user_favorites', 
        backref=db.backref('favorited_by', lazy='dynamic'),
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self, expires_in=86400):
        if jwt is None:
            raise ImportError("PyJwt库未安装，请执行 `pip install pyjwt` 安装")
        expire_time = datetime.utcnow() + timedelta(seconds=expires_in)
        payload = {
            'user_id': self.id,
            'username': self.username,
            'exp': expire_time
        }
        try:
            token = jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY', 'default-secret-key'),
                algorithm='HS256'
            )
            return token.decode('utf-8') if isinstance(token, bytes) else token
        except Exception as e:
            raise RuntimeError(f"生成Token失败: {str(e)}")
    
    @staticmethod
    def verify_token(token):
        if jwt is None:
            raise ImportError("PyJwt库未安装，请执行 `pip install pyjwt` 安装")
        try:
            payload = jwt.decode(
                token,
                current_app.config.get('SECRET_KEY', 'default-secret-key'),
                algorithms=['HS256']
            )
            user_id = payload.get('user_id')
            return User.query.get(user_id) if user_id else None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def to_dict(self):
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    career_id = db.Column(db.Integer, db.ForeignKey('careers.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'career_id', name='_user_career_uc'),)

# 职业模型
class Career(db.Model):
    __tablename__ = 'careers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), index=True)
    description = db.Column(db.Text)
    required_skills = db.Column(db.Text)
    skills_required = db.Column(db.Text)
    avg_entry_salary = db.Column(db.Integer, index=True)
    demand_level = db.Column(db.String(20))
    in_demand = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ========== 补充缺失模型（关键修复） ==========
# 技术热度模型
class TechHeat(db.Model):
    __tablename__ = 'tech_heat'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    skill = db.Column(db.String(50), nullable=False)
    heat = db.Column(db.Integer, nullable=False)

# 就业趋势模型
class EmploymentTrend(db.Model):
    __tablename__ = 'employment_trend'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.Integer, nullable=False)
    profession = db.Column(db.String(50), nullable=False)
    number = db.Column(db.Integer, nullable=False)

# 薪资趋势模型
# app/models.py 中 SalaryTrend 模型的正确定义
class SalaryTrend(db.Model):
    __tablename__ = 'salary_trends'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 必须添加 career_id 字段（关联 Career 表）
    career_id = db.Column(db.Integer, db.ForeignKey('careers.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    avg_salary = db.Column(db.Float, nullable=False)
    min_salary = db.Column(db.Float, nullable=False)
    max_salary = db.Column(db.Float, nullable=False)
    # 可选：添加与 Career 表的关联关系
    career = db.relationship('Career', backref=db.backref('salary_trends', lazy=True))

# 词云数据模型
class WordCloud(db.Model):
    __tablename__ = 'word_cloud'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, nullable=False)

# 就业趋势表
class EmploymentRate(db.Model):
    __tablename__ = 'employment_rates'
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey('careers.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    quarter = db.Column(db.Integer)
    employment_rate = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    career = db.relationship('Career', backref=db.backref('employment_trends', lazy=True))
    __table_args__ = (db.UniqueConstraint('career_id', 'year', 'quarter', name='_career_year_quarter_uc'),)

# 薪资趋势表
#class SalaryTrend(db.Model):
   # __tablename__ = 'salary_trends'
    #id = db.Column(db.Integer, primary_key=True)
    #career_id = db.Column(db.Integer, db.ForeignKey('careers.id'), nullable=False, index=True)
    #year = db.Column(db.Integer, nullable=False, index=True)
    #avg_salary = db.Column(db.Float)
    #min_salary = db.Column(db.Float)
    #max_salary = db.Column(db.Float)
    #created_at = db.Column(db.DateTime, default=datetime.utcnow)
    #updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    #career = db.relationship('Career', backref=db.backref('salary_trends', lazy=True))
    #__table_args__ = (db.UniqueConstraint('career_id', 'year', name='_career_year_uc'),)

# 技能要求表
class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey('careers.id'), nullable=False, index=True)
    skill_name = db.Column(db.String(100), nullable=False, index=True)
    importance_level = db.Column(db.Integer, default=3)
    is_required = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    career = db.relationship('Career', backref=db.backref('skills', lazy=True))
    __table_args__ = (db.UniqueConstraint('career_id', 'skill_name', name='_career_skill_uc'),)