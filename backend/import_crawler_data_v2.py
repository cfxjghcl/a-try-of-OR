# backend/import_crawler_data_v2.py
import json
import re
import sys
import os
from datetime import datetime
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Career, EmploymentRate, SalaryTrend, Skill

# IT职位分类器
def classify_it_job(job_name):
    """智能分类IT职位"""
    job_name_lower = job_name.lower()
    
    classification_rules = {
        '后端开发工程师': ['后端开发', 'java开发', 'python开发', 'c++开发', 'go开发', 'php开发', '服务器开发'],
        '前端开发工程师': ['前端开发', 'web前端', 'javascript开发', 'vue开发', 'react开发', 'angular开发'],
        '移动开发工程师': ['android开发', 'ios开发', '移动开发', 'app开发', 'flutter', 'react native'],
        '全栈开发工程师': ['全栈开发', '全栈工程师'],
        '软件工程师': ['软件工程师', '软件开发'],
        '算法工程师': ['算法工程师', '机器学习', '深度学习', '人工智能', 'ai工程师'],
        '数据工程师': ['数据工程师', '数据分析师', '大数据工程师', 'etl工程师'],
        '测试工程师': ['测试工程师', 'qa工程师', '测试开发', '软件测试'],
        '运维工程师': ['运维工程师', 'devops', 'sre', '系统运维', '网络运维'],
        '安全工程师': ['安全工程师', '网络安全', '信息安全', '渗透测试'],
        '嵌入式工程师': ['嵌入式工程师', '嵌入式开发', '单片机', 'fpga'],
        '硬件工程师': ['硬件工程师', 'pcb设计', '电路设计'],
        '通信工程师': ['通信工程师', '网络工程师', '通信技术'],
        'UI/UX设计师': ['ui设计', 'ux设计', '交互设计', '视觉设计', 'ui设计师'],
        '产品经理': ['产品经理', '产品专员'],
        '项目经理': ['项目经理', '项目专员'],
        '数据库管理员': ['dba', '数据库管理员'],
        '系统架构师': ['系统架构师', '架构师']
    }
    
    for category, keywords in classification_rules.items():
        for keyword in keywords:
            if keyword in job_name_lower:
                return category
    
    return 'IT工程师'  # 默认分类

