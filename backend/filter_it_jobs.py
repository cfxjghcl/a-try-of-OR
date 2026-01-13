#数据筛选，it职位
import json
import re
import os

def is_it_job(job_name, job_category):
    """判断是否是IT/计算机相关职位"""
    
    if not job_name:
        return False
    
    job_name_lower = job_name.lower()
    
    # 职位名称中的IT关键词（更严格）
    it_keywords = [
        '后端', '前端', '全栈', '开发', '工程师', '架构', '算法',
        '数据', '分析', '运维', '测试', 'QA', 'DevOps', 'SRE',
        '机器学习', '人工智能', 'AI', '大数据', '云计算', '区块链',
        '安全', '网络安全', '信息安全', '软件', '硬件', '嵌入式',
        'Java', 'Python', 'C++', 'C#', 'Go', 'PHP', 'JavaScript',
        'Android', 'iOS', '移动开发', 'App开发', 'Web开发',
        'DBA', '数据库', '系统', '网络', '通信', '物联网'
    ]
    
    
    # 排除明显非IT的职位（更严格）
    exclude_keywords = [
        '教师', '教育', '培训', '销售', '市场', '营销', '推广', '运营',
        '行政', '文员', '助理', '秘书', '人事', '人力', 'hr', '财务', '会计',
        '客服', '售后', '售前', '技术支持', '技术顾问',  # 这些可能属于IT，但先排除
        '司机', '保安', '保洁', '厨师', '医生', '护士', '律师', '翻译',
        '编辑', '记者', '文案', '策划', '设计',  # 泛设计可能包含UI，但这里排除
        '管理', '主管', '经理', '总监', '代表', '专员'  # 泛管理职位
    ]
    
    job_name_lower = job_name.lower() if job_name else ''

    # 检查排除关键词
    for exclude in exclude_keywords:
        if exclude.lower() in job_name_lower:
            return False
    
    # 检查IT关键词
    for keyword in it_keywords:
        if keyword.lower() in job_name_lower:
            return True
    
    # 检查是否有编程语言或技术栈关键词
    tech_keywords = [
        'java', 'python', 'c++', 'c#', 'javascript', 'php', 'go', 'ruby',
        'react', 'vue', 'angular', 'spring', 'django', 'flask',
        'mysql', 'oracle', 'sql', 'mongodb', 'redis',
        'linux', 'docker', 'kubernetes', 'aws', '云计算'
    ]
    
    for tech in tech_keywords:
        if tech.lower() in job_name_lower:
            return True
    
    # 排除非IT职位
    for exclude in exclude_keywords:
        if exclude.lower() in job_name_lower:
            return False
    
    # 检查职位类别
    if job_category:
        it_categories = [
            '计算机', '软件', '互联网', 'IT', '通信', '电子', '网络',
            '游戏', '电子商务', '大数据', '人工智能', '云计算'
        ]
        
        for cat in it_categories:
            if cat in job_category:
                return True
    
    return False

def extract_it_skills(description):
    """从职位描述中提取IT技能"""
    if not description:
        return []
    
    # IT技能关键词库
    it_skills = [
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Go', 'Rust',
        'PHP', 'Ruby', 'Swift', 'Kotlin', 'TypeScript', 'HTML', 'CSS',
        
        'React', 'Vue', 'Angular', 'jQuery', 'Bootstrap', 'Webpack',
        'Vite', 'Next.js', 'Nuxt.js',
        
        'Spring', 'Spring Boot', 'Django', 'Flask', 'FastAPI',
        'Node.js', 'Express', 'NestJS', '.NET', 'ASP.NET',
        
        'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server',
        'SQLite', 'Elasticsearch', 'ClickHouse', 'TiDB',
        
        'Docker', 'Kubernetes', 'Linux', 'Shell', 'Nginx', 'Apache',
        'AWS', '阿里云', '腾讯云', '华为云', 'Azure', 'GCP',
        'Jenkins', 'GitLab CI', 'GitHub Actions', 'Ansible',
        
        'Hadoop', 'Spark', 'Flink', 'Hive', 'Kafka',
        'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy',
        
        'Git', 'SVN', 'Jira', 'Confluence', 'Postman', 'Swagger',
        
        'RESTful', 'API', '微服务', '分布式', '高并发', '多线程'
    ]
    
    found_skills = []
    description_lower = description.lower()
    
    for skill in it_skills:
        if skill.lower() in description_lower:
            found_skills.append(skill)
    
    # 去重并返回
    return list(set(found_skills))[:20]  # 最多返回20个技能

