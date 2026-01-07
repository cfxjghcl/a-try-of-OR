from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['JSON_AS_ASCII'] = False  # 支持中文JSON
    app.config['JSON_SORT_KEYS'] = False  # 保持JSON顺序
    
    # 数据库配置
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@127.0.0.1:3306/jobviz?charset=utf8mb4'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    db.init_app(app)
    
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    with app.app_context():
        db.create_all()
    
    return app