#配置文件创建脚本
#!/usr/bin/env python3
"""
创建部署配置文件
位置: scripts/deployment/create_configs.py
"""

import os
import json
import configparser
from pathlib import Path

def create_nginx_config():
    """创建 Nginx 配置文件（如果部署到 Linux）"""
    config = """
# OR 项目 Nginx 配置
server {
    listen 80;
    server_name your-domain.com;  # 修改为你的域名
    
    # 前端静态文件
    location / {
        root /var/www/or-app/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 30d;
    }
    
    # 后端 API 代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 安全头部
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
"""
    
    with open("nginx-or.conf", "w", encoding="utf-8") as f:
        f.write(config)
    print("✅ 已创建 Nginx 配置文件: nginx-or.conf")

def create_supervisor_config():
    """创建 Supervisor 配置文件（Linux）"""
    config = """[program:or-flask]
command=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:create_app()
directory=/path/to/or-app/backend
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/or-app/flask.err.log
stdout_logfile=/var/log/or-app/flask.out.log

[program:or-celery]
command=/path/to/venv/bin/celery -A app.celery worker --loglevel=info
directory=/path/to/or-app/backend
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/or-app/celery.err.log
stdout_logfile=/var/log/or-app/celery.out.log
"""
    
    with open("supervisor-or.conf", "w", encoding="utf-8") as f:
        f.write(config)
    print("✅ 已创建 Supervisor 配置文件: supervisor-or.conf")

def create_windows_service_xml():
    """创建 Windows 服务 XML 配置文件（用于 winsw）"""
    config = """<service>
    <id>or-flask</id>
    <name>OR Flask Application</name>
    <description>开源项目技术栈热度可视化系统</description>
    <executable>%BASE%\backend\venv\Scripts\python.exe</executable>
    <arguments>run_prod.py</arguments>
    <workingdirectory>%BASE%\backend</workingdirectory>
    <logmode>rotate</logmode>
    <logpath>%BASE%\backend\logs</logpath>
    <stoptimeout>30 sec</stoptimeout>
    <startmode>Automatic</startmode>
    <delayedAutoStart>true</delayedAutoStart>
    <onfailure action="restart" delay="10 sec"/>
    <serviceaccount>
        <domain>LocalSystem</domain>
    </serviceaccount>
    <environment>
        <variable name="FLASK_ENV" value="production"/>
        <variable name="PYTHONPATH" value="%BASE%\backend"/>
    </environment>
</service>
"""
    
    with open("or-service.xml", "w", encoding="utf-8") as f:
        f.write(config)
    print("✅ 已创建 Windows 服务配置文件: or-service.xml")

def create_docker_compose():
    """创建 Docker Compose 配置文件"""
    config = """version: '3.8'

services:
  backend:
    build: ./backend
    container_name: or-backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=mysql://root:password@db:3306/jobviz
      - FLASK_ENV=production
    volumes:
      - ./backend/logs:/app/logs
      - ./backend/data:/app/data
    depends_on:
      - db
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: or-frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: mysql:8.0
    container_name: or-mysql
    environment:
      - MYSQL_ROOT_PASSWORD=123456
      - MYSQL_DATABASE=jobviz
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./scripts/database/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  redis:
    image: redis:alpine
    container_name: or-redis
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: or-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  mysql_data:
"""
    
    with open("docker-compose.yml", "w", encoding="utf-8") as f:
        f.write(config)
    print("✅ 已创建 Docker Compose 文件: docker-compose.yml")

def create_backend_dockerfile():
    """创建后端 Dockerfile"""
    dockerfile = """FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 设置环境变量
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:create_app()"]
"""
    
    with open("backend/Dockerfile", "w", encoding="utf-8") as f:
        f.write(dockerfile)
    print("✅ 已创建后端 Dockerfile: backend/Dockerfile")

def create_env_file():
    """创建环境变量配置文件"""
    env_config = """# OR 项目环境变量配置

# Flask 配置
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-in-production

# 数据库配置
DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/jobviz
# SQLite 后备配置
# DATABASE_URL=sqlite:///data/app.db

# Redis 配置（可选）
REDIS_URL=redis://localhost:6379/0

# OpenDigger 配置
OPENDIGGER_TIMEOUT=30
OPENDIGGER_CACHE_TTL=3600

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 定时任务配置
CRON_HOUR=2
CRON_MINUTE=0

# 前端配置
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
"""
    
    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(env_config)
    print("✅ 已创建环境变量示例文件: .env.example")

def main():
    print("🚀 创建部署配置文件")
    print("=" * 60)
    
    print("\n请选择要创建的配置文件类型：")
    print("1. 全部配置文件")
    print("2. Windows 部署文件")
    print("3. Linux 部署文件")
    print("4. Docker 部署文件")
    print("5. 环境变量文件")
    
    choice = input("\n请输入选项 (1-5): ").strip()
    
    if choice in ["1", "2"]:
        create_windows_service_xml()
    
    if choice in ["1", "3"]:
        create_nginx_config()
        create_supervisor_config()
    
    if choice in ["1", "4"]:
        create_docker_compose()
        create_backend_dockerfile()
    
    if choice in ["1", "5"]:
        create_env_file()
    
    if choice == "1":
        print("\n✅ 所有配置文件已创建完成！")
    else:
        print(f"\n✅ {choice} 类型的配置文件已创建完成！")
    
    print("\n📋 使用说明：")
    print("1. 根据部署环境修改配置文件中的路径和参数")
    print("2. 生产环境请务必修改 SECRET_KEY 和数据库密码")
    print("3. 使用 deploy.bat 启动部署流程")
    
    input("\n按 Enter 键退出...")

if __name__ == "__main__":
    main()