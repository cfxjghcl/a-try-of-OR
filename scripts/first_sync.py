import pandas as pd
import pymysql
from opendigger_pycli.dataloaders import StarRepoDataloader

# 1. 预置 50 个热门 JavaScript 仓库
repo_list = [
    ('microsoft', 'vscode'), ('facebook', 'react'), ('nodejs', 'node'),
    ('vuejs', 'vue'), ('angular', 'angular'), ('twbs', 'bootstrap'),
    ('axios', 'axios'), ('lodash', 'lodash'), ('mrdoob', 'three.js'),
    ('webpack', 'webpack'), ('babel', 'babel'), ('prettier', 'prettier'),
    ('vercel', 'next.js'), ('nuxt', 'nuxt'), ('reduxjs', 'redux'),
    ('vuejs', 'vuex'), ('facebook', 'jest'), ('cypress-io', 'cypress'),
    ('storybookjs', 'storybook'), ('ionic-team', 'ionic'),
    ('electron', 'electron'), ('prisma', 'prisma'), ('nestjs', 'nest'),
    ('fastify', 'fastify'), ('expressjs', 'express'), ('socketio', 'socket.io'),
    ('mongoose', 'mongoose'), ('typeorm', 'typeorm'), ('sequelize', 'sequelize'),
    ('vercel', 'swr'), ('tanstack', 'query'), ('reduxjs', 'redux-toolkit'),
    ('pmndrs', 'zustand'), ('vueuse', 'vueuse'), ('vitejs', 'vite'),
    ('element-plus', 'element-plus'), ('ant-design', 'ant-design'),
    ('mui', 'material-ui'), ('tailwindlabs', 'tailwindcss'),
    ('rollup', 'rollup'), ('parcel-bundler', 'parcel'), ('gulpjs', 'gulp'),
    ('gruntjs', 'grunt'), ('mochajs', 'mocha'), ('jasmine', 'jasmine'),
    ('apollographql', 'apollo-server'), ('graphql', 'graphql-js'),
    ('redis', 'node-redis'), ('mysqljs', 'mysql'), ('knex', 'knex'),
    ('immerjs', 'immer'), ('recoiljs', 'recoil'), ('vuejs', 'router'),
    ('markedjs', 'marked'), ('xtermjs', 'xterm'), ('facebook', 'react')
]

loader = StarRepoDataloader()
records = []

for org, repo in repo_list:
    result = loader.load(org=org, repo=repo)
    if result.data and result.data.value:
        # 最近 30 天 star 增长 = 最近 30 条 value 求和
        recent_30 = sum(v.value for v in result.data.value[-30:])
        records.append({
            'org': org,
            'repo': repo,
            'star_growth': recent_30,
            # topics 暂无，先用 repo 名占位，后面再补
            'topics': [org + '/' + repo]
        })

# 转 DataFrame 并取前 20
df = pd.DataFrame(records).nlargest(20, 'star_growth')

# 拆 topics 并计数（repo 名当临时 topic）
skills = df['topics'].explode().value_counts().head(20).reset_index()
skills.columns = ['skill', 'heat']

# 3. 写库（改用 SQLAlchemy 引擎，pandas 12+ 强制要求）
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/jobviz?charset=utf8mb4')
skills.to_sql('tech_heat', engine, if_exists='replace', index=False)
print('INSERTED', len(skills), 'skills')


# ====== 同步函数 ======

def sync_data():
    """同步数据到数据库"""
    import pandas as pd
    import pymysql
    from opendigger_pycli.dataloaders import StarRepoDataloader
    from sqlalchemy import create_engine
    
    repo_list = [
        ('microsoft', 'vscode'), ('facebook', 'react'), ('nodejs', 'node'),
        ('vuejs', 'vue'), ('angular', 'angular'), ('twbs', 'bootstrap'),
        ('axios', 'axios'), ('lodash', 'lodash'), ('mrdoob', 'three.js'),
        ('webpack', 'webpack'), ('babel', 'babel'), ('prettier', 'prettier'),
        ('vercel', 'next.js'), ('nuxt', 'nuxt'), ('reduxjs', 'redux'),
        ('vuejs', 'vuex'), ('facebook', 'jest'), ('cypress-io', 'cypress'),
        ('storybookjs', 'storybook'), ('ionic-team', 'ionic'),
        ('electron', 'electron'), ('prisma', 'prisma'), ('nestjs', 'nest'),
        ('fastify', 'fastify'), ('expressjs', 'express'), ('socketio', 'socket.io'),
        ('mongoose', 'mongoose'), ('typeorm', 'typeorm'), ('sequelize', 'sequelize'),
        ('vercel', 'swr'), ('tanstack', 'query'), ('reduxjs', 'redux-toolkit'),
        ('pmndrs', 'zustand'), ('vueuse', 'vueuse'), ('vitejs', 'vite'),
        ('element-plus', 'element-plus'), ('ant-design', 'ant-design'),
        ('mui', 'material-ui'), ('tailwindlabs', 'tailwindcss'),
        ('rollup', 'rollup'), ('parcel-bundler', 'parcel'), ('gulpjs', 'gulp'),
        ('gruntjs', 'grunt'), ('mochajs', 'mocha'), ('jasmine', 'jasmine'),
        ('apollographql', 'apollo-server'), ('graphql', 'graphql-js'),
        ('redis', 'node-redis'), ('mysqljs', 'mysql'), ('knex', 'knex'),
        ('immerjs', 'immer'), ('recoiljs', 'recoil'), ('vuejs', 'router'),
        ('markedjs', 'marked'), ('xtermjs', 'xterm'), ('facebook', 'react')
    ]
    
    loader = StarRepoDataloader()
    records = []
    
    for org, repo in repo_list:
        result = loader.load(org=org, repo=repo)
        if result.data and result.data.value:
            recent_30 = sum(v.value for v in result.data.value[-30:])
            records.append({
                'org': org,
                'repo': repo,
                'star_growth': recent_30,
                'topics': [org + '/' + repo]
            })
    
    df = pd.DataFrame(records).nlargest(20, 'star_growth')
    skills = df['topics'].explode().value_counts().head(20).reset_index()
    skills.columns = ['skill', 'heat']
    
    engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/jobviz?charset=utf8mb4')
    skills.to_sql('tech_heat', engine, if_exists='replace', index=False)
    
    return len(skills)


if __name__ == '__main__':
    count = sync_data()
    print(f'INSERTED {count} skills')