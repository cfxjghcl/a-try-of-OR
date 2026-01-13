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
    
    return '其他职业'  # 默认分类

def generate_skills_for_career(career_name):
    """根据职业名称生成技能"""
    #由于爬虫爬取的数据有限，缺少技能信息，这里简单根据职业名称生成一些常见技能
    career_lower = career_name.lower()
    skills_map = {
        # 编程语言
        'Python': ['python', '爬虫', '数据分析', '机器学习'],
        'Java': ['java', 'spring', '后端', '安卓'],
        'JavaScript': ['javascript', '前端', 'web', 'node'],
        'C++': ['c++', '算法', '游戏', '嵌入式'],
        'C#': ['c#', '.net', 'unity'],
        'Go': ['go', '后端', '并发'],
        'PHP': ['php', 'web', '后端'],
        'Swift': ['swift', 'ios'],
        'Kotlin': ['kotlin', '安卓'],
        'TypeScript': ['typescript', '前端'],
        
        # 前端框架
        'React': ['react', '前端'],
        'Vue': ['vue', '前端'],
        'Angular': ['angular', '前端'],
        
        # 后端框架
        'Spring': ['spring', 'java', '后端'],
        'Django': ['django', 'python', '后端'],
        'Flask': ['flask', 'python', '后端'],
        'Express': ['express', 'node', '后端'],
        
        # 数据库
        'MySQL': ['mysql', '数据库'],
        'PostgreSQL': ['postgresql', '数据库'],
        'MongoDB': ['mongodb', '数据库', 'nosql'],
        'Redis': ['redis', '缓存', '数据库'],
        'Oracle': ['oracle', '数据库'],
        
        # 运维工具
        'Linux': ['linux', '运维', '服务器'],
        'Docker': ['docker', '容器', '运维'],
        'Kubernetes': ['kubernetes', 'k8s', '容器'],
        'AWS': ['aws', '云计算', '运维'],
        '阿里云': ['阿里云', '云计算'],
        '腾讯云': ['腾讯云', '云计算'],
        
        # 大数据/AI
        'Hadoop': ['hadoop', '大数据'],
        'Spark': ['spark', '大数据'],
        'TensorFlow': ['tensorflow', '机器学习', 'ai'],
        'PyTorch': ['pytorch', '深度学习', 'ai'],
        
        # 工具
        'Git': ['git', '版本控制'],
        'Jenkins': ['jenkins', 'ci/cd'],
        'Jira': ['jira', '项目管理']
    }
    
    # 收集匹配的技能
    matched_skills = []
    for skill, keywords in skills_map.items():
        for keyword in keywords:
            if keyword in career_lower:
                matched_skills.append(skill)
                break
    # 去重，并取前5个
    unique_skills = list(dict.fromkeys(matched_skills))
    return unique_skills[:5]

