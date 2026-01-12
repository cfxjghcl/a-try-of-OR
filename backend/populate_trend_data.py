#本文件用于生成模拟数据，用于调试模块
import random
from datetime import datetime
from app import db, app
from app.models import Career, EmploymentRate, SalaryTrend, Skill

def populate_trend_data():
    """填充趋势数据"""
    with app.app_context():
        careers = Career.query.all()
        
        for career in careers:
            for year in range(2020, 2026):
                # 就业率数据
                emp_rate = EmploymentRate(
                    career_id=career.id,
                    year=year,
                    employment_rate=round(80 + random.uniform(0, 20), 1)
                )
                db.session.add(emp_rate)
                
                # 薪资趋势数据
                salary_trend = SalaryTrend(
                    career_id=career.id,
                    year=year,
                    avg_salary=career.avg_entry_salary * (1 + (year-2020)*0.1),  # 每年增长10%
                    min_salary=career.avg_entry_salary * 0.7,
                    max_salary=career.avg_entry_salary * 1.5
                )
                db.session.add(salary_trend)
            
            # 技能数据
            skill_names = ["Python", "Java", "SQL", "Git", "Linux", "Docker", "AWS"]
            for skill_name in random.sample(skill_names, 4):
                skill = Skill(
                    career_id=career.id,
                    skill_name=skill_name,
                    importance_level=random.randint(2, 5),
                    is_required=random.choice([True, False])
                )
                db.session.add(skill)
        
        db.session.commit()
        print("趋势数据填充完成！")

if __name__ == '__main__':
    populate_trend_data()