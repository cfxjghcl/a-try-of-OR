# 1. 导入Flask核心组件
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 2. 初始化Flask应用实例（后端服务的核心对象）
app = Flask(__name__)

# 3. 配置数据库（SQLite文件数据库，无需启动服务，适合新手）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # 数据库文件路径
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭不必要的性能消耗

# 4. 初始化数据库对象（后续操作数据库都靠这个db）
db = SQLAlchemy(app)

# 5. 延迟导入+注册蓝图（解决循环导入问题）
if __name__ == '__main__':
    from routes import main_bp, api_bp  # 导入接口路由蓝图
    app.register_blueprint(main_bp)     # 注册主页面路由
    app.register_blueprint(api_bp)      # 注册API接口路由
    app.run(debug=True, port=5000)      # 启动服务（debug=True：代码修改后自动重启）