def filter_and_process_data():
    """筛选并处理IT职位数据"""
    
    # 输入文件路径 - 根据你的目录结构调整
    input_file = '../crawler/crawler/data/sampled_jobs.json'
    output_file = '../crawler/crawler/data/it_jobs_filtered.json'
    
    # 如果文件不存在，尝试其他路径
    if not os.path.exists(input_file):
        input_file = '../crawler/data/sampled_jobs.json'
        output_file = '../crawler/data/it_jobs_filtered.json'
    
    if not os.path.exists(input_file):
        print(f"❌ 找不到输入文件: {input_file}")
        print("请确认sampled_jobs.json文件的位置")
        return None
    
    print("📖 正在读取数据...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        print("文件可能格式不正确，尝试修复...")
        # 尝试逐行读取
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        data = []
        for line in lines:
            if line.strip():
                try:
                    data.append(json.loads(line.strip()))
                except:
                    continue
    
    print(f"📊 原始数据量: {len(data)} 条")
    
    # 筛选IT职位
    it_jobs = []
    non_it_jobs = []
    
    for job in data:
        job_name = job.get('job_name', job.get('title', job.get('job_name', '')))
        job_category = job.get('job_catory', job.get('job_category', job.get('job_catory', '')))
        
        if is_it_job(job_name, job_category):
            # 添加标记
            job['is_it_job'] = True
            it_jobs.append(job)
        else:
            non_it_jobs.append(job)
    
    print(f"✅ 筛选出IT职位: {len(it_jobs)} 条")
    print(f"❌ 非IT职位: {len(non_it_jobs)} 条")
    
    # 保存筛选后的数据
    if it_jobs:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(it_jobs, f, ensure_ascii=False, indent=2)
        
        print(f"💾 筛选后的数据已保存到: {output_file}")
        
        # 统计分析
        analyze_it_jobs(it_jobs)
    
    return it_jobs

def analyze_it_jobs(it_jobs):
    """分析IT职位数据"""
    print("\n📈 IT职位分析报告:")
    print("=" * 50)
    
    if not it_jobs:
        print("⚠️ 没有IT职位数据")
        return
    
    # 职位类别分布
    category_count = {}
    for job in it_jobs:
        category = job.get('job_catory', job.get('job_category', '未知类别'))
        if category is None:
            category = '未知类别'
        category_count[category] = category_count.get(category, 0) + 1
    
    print("📋 职位类别分布:")
    for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count} 条")
    
    # 薪资分析 - 修正薪资单位问题
    salaries = []
    for job in it_jobs:
        low = job.get('low_month_pay', 0)
        high = job.get('high_month_pay', 0)
        
        # 处理可能的字符串类型
        try:
            low = float(low) if low else 0
            high = float(high) if high else 0
        except (ValueError, TypeError):
            low = 0
            high = 0
        
        if low > 0 and high > 0:
            # 假设薪资单位是"千元/月"，需要转换为"元/年"
            # 乘以1000转为元，再乘以12转为年薪
            low_annual = low * 1000 * 12
            high_annual = high * 1000 * 12
            avg_annual = (low_annual + high_annual) / 2
            salaries.append(avg_annual)
        elif low > 0:
            # 只有最低薪资
            avg_annual = low * 1000 * 12
            salaries.append(avg_annual)
        elif high > 0:
            # 只有最高薪资
            avg_annual = high * 1000 * 12
            salaries.append(avg_annual)
    
    if salaries:
        print(f"\n💰 薪资分析:")
        print(f"  平均年薪: {sum(salaries)/len(salaries):,.2f} 元")
        print(f"  最高年薪: {max(salaries):,.2f} 元")
        print(f"  最低年薪: {min(salaries):,.2f} 元")
        print(f"  薪资范围: {min(salaries):,.0f} - {max(salaries):,.0f} 元")
    else:
        print(f"\n💰 薪资分析: 无有效薪资数据")
    
    # 热门技能分析
    all_skills = []
    for job in it_jobs:
        description = job.get('description', '')
        skills = extract_it_skills(description)
        all_skills.extend(skills)
    
    if all_skills:
        skill_count = {}
        for skill in all_skills:
            skill_count[skill] = skill_count.get(skill, 0) + 1
        
        print(f"\n🔧 热门技能TOP 10:")
        sorted_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:10]
        for skill, count in sorted_skills:
            print(f"  {skill}: {count} 次")
    else:
        print(f"\n🔧 热门技能: 无技能数据")
    
    # 公司规模统计 - 修复None值问题
    print(f"\n🏢 公司规模统计:")
    company_sizes = {}
    for job in it_jobs:
        # 处理可能的字段名
        size = job.get('company.scale', job.get('company_scale', None))
        if size is None or size == '':
            size = '未知'
        
        # 确保size是字符串
        size = str(size)
        company_sizes[size] = company_sizes.get(size, 0) + 1
    
    # 排序前确保所有值都是字符串
    try:
        for size, count in sorted(company_sizes.items()):
            print(f"  {size}: {count} 条")
    except TypeError:
        # 如果还有类型问题，直接打印不排序
        for size, count in company_sizes.items():
            print(f"  {size}: {count} 条")
    
    # 地区分布
    print(f"\n📍 地区分布:")
    area_counts = {}
    for job in it_jobs:
        area = job.get('area_code_name', job.get('search_area_name', '未知地区'))
        if area is None:
            area = '未知地区'
        area_counts[area] = area_counts.get(area, 0) + 1
    
    for area, count in sorted(area_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {area}: {count} 条")
    
    # 学历要求
    print(f"\n🎓 学历要求分布:")
    degree_counts = {}
    for job in it_jobs:
        degree = job.get('degree_name', '学历不限')
        if degree is None:
            degree = '学历不限'
        degree_counts[degree] = degree_counts.get(degree, 0) + 1
    
    for degree, count in sorted(degree_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {degree}: {count} 条")
    
    print(f"\n📊 分析完成!")

def show_sample_it_jobs(it_jobs, count=5):
    """显示IT职位样本"""
    if not it_jobs:
        print("没有IT职位数据")
        return
    
    print(f"\n🎯 IT职位样本（前{min(count, len(it_jobs))}条）:")
    for i, job in enumerate(it_jobs[:count]):
        job_name = job.get('job_name', '未知职位')
        company = job.get('company_name', '未知公司')
        low_pay = job.get('low_month_pay', 0)
        high_pay = job.get('high_month_pay', 0)
        
        # 计算年薪（千元/月 → 元/年）
        low_annual = float(low_pay) * 1000 * 12 if low_pay else 0
        high_annual = float(high_pay) * 1000 * 12 if high_pay else 0
        
        print(f"{i+1}. {job_name}")
        print(f"   公司: {company}")
        if low_annual and high_annual:
            print(f"   年薪: {low_annual:,.0f} - {high_annual:,.0f} 元")
        elif low_annual:
            print(f"   最低年薪: {low_annual:,.0f} 元")
        elif high_annual:
            print(f"   最高年薪: {high_annual:,.0f} 元")
        else:
            print(f"   薪资: 面议")
        print()

if __name__ == '__main__':
    print("🔍 IT职位筛选工具")
    print("=" * 50)
    
    it_jobs = filter_and_process_data()
    
    if it_jobs:
        show_sample_it_jobs(it_jobs, 5)
        
        # 询问是否查看非IT职位
        view_non_it = input("\n是否查看非IT职位样本? (y/N): ").lower()
        if view_non_it == 'y':
            # 重新读取数据计算非IT职位
            try:
                input_file = '../crawler/crawler/data/sampled_jobs.json'
                if not os.path.exists(input_file):
                    input_file = '../crawler/data/sampled_jobs.json'
                
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                non_it_jobs = []
                for job in data:
                    job_name = job.get('job_name', job.get('title', job.get('job_name', '')))
                    job_category = job.get('job_catory', job.get('job_category', job.get('job_catory', '')))
                    
                    if not is_it_job(job_name, job_category):
                        non_it_jobs.append(job)
                
                print(f"\n❌ 非IT职位样本（前5条）:")
                for i, job in enumerate(non_it_jobs[:5]):
                    job_name = job.get('job_name', '未知职位')
                    company = job.get('company_name', '未知公司')
                    print(f"{i+1}. {job_name} ({company})")
            except Exception as e:
                print(f"读取非IT职位失败: {e}")
    
    print("\n✅ 筛选完成!")