def process_it_job_data():
    """处理爬虫数据并导入数据库"""
    print("🚀 开始处理爬虫数据...")
    
    # 1. 先筛选IT职位
    try:
        from filter_it_jobs import filter_and_process_data
        it_jobs = filter_and_process_data()
    except ImportError:
        print("❌ 无法导入filter_it_jobs模块")
        return
    
    if not it_jobs:
        print("❌ 没有IT职位数据，无法导入")
        return
    
    app = create_app()
    
    with app.app_context():
        # 清空现有数据（可选）
        confirm = input("\n是否清空现有职业相关数据? (y/N): ").lower()
        if confirm == 'y':
            print("🧹 清空现有数据...")
            EmploymentRate.query.delete()
            SalaryTrend.query.delete()
            Skill.query.delete()
            # 不清除careers表，保留用户收藏关系
            db.session.commit()
        
        print(f"\n📊 处理 {len(it_jobs)} 个IT职位...")
        
        # 按职业分类统计
        career_stats = defaultdict(lambda: {
            'count': 0,
            'salaries': [],
            'skills': set(),
            'companies': set(),
            'job_names': []
        })
        
        # 第一遍：统计信息
        for job in it_jobs:
            try:
                job_name = job.get('job_name', '').strip()
                if not job_name:
                    continue
                
                # 分类
                category = classify_it_job(job_name)
                
                # 解析薪资（千元/月 → 元/年）
                try:
                    low_month = float(job.get('low_month_pay', 0))
                    high_month = float(job.get('high_month_pay', 0))
                except (ValueError, TypeError):
                    low_month = 0
                    high_month = 0
                
                if low_month > 0 and high_month > 0:
                    # 月薪(千元) → 年薪(元)
                    low_annual = low_month * 1000 * 12
                    high_annual = high_month * 1000 * 12
                    avg_annual = (low_annual + high_annual) / 2
                elif low_month > 0:
                    avg_annual = low_month * 1000 * 12
                elif high_month > 0:
                    avg_annual = high_month * 1000 * 12
                else:
                    # 默认年薪
                    avg_annual = 150000  # 15万元
                
                company = job.get('company_name', '')
                
                # 提取技能（从职位名称和描述）
                description = job.get('description', '')
                skills = []
                
                job_name_lower = job_name.lower()
                tech_keywords = [
                    'Java', 'Python', 'C++', 'C#', 'JavaScript', 'PHP', 'Go',
                    'React', 'Vue', 'Angular', 'Spring', 'Django', 'Flask',
                    'MySQL', 'Oracle', 'SQL', 'MongoDB', 'Redis',
                    'Linux', 'Docker', 'Kubernetes', 'AWS'
                ]
                
                for skill in tech_keywords:
                    if skill.lower() in job_name_lower:
                        skills.append(skill)
                
                # 从描述提取技能
                if description:
                    for skill in tech_keywords:
                        if skill.lower() in description.lower():
                            skills.append(skill)
                
                # 更新统计
                stats = career_stats[category]
                stats['count'] += 1
                stats['salaries'].append(avg_annual)
                if company:
                    stats['companies'].add(company)
                stats['skills'].update(skills)
                stats['job_names'].append(job_name)
                
            except Exception as e:
                print(f"⚠️ 处理职位失败: {e}")
                continue
        
        print(f"\n📋 职位分类统计:")
        for category, stats in sorted(career_stats.items(), key=lambda x: x[1]['count'], reverse=True):
            if stats['salaries']:
                avg_salary = sum(stats['salaries']) / len(stats['salaries'])
                print(f"  {category}: {stats['count']} 条, 平均年薪: {avg_salary:,.0f} 元")
        
        # 创建或更新职业
        created_count = 0
        updated_count = 0
        
        for category, stats in career_stats.items():
            if stats['count'] == 0:
                continue
            
            # 计算平均薪资
            avg_salary = sum(stats['salaries']) / len(stats['salaries']) if stats['salaries'] else 150000
            
            # 生成职业描述
            company_count = len(stats['companies'])
            sample_jobs = stats['job_names'][:3]  # 取前3个职位名称作为示例
            
            description = f"{category}岗位，平均年薪{avg_salary:,.0f}元"
            if company_count > 0:
                description += f"，来自{company_count}家公司"
            if sample_jobs:
                description += f"，例如：{'、'.join(sample_jobs)}"
            
            # 查找或创建职业
            career = Career.query.filter_by(name=category).first()
            if not career:
                career = Career(
                    name=category,
                    category="IT/互联网",  # 统一分类
                    avg_entry_salary=avg_salary,
                    description=description,
                    in_demand=stats['count'] >= 2  # 有2个以上职位算需求高
                )
                db.session.add(career)
                db.session.flush()
                created_count += 1
                print(f"➕ 创建职业: {category} ({stats['count']}条数据)")
            else:
                # 更新现有职业
                career.avg_entry_salary = avg_salary
                career.description = description
                career.in_demand = stats['count'] >= 2
                updated_count += 1
                print(f"🔄 更新职业: {category} ({stats['count']}条数据)")
            
            # 生成2020-2026年的趋势数据
            base_year = 2024  # 假设数据是2024年的
            for year in range(2020, 2027):
                # 计算该年份的就业率（模拟）
                # 假设2024年就业率最高，其他年份按时间递减
                if year == base_year:
                    employment_rate = min(95, 70 + stats['count'] * 2)
                else:
                    # 其他年份模拟
                    diff = abs(year - base_year)
                    employment_rate = 70 + stats['count'] * 2 - diff * 5
                    employment_rate = max(60, min(95, employment_rate))
                
                # 创建就业率记录
                emp_record = EmploymentRate.query.filter_by(
                    career_id=career.id, year=year
                ).first()
                
                if not emp_record:
                    emp_record = EmploymentRate(
                        career_id=career.id,
                        year=year,
                        employment_rate=round(employment_rate, 1)
                    )
                    db.session.add(emp_record)
                
                # 计算该年份的薪资（模拟增长）
                year_diff = year - base_year
                year_salary = avg_salary * (1 + year_diff * 0.05)  # 每年增长5%
                
                # 创建薪资趋势记录
                salary_record = SalaryTrend.query.filter_by(
                    career_id=career.id, year=year
                ).first()
                
                if not salary_record:
                    salary_record = SalaryTrend(
                        career_id=career.id,
                        year=year,
                        avg_salary=round(year_salary, 2),
                        min_salary=round(year_salary * 0.7, 2),
                        max_salary=round(year_salary * 1.5, 2)
                    )
                    db.session.add(salary_record)
            
            # 创建技能记录
            if stats['skills']:
                # 取前5个技能
                top_skills = list(stats['skills'])[:5]
                
                for i, skill_name in enumerate(top_skills):
                    # 根据顺序确定重要性
                    importance = 5 - i  # 第一个最重要
                    
                    skill_record = Skill.query.filter_by(
                        career_id=career.id,
                        skill_name=skill_name
                    ).first()
                    
                    if not skill_record:
                        skill_record = Skill(
                            career_id=career.id,
                            skill_name=skill_name,
                            importance_level=importance,
                            is_required=importance >= 3
                        )
                        db.session.add(skill_record)
        
        # 提交所有更改
        try:
            db.session.commit()
            print(f"\n✅ 数据导入完成！")
            print(f"   创建: {created_count} 个新职业")
            print(f"   更新: {updated_count} 个现有职业")
            
            # 显示导入结果
            total_careers = Career.query.count()
            total_employment = EmploymentRate.query.count()
            total_salary = SalaryTrend.query.count()
            total_skills = Skill.query.count()
            
            print(f"\n📊 数据库状态:")
            print(f"  职业数量: {total_careers}")
            print(f"  就业率记录: {total_employment}")
            print(f"  薪资趋势记录: {total_salary}")
            print(f"  技能记录: {total_skills}")
            
            # 显示所有职业
            print(f"\n📋 当前所有职业:")
            careers = Career.query.all()
            for career in careers:
                skills = Skill.query.filter_by(career_id=career.id).all()
                skill_names = [s.skill_name for s in skills[:3]]
                print(f"  {career.name}: {career.avg_entry_salary:,.0f}元" + 
                      (f" [技能: {', '.join(skill_names)}]" if skill_names else ""))
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 提交失败: {e}")
            raise

if __name__ == '__main__':
    process_it_job_data()
