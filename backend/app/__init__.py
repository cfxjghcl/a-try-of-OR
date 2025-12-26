from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    
    CORS(app, resources={"/api/": {"origins":"*"}})
    db.init_app(app)
    
    from app import routes
    app.register_blueprint(routes.bp)

    return app
