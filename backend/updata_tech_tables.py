# backend/update_tech_tables.py
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import TechHeat

def update_tech_tables():
    """更新技术相关数据表"""
    print("🔄 更新技术数据表...")
    
    app = create_app()
    
    with app.app_context():
        # 1. 更新技术热度表
        tech_heat_file = '../data/tech_heat.json'
        if os.path.exists(tech_heat_file):
            print("📊 更新技术热度表...")
            with open(tech_heat_file, 'r', encoding='utf-8') as f:
                tech_data = json.load(f)
            
            # 清空现有数据
            TechHeat.query.delete()
            
            # 插入新数据
            for item in tech_data:
                tech = TechHeat(
                    tech_name=item['name'],
                    hot_index=item['hot_index'],
                    star_growth=item.get('star_growth', 0),
                    fork_activity=item.get('fork_activity', 0),
                    rank=item.get('rank', 0),
                    updated_at=datetime.fromisoformat(item.get('updated_at', datetime.now().isoformat()))
                )
                db.session.add(tech)
            
            db.session.commit()
            print(f"✅ 更新了 {len(tech_data)} 条技术热度数据")
        
        print("🎯 技术数据表更新完成！")

if __name__ == '__main__':
    update_tech_tables()