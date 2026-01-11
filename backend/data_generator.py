#用于接入爬虫之前的数据处理

# backend/data_generator.py
import random
import json
from datetime import datetime, timedelta
import os

def generate_employment_trends():
    """生成就业趋势模拟数据"""
    careers = {
        'backend': {'base': 85, 'growth': (0.5, 2.5)},
        'frontend': {'base': 88, 'growth': (0.8, 2.8)},
        'fullstack': {'base': 82, 'growth': (1.0, 3.0)},
        'data_science': {'base': 90, 'growth': (0.7, 2.7)},
        'ai_engineer': {'base': 92, 'growth': (1.2, 3.2)}
    }
    
    years = [2020, 2021, 2022, 2023, 2024]
    
    result = {'years': years}
    for career, config in careers.items():
        rates = []
        current = config['base']
        for year in years:
            growth = random.uniform(*config['growth'])
            current = min(98, current + growth)  # 不超过98%
            rates.append(round(current, 1))
        result[career] = rates
    
    return result

def generate_salary_trends():
    """生成薪资趋势模拟数据"""
    careers = {
        'backend': {'base': 15000, 'growth': (0.08, 0.15)},
        'frontend': {'base': 14000, 'growth': (0.07, 0.14)},
        'fullstack': {'base': 18000, 'growth': (0.09, 0.16)},
        'data_science': {'base': 20000, 'growth': (0.10, 0.18)},
        'ai_engineer': {'base': 22000, 'growth': (0.12, 0.20)}
    }
    
    years = [2020, 2021, 2022, 2023, 2024]
    
    result = {'years': years}
    for career, config in careers.items():
        salaries = []
        current = config['base']
        for year in years:
            growth_rate = random.uniform(*config['growth'])
            current = int(current * (1 + growth_rate))
            salaries.append(current)
        result[career] = salaries
    
    return result

def save_data():
    """保存所有数据到文件"""
    os.makedirs('data', exist_ok=True)
    
    # 生成数据
    employment_data = generate_employment_trends()
    salary_data = generate_salary_trends()
    
    # 保存数据
    with open('data/employment_trends.json', 'w', encoding='utf-8') as f:
        json.dump({
            'data': employment_data,
            'updated_at': datetime.now().isoformat(),
            'note': '模拟数据 - 就业率趋势'
        }, f, ensure_ascii=False, indent=2)
    
    with open('data/salary_trends.json', 'w', encoding='utf-8') as f:
        json.dump({
            'data': salary_data,
            'updated_at': datetime.now().isoformat(),
            'note': '模拟数据 - 薪资趋势'
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[{datetime.now()}] ✅ 数据生成完成")
    print(f"  就业数据: {len(employment_data)} 个系列")
    print(f"  薪资数据: {len(salary_data)} 个系列")
    
    return {
        'employment': employment_data,
        'salary': salary_data
    }

if __name__ == '__main__':
    print("开始生成模拟数据...")
    data = save_data()
    print("数据已保存到 data/ 目录")