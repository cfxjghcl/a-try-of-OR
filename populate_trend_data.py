#本文件用于生成模拟数据，用于调试模块
import random
from datetime import datetime

# 方法1：导入create_app并创建应用实例
from app import create_app, db
from app.models import Career, EmploymentRate, SalaryTrend, Skill

def populate_trend_data():
    """填充趋势数据"""
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        # 清空现有数据（可选）
        print("正在清空现有趋势数据...")
        EmploymentRate.query.delete()
        SalaryTrend.query.delete()
        Skill.query.delete()
        
        careers = Career.query.all()
        print(f"找到 {len(careers)} 个职业")
        
        for career in careers:
            print(f"正在处理职业: {career.name}")
            
            # 为每个职业生成2020-2026年的趋势数据
            for year in range(2020, 2027):  # 2020-2026，包括2026
                # 就业率数据
                emp_rate = EmploymentRate(
                    career_id=career.id,
                    year=year,
                    employment_rate=round(80 + random.uniform(0, 20), 1)
                )
                db.session.add(emp_rate)
                
                # 薪资趋势数据 - 模拟每年增长5%
                base_salary = float(career.avg_entry_salary) if career.avg_entry_salary else 15000
                growth_factor = 1 + (year - 2020) * 0.05
                
                salary_trend = SalaryTrend(
                    career_id=career.id,
                    year=year,
                    avg_salary=round(base_salary * growth_factor, 2),
                    min_salary=round(base_salary * growth_factor * 0.7, 2),
                    max_salary=round(base_salary * growth_factor * 1.5, 2)
                )
                db.session.add(salary_trend)
            
            # 技能数据
            skill_names = ["Python", "Java", "SQL", "Git", "Linux", "Docker", "AWS", "JavaScript", 
                          "HTML/CSS", "React", "Vue", "Spring Boot", "MySQL", "PostgreSQL", "MongoDB"]
            
            # 根据职业类别选择不同的技能
            if "后端" in career.name or "Java" in career.name:
                selected_skills = ["Java", "Spring Boot", "MySQL", "Git", "Linux"]
            elif "前端" in career.name:
                selected_skills = ["JavaScript", "HTML/CSS", "React", "Vue", "Git"]
            elif "数据" in career.name or "分析" in career.name:
                selected_skills = ["Python", "SQL", "MySQL", "MongoDB", "Linux"]
            elif "AI" in career.name or "算法" in career.name:
                selected_skills = ["Python", "SQL", "Git", "Linux", "Docker"]
            else:
                selected_skills = random.sample(skill_names, 5)
            
            for skill_name in selected_skills:
                skill = Skill(
                    career_id=career.id,
                    skill_name=skill_name,
                    importance_level=random.randint(3, 5),
                    is_required=random.choice([True, False])
                )
                db.session.add(skill)
        
        try:
            db.session.commit()
            print(f"✅ 趋势数据填充完成！")
            print(f"   - 就业率数据: {len(careers) * 7} 条 (每个职业7年数据)")
            print(f"   - 薪资趋势数据: {len(careers) * 7} 条")
            print(f"   - 技能数据: {len(careers) * 5} 条")
        except Exception as e:
            db.session.rollback()
            print(f"❌ 提交失败: {e}")
            raise

if __name__ == '__main__':
    populate_trend_data()