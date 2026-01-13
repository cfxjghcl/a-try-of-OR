import random
import json
from datetime import datetime
import os

def generate_wordcloud_data():
    """生成词云数据"""
    skills = [
        "Python", "Java", "JavaScript", "Vue.js", "React", "MySQL", "Redis",
        "Docker", "Kubernetes", "AWS", "微服务", "Spring Boot", "Flask",
        "FastAPI", "Git", "Linux", "TypeScript", "MongoDB", "PostgreSQL",
        "Elasticsearch", "Vue", "React Native", "小程序", "Node.js"
    ]
    
    # 生成权重（50-100之间）
    wordcloud_data = []
    for skill in skills:
        value = random.randint(50, 100)
        wordcloud_data.append({"name": skill, "value": value})   
    wordcloud_data.sort(key=lambda x: x['value'], reverse=True)

    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    # 保存
    result = {
        "data": wordcloud_data,
        "updated_at": datetime.now().isoformat(),
        "count": len(wordcloud_data)
    }
    with open('data/wordcloud.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"[{datetime.now()}] ✅ 词云数据已生成，共 {len(wordcloud_data)} 个词条")
    return result