# backend/generate_tech_data.py
import json
import random
from datetime import datetime

def generate_tech_heat_data():
    """生成技术栈热度数据"""
    # 常见技术栈
    tech_stacks = [
        {"name": "Python", "hot_index": 95, "star_growth": 12.5, "fork_activity": 8.7},
        {"name": "Java", "hot_index": 88, "star_growth": 8.2, "fork_activity": 6.5},
        {"name": "JavaScript", "hot_index": 92, "star_growth": 10.3, "fork_activity": 9.1},
        {"name": "TypeScript", "hot_index": 85, "star_growth": 15.2, "fork_activity": 7.8},
        {"name": "Go", "hot_index": 82, "star_growth": 18.4, "fork_activity": 6.2},
        {"name": "Rust", "hot_index": 78, "star_growth": 22.1, "fork_activity": 5.4},
        {"name": "C++", "hot_index": 80, "star_growth": 7.5, "fork_activity": 4.8},
        {"name": "C#", "hot_index": 75, "star_growth": 6.8, "fork_activity": 4.2},
        {"name": "PHP", "hot_index": 68, "star_growth": 3.2, "fork_activity": 3.1},
        {"name": "Swift", "hot_index": 72, "star_growth": 9.5, "fork_activity": 4.5},
        {"name": "Kotlin", "hot_index": 76, "star_growth": 14.3, "fork_activity": 5.2},
        {"name": "React", "hot_index": 90, "star_growth": 11.8, "fork_activity": 8.9},
        {"name": "Vue", "hot_index": 87, "star_growth": 13.4, "fork_activity": 8.3},
        {"name": "Angular", "hot_index": 72, "star_growth": 5.6, "fork_activity": 4.1},
        {"name": "Spring Boot", "hot_index": 84, "star_growth": 9.2, "fork_activity": 6.8},
        {"name": "Django", "hot_index": 79, "star_growth": 8.7, "fork_activity": 5.9},
        {"name": "Flask", "hot_index": 76, "star_growth": 7.9, "fork_activity": 5.4},
        {"name": "Express", "hot_index": 73, "star_growth": 8.1, "fork_activity": 5.1},
        {"name": "MySQL", "hot_index": 86, "star_growth": 6.5, "fork_activity": 4.8},
        {"name": "PostgreSQL", "hot_index": 81, "star_growth": 9.2, "fork_activity": 5.3},
        {"name": "MongoDB", "hot_index": 78, "star_growth": 8.4, "fork_activity": 5.0},
        {"name": "Redis", "hot_index": 83, "star_growth": 10.2, "fork_activity": 5.7},
        {"name": "Docker", "hot_index": 89, "star_growth": 12.8, "fork_activity": 7.9},
        {"name": "Kubernetes", "hot_index": 86, "star_growth": 15.3, "fork_activity": 6.8},
        {"name": "AWS", "hot_index": 88, "star_growth": 13.7, "fork_activity": 7.2},
    ]
    
    # 添加时间戳和排名
    for i, tech in enumerate(tech_stacks):
        tech["rank"] = i + 1
        tech["updated_at"] = datetime.now().isoformat()
    
    # 保存数据
    output_file = '../data/tech_heat.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tech_stacks, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 生成了 {len(tech_stacks)} 个技术栈热度数据")
    print(f"💾 已保存到: {output_file}")
    
    return tech_stacks

def generate_wordcloud_data():
    """生成词云数据"""
    tech_words = [
        {"name": "Python", "value": 95},
        {"name": "Java", "value": 88},
        {"name": "JavaScript", "value": 92},
        {"name": "前端开发", "value": 85},
        {"name": "后端开发", "value": 87},
        {"name": "数据科学", "value": 78},
        {"name": "机器学习", "value": 82},
        {"name": "人工智能", "value": 84},
        {"name": "云计算", "value": 79},
        {"name": "大数据", "value": 76},
        {"name": "区块链", "value": 68},
        {"name": "物联网", "value": 72},
        {"name": "DevOps", "value": 81},
        {"name": "微服务", "value": 77},
        {"name": "容器技术", "value": 83},
        {"name": "数据库", "value": 89},
        {"name": "算法", "value": 86},
        {"name": "架构设计", "value": 80},
        {"name": "网络安全", "value": 75},
        {"name": "移动开发", "value": 73},
        {"name": "React", "value": 90},
        {"name": "Vue", "value": 87},
        {"name": "Spring", "value": 84},
        {"name": "Docker", "value": 89},
        {"name": "Kubernetes", "value": 86},
        {"name": "MySQL", "value": 86},
        {"name": "Redis", "value": 83},
        {"name": "Linux", "value": 88},
        {"name": "Git", "value": 91},
        {"name": "CI/CD", "value": 79},
    ]
    
    # 添加一些随机性
    for word in tech_words:
        word["value"] = word["value"] + random.randint(-5, 5)
        word["value"] = max(50, min(100, word["value"]))
    
    # 保存数据
    output_file = '../data/wordcloud.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tech_words, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 生成了 {len(tech_words)} 个词云数据")
    print(f"💾 已保存到: {output_file}")
    
    return tech_words

def generate_github_trend_data():
    """生成GitHub趋势数据"""
    import random
    from datetime import datetime, timedelta
    
    trends = []
    today = datetime.now()
    
    # 生成30天的数据
    for i in range(30):
        date = (today - timedelta(days=29-i)).strftime("%Y-%m-%d")
        
        daily_trends = [
            {"name": "Python", "stars": random.randint(50, 200)},
            {"name": "JavaScript", "stars": random.randint(40, 180)},
            {"name": "TypeScript", "stars": random.randint(30, 150)},
            {"name": "Go", "stars": random.randint(20, 120)},
            {"name": "Rust", "stars": random.randint(15, 100)},
            {"name": "Java", "stars": random.randint(25, 130)},
        ]
        
        # 添加一些随机波动
        for item in daily_trends:
            item["stars"] = max(10, item["stars"] + random.randint(-20, 20))
        
        trends.append({
            "date": date,
            "trends": daily_trends
        })
    
    # 保存数据
    output_file = '../data/github_trends.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(trends, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 生成了 {len(trends)} 天GitHub趋势数据")
    print(f"💾 已保存到: {output_file}")
    
    return trends

if __name__ == '__main__':
    print("🚀 开始生成模拟数据...")
    print("=" * 50)
    
    generate_tech_heat_data()
    print()
    
    generate_wordcloud_data()
    print()
    
    generate_github_trend_data()
    print()
    
    print("✅ 所有模拟数据生成完成！")