def process_it_job_data():
    """处理完整数据集并导入数据库"""
    print("🚀 开始处理完整数据集...")
    
    # 数据文件路径 - 修改这里！
    data_file = '../data/jobs.json'
    
    if not os.path.exists(data_file):
        print(f"❌ 找不到数据文件: {data_file}")
        # 尝试其他可能的路径
        data_file = 'data/jobs.json'
        if not os.path.exists(data_file):
            print(f"❌ 找不到数据文件: {data_file}")
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
            Career.query.delete()  # 也清除职业表，重新开始
            db.session.commit()
        
        print(f"📖 正在读取数据文件: {data_file}")
        
        # 读取数据 - 添加这部分！
        jobs = []
        try:
            # 尝试读取JSON文件（可能是数组或每行一个JSON对象）
            with open(data_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # 检查是否为JSON数组
                if content.startswith('['):
                    jobs = json.loads(content)
                else:
                    # 可能是每行一个JSON对象
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip():
                            try:
                                jobs.append(json.loads(line.strip()))
                            except json.JSONDecodeError:
                                continue
            
            print(f"✅ 成功读取 {len(jobs)} 条职位数据")
            
        except Exception as e:
            print(f"❌ 读取数据失败: {e}")
            return
        
        # 定义IT职位判断函数 - 添加这个！
        def is_it_job_simple(job_name, job_category):
            """判断是否是IT职位"""
            if not job_name:
                return False
            
            job_lower = job_name.lower()
            job_cat_lower = str(job_category).lower() if job_category else ''
            
            # IT职位关键词
            it_keywords = [
                '开发', '工程', '测试', '运维', '数据', '算法', '网络', '安全',
                '软件', '硬件', '前端', '后端', '全栈', '架构', '移动', 'app',
                'java', 'python', 'c++', 'javascript', 'php', 'go', 'ruby',
                '数据库', '系统', '嵌入式', '通信', '物联网', '云计算', '大数据',
                '人工智能', '机器学习', '深度学习', '区块链', 'devops', 'sre',
                'dba', 'ui设计', 'ux设计', '产品经理', '项目经理', '技术支持'
            ]
            
            # 排除明显非IT职位
            exclude_keywords = [
                '教师', '教育', '培训', '销售', '市场', '行政', '财务', '会计',
                '人力', '人事', '运营', '客服', '文员', '助理', '秘书', '司机',
                '保安', '保洁', '厨师', '医生', '护士', '律师', '翻译', '编辑',
                '记者', '文案', '策划', '设计', '管理', '主管', '经理', '总监',
                '代表', '专员', '顾问', '分析', '投资', '金融', '保险', '银行'
            ]
            
            # 检查排除关键词
            for exclude in exclude_keywords:
                if exclude in job_lower:
                    return False
            
            # 检查IT关键词
            for keyword in it_keywords:
                if keyword in job_lower:
                    return True
            
            return False
        
        # 筛选IT职位 - 添加这部分！
        print("\n🔍 正在筛选IT职位...")
        it_jobs = []
        non_it_jobs = []
        
        for job in jobs:
            job_name = job.get('job_name', job.get('title', ''))
            job_category = job.get('job_catory', job.get('job_category', job.get('job_catory', '')))
            
            if is_it_job_simple(job_name, job_category):
                it_jobs.append(job)
            else:
                non_it_jobs.append(job)
        
        print(f"✅ 筛选出 {len(it_jobs)} 个IT职位")
        print(f"❌ 排除 {len(non_it_jobs)} 个非IT职位")
        
        if not it_jobs:
            print("❌ 没有IT职位数据，无法导入")
            return
        
        print(f"\n📊 开始处理 {len(it_jobs)} 个IT职位...")
        
        # 按职业分类统计
        career_stats = defaultdict(lambda: {
            'count': 0,
            'salaries': [],
            'skills': set(),
            'companies': set(),
            'job_names': []
        })
        
        # 第一遍：统计信息
        processed_count = 0
        for job in it_jobs:
            try:
                job_name = job.get('job_name', '').strip()
                if not job_name:
                    continue
                
                # 分类 - 使用更智能的分类
                category = classify_it_job(job_name)
                
                # 解析薪资（千元/月 → 元/年）
                try:
                    low_month = float(job.get('low_month_pay', 0))
                    high_month = float(job.get('high_month_pay', 0))
                except (ValueError, TypeError):
                    low_month = 0
                    high_month = 0
                
                # 计算年薪 - 改进的薪资处理
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
                    # 根据职位分类设定默认年薪
                    if '算法' in category or 'AI' in category:
                        avg_annual = 250000
                    elif '后端' in category or '架构' in category:
                        avg_annual = 200000
                    elif '前端' in category or '数据' in category:
                        avg_annual = 180000
                    elif '测试' in category or '运维' in category:
                        avg_annual = 150000
                    else:
                        avg_annual = 150000  # 默认15万元
                
                # 公司
                company = job.get('company_name', '')
                
                # 提取技能 - 改进的技能提取
                description = job.get('description', '')
                skills = []
                
                job_name_lower = job_name.lower()
                tech_keywords = [
                    # 编程语言
                    'Java', 'Python', 'C++', 'C#', 'JavaScript', 'PHP', 'Go', 'Rust',
                    'Ruby', 'Swift', 'Kotlin', 'TypeScript', 'Scala', 'Perl',
                    
                    # 前端技术
                    'React', 'Vue', 'Angular', 'jQuery', 'Bootstrap', 'Webpack',
                    'Vite', 'Next.js', 'Nuxt.js', 'Sass', 'Less',
                    
                    # 后端技术
                    'Spring', 'Spring Boot', 'Django', 'Flask', 'FastAPI', 'Express',
                    'NestJS', '.NET', 'ASP.NET', 'Node.js', 'Laravel', 'Symfony',
                    
                    # 数据库
                    'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server',
                    'SQLite', 'Elasticsearch', 'ClickHouse', 'TiDB', 'Cassandra',
                    
                    # 云计算与运维
                    'Docker', 'Kubernetes', 'Linux', 'Shell', 'Nginx', 'Apache',
                    'AWS', '阿里云', '腾讯云', '华为云', 'Azure', 'GCP',
                    'Jenkins', 'GitLab CI', 'GitHub Actions', 'Ansible', 'Terraform',
                    
                    # 大数据与AI
                    'Hadoop', 'Spark', 'Flink', 'Hive', 'Kafka', 'Storm',
                    'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy',
                    
                    # 工具和框架
                    'Git', 'SVN', 'Jira', 'Confluence', 'Postman', 'Swagger',
                    'Maven', 'Gradle', 'WebSocket', 'RESTful', '微服务', '分布式'
                ]
                
                # 从职位名称提取技能
                for skill in tech_keywords:
                    if skill.lower() in job_name_lower:
                        skills.append(skill)
                
                # 从描述提取技能
                if description:
                    for skill in tech_keywords:
                        if skill.lower() in description.lower():
                            skills.append(skill)
                
                # 根据职位类别添加默认技能
                if not skills:
                    if '后端' in category:
                        skills = ['Java', 'Spring', 'MySQL', 'Linux']
                    elif '前端' in category:
                        skills = ['JavaScript', 'React', 'Vue', 'HTML/CSS']
                    elif '数据' in category:
                        skills = ['Python', 'SQL', 'Hadoop', 'Spark']
                    elif '算法' in category:
                        skills = ['Python', 'TensorFlow', 'PyTorch', '机器学习']
                    elif '测试' in category:
                        skills = ['Python', 'Selenium', '自动化测试', 'Linux']
                    elif '运维' in category:
                        skills = ['Linux', 'Docker', 'Kubernetes', 'Shell']
                    else:
                        skills = ['Python', 'Java', 'SQL', 'Git']
                
                # 更新统计
                stats = career_stats[category]
                stats['count'] += 1
                stats['salaries'].append(avg_annual)
                if company:
                    stats['companies'].add(company)
                stats['skills'].update(skills)
                stats['job_names'].append(job_name)
                
                processed_count += 1
                if processed_count % 100 == 0:
                    print(f"  已处理 {processed_count}/{len(it_jobs)} 条记录")
                
            except Exception as e:
                print(f"⚠️ 处理职位失败: {job.get('job_name', '未知')} - {e}")
                continue
        
        print(f"\n📋 职位分类统计:")
        for category, stats in sorted(career_stats.items(), key=lambda x: x[1]['count'], reverse=True):
            if stats['salaries']:
                avg_salary = sum(stats['salaries']) / len(stats['salaries'])
                print(f"  {category}: {stats['count']} 条, 平均年薪: {avg_salary:,.0f} 元")
        
        # 第二遍：创建或更新职业
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
                description += f"，例如：{'、'.join(sample_jobs[:2])}"
            
            # 查找或创建职业
            career = Career.query.filter_by(name=category).first()
            if not career:
                career = Career(
                    name=category,
                    category="开发",  # 统一分类
                    avg_entry_salary=avg_salary,
                    description=description,
                    demand_level=min(5, 1 + stats['count'] // 10),  # 根据数量确定需求等级
                    required_skills=', '.join(list(stats['skills'])[:5]),
                    in_demand=stats['count'] >= 2  # 有2个以上职位算需求高
                )
                db.session.add(career)
                created_count += 1
                print(f"➕ 创建职业: {category} ({stats['count']}条数据)")
            else:
                # 更新现有职业
                career.avg_entry_salary = avg_salary
                career.description = description
                career.demand_level = min(5, 1 + stats['count'] // 10)
                career.in_demand = stats['count'] >= 2
                updated_count += 1
                print(f"🔄 更新职业: {category} ({stats['count']}条数据)")
            
            # 需要先提交以获取career.id
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"❌ 提交职业失败: {e}")
                continue
            
            # 生成2020-2026年的趋势数据
            base_year = 2024  # 假设数据是2024年的
            for year in range(2020, 2027):
                try:
                    # 计算该年份的就业率（模拟）
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
                    
                    # 计算该年份的薪资
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
                    
                except Exception as e:
                    print(f"⚠️ 创建{year}年趋势数据失败: {e}")
            
            # 创建技能记录
            if stats['skills']:
                # 取前5个技能
                top_skills = list(stats['skills'])[:5]
                
                for i, skill_name in enumerate(top_skills):
                    try:
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
                    except Exception as e:
                        print(f"⚠️ 创建技能失败: {skill_name} - {e}")
            
            # 提交当前职业的所有数据
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"❌ 提交{category}数据失败: {e}")
        
        # 最终统计
        print(f"\n✅ 数据导入完成！")
        print(f"   创建: {created_count} 个新职业")
        print(f"   更新: {updated_count} 个现有职业")
        
        try:
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
            print(f"❌ 查询统计信息失败: {e}")

if __name__ == '__main__':
    process_it_job_data()

def classify_it_job(job_name):
    """根据职位名称智能分类IT职位"""
    if not job_name:
        return '其他IT职位'
    
    job_name_lower = job_name.lower()
    
    classification_rules = {
        '后端开发工程师': ['后端开发', 'java开发', 'python开发', 'c++开发', 'go开发', 'php开发', '服务器开发'],
        '前端开发工程师': ['前端开发', 'web前端', 'javascript开发', 'vue开发', 'react开发', 'angular开发'],
        '移动开发工程师': ['android开发', 'ios开发', '移动开发', 'app开发', 'flutter', 'react native'],
        '软件工程师': ['软件工程师', '软件开发'],
        '算法工程师': ['算法工程师', '机器学习', '深度学习', '人工智能', 'ai工程师'],
        '数据工程师': ['数据工程师', '数据分析师', '大数据工程师', 'etl工程师'],
        '测试工程师': ['测试工程师', 'qa工程师', '测试开发', '软件测试'],
        '运维工程师': ['运维工程师', 'devops', 'sre', '系统运维', '网络运维'],
        '安全工程师': ['安全工程师', '网络安全', '信息安全', '渗透测试'],
        '嵌入式工程师': ['嵌入式工程师', '嵌入式开发', '单片机', 'fpga'],
        '硬件工程师': ['硬件工程师', 'pcb设计', '电路设计'],
        '网络工程师': ['网络工程师', '通信工程师'],
        'UI设计师': ['ui设计', 'ui', '视觉设计'],
        'UX设计师': ['ux设计', 'ux', '交互设计'],
        '产品经理': ['产品经理', '产品'],
        '项目经理': ['项目经理', '项目'],
        '架构师': ['架构师', '系统架构师'],
        '数据库管理员': ['dba', '数据库管理员'],
        '技术支持工程师': ['技术支持', '技术顾问']
    }
    
    for category, keywords in classification_rules.items():
        for keyword in keywords:
            if keyword in job_name_lower:
                return category
    
    # 如果没有匹配到，根据关键词返回
    if any(word in job_name_lower for word in ['开发', '工程']):
        return '开发工程师'
    elif any(word in job_name_lower for word in ['数据', '分析']):
        return '数据分析师'
    elif any(word in job_name_lower for word in ['测试', 'qa']):
        return '测试工程师'
    elif any(word in job_name_lower for word in ['运维', 'devops']):
        return '运维工程师'
    elif any(word in job_name_lower for word in ['产品', 'pm']):
        return '产品经理'
    else:
        return 'IT工程师'