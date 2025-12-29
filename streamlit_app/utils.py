# streamlit_app/utils.py
import streamlit as st
import pandas as pd
import json
import os, sys
import plotly.express as px
from collections import Counter
import re
from datetime import datetime, timezone # 确保导入 timezone
import jieba # 如果需要中文分词
from itertools import combinations # 用于共现分析
from collections import Counter
import pandas as pd
import numpy as np


# --- 路径定义 ---
# __file__ is streamlit_app/utils.py
# streamlit_app_dir is the directory containing utils.py
streamlit_app_dir = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT is the parent of streamlit_app_dir
PROJECT_ROOT = os.path.dirname(streamlit_app_dir)

CRAWLER_MODULE_DIR = os.path.join(PROJECT_ROOT, 'crawler', 'crawler')
DATA_DIR_INSIDE_CRAWLER = os.path.join(CRAWLER_MODULE_DIR, 'data')

JOBS_FILE = os.path.join(DATA_DIR_INSIDE_CRAWLER, 'jobs.json') # 或 jobs.jsonl
CITIES_FILE = os.path.join(DATA_DIR_INSIDE_CRAWLER, 'cities.json') # Not actively used in provided snippets, but path is defined
CATEGORIES_FILE = os.path.join(DATA_DIR_INSIDE_CRAWLER, 'positions.json') # Used in Skills/Majors page
DEFAULT_OPTIONS_FILE_PATH = os.path.join(DATA_DIR_INSIDE_CRAWLER, 'target_options.json') # Path to target_options.json

# --- 可选：加载停用词和自定义词典的路径 ---
ASSETS_DIR = os.path.join(streamlit_app_dir, 'assets') # assets folder inside streamlit_app
STOPWORDS_FILE = os.path.join(ASSETS_DIR, 'stopwords.txt')
USER_DICT_FILE = os.path.join(ASSETS_DIR, 'user_dict.txt')

# --- 技能关键词列表 (核心) ---
DEFAULT_SKILL_KEYWORDS = [
    # 编程语言 & 框架
    'Python', 'Java', 'Go', 'Golang', 'C++', 'C#', 'JavaScript', 'JS', 'TypeScript', 'TS', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Scala', 'Rust', 'Perl',
    'React', 'React.js', 'Vue', 'Vue.js', 'Angular', 'Angular.js', 'Node.js', 'Node', 'Express.js',
    'Spring', 'Spring Boot', 'Django', 'Flask', 'FastAPI', 'Ruby on Rails', '.NET', 'ASP.NET',
    # 数据库
    'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQLServer', 'NoSQL', 'SQLite', 'Cassandra', 'Elasticsearch',
    # 云计算 & DevOps
    'AWS', 'Azure', 'GCP', '阿里云', '腾讯云', '华为云', '云计算', '云原生', 'Cloud', 'OpenStack', 'Serverless',
    'Docker', 'Kubernetes', 'K8S', 'CI/CD', 'DevOps', 'Jenkins', 'Git', 'GitLab', 'GitHub', 'Ansible', 'Terraform', 'Puppet', 'Chef',
    # 操作系统 & Shell
    'Linux', 'Unix', 'Windows Server', 'Shell', 'Bash', 'PowerShell',
    # 大数据
    '数据分析', '数据挖掘', '大数据', 'Spark', 'Apache Spark', 'Hadoop', 'Flink', 'Apache Flink', 'Kafka', 'Apache Kafka',
    'Hive', 'HBase', 'Storm', 'Presto', 'ClickHouse', 'ETL',
    # AI & 机器学习
    '机器学习', '深度学习', 'AI', '人工智能', 'NLP', '自然语言处理', 'CV', '计算机视觉', '推荐算法', 'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn',
    # 前后端 & 测试 & 运维
    '算法', '架构', '架构师', '系统设计', '微服务',
    '前端', '后端', '全栈',
    '测试', '软件测试', '自动化测试', '性能测试', '安全测试', 'QA',
    '运维', 'SRE', '监控', '日志',
    # 职位角色 & 软技能 (部分也可能是关键词)
    '产品经理', '项目经理', 'PM', 'PO',
    '运营', '市场', '销售', 'BD', '客服',
    'HR', '人事', '招聘',
    '行政', '财务', '会计', '审计', '法务', '风控',
    # 设计 & 游戏
    'UI', 'UX', '用户体验', '交互设计', '视觉设计', '设计', '平面设计',
    '游戏开发', 'UE4', 'UE5', 'Unreal Engine', 'Unity', 'U3D', 'Cocos',
    # 移动开发
    '移动开发', 'iOS', 'Android', 'Flutter', 'React Native', '小程序', '鸿蒙', 'HarmonyOS',
    # 其他技术 & 领域
    '嵌入式', '物联网', 'IoT', '芯片', 'FPGA', 'ASIC', '驱动开发', '固件',
    '网络安全', '信息安全', '密码学', '渗透测试',
    '区块链', '智能合约',
    '写作', '编辑', '文案', '翻译',
    '医学', '药学', '生物', '化学',
    # 通用专业/领域词 (也可能出现在 major_required)
    '计算机', '软件工程', '通信工程', '电子信息', '自动化', '机械', '数学', '统计', '物理', '金融', '经济'
]

DEFAULT_COMPANY_TAGS = [
    "五险一金", "年底双薪", "绩效奖金", "带薪年假", "弹性工作",
    "定期体检", "补充医疗保险", "交通补贴", "餐饮补贴", "通讯补贴",
    "节日福利", "专业培训", "晋升空间大", "扁平化管理", "技术氛围好",
    "团队优秀", "股票期权", "免费班车", "健身房", "零食下午茶",
    "提供住宿", "带薪年假", "绩效奖金", "节日礼物", "定期体检", "午餐补贴"
    # ... add more standard tags
]

PREPROCESS_SCALES_ORDERED = ["1-49人", "50-99人", "100-499人", "500-999人", "1000-9999人", "10000+人", "未知"]
PREPROCESS_DEGREES_ORDERED = ['学历不限', '其他', '初中及以下', '中专', '中技', '中专/中技', '高中', '大专', '本科', '硕士', '博士', '博士后']
PREPROCESS_WORK_YEAR_LABELS = ['经验不限', '1年以内', '1-3年', '3-5年', '5-10年', '10年以上']

# 对关键词进行预处理，例如全部转为小写，并去重，但保留原始大小写用于映射
# 构建一个映射：小写关键词 -> 原始大小写关键词 (选择第一个出现的原始大小写)
LOWER_TO_ORIGINAL_SKILL_MAP = {kw.lower(): kw for kw in reversed(DEFAULT_SKILL_KEYWORDS)} # reversed确保短词不会覆盖长词的小写形式
UNIQUE_LOWER_SKILLS = list(LOWER_TO_ORIGINAL_SKILL_MAP.keys())

# 为去重后的小写技能构建正则表达式 (按长度降序排列，优先匹配长词)
SORTED_UNIQUE_LOWER_SKILLS_FOR_REGEX = sorted(UNIQUE_LOWER_SKILLS, key=len, reverse=True)

SKILL_REGEX_PATTERNS = {}
for lower_skill in SORTED_UNIQUE_LOWER_SKILLS_FOR_REGEX:
    original_kw = LOWER_TO_ORIGINAL_SKILL_MAP[lower_skill]
    pattern_str = ""
    # 对 original_kw 进行 re.escape 是必要的，特别是包含特殊字符如 C++ 时
    escaped_kw = re.escape(original_kw)
    if re.search(r'[\u4e00-\u9fff]', original_kw): # 中文或中英混合
        pattern_str = escaped_kw # 精确匹配
    elif original_kw.isalnum() or (original_kw.isascii() and not any(c in '+*#.' for c in original_kw)): # 简单英文/数字 (避免对C++, C#等用\b)
        pattern_str = r'\b' + escaped_kw + r'\b'
    else: # 包含特殊符号的，如 C++, C#, Node.js, React.js
        pattern_str = escaped_kw # 精确匹配，因为\b可能不适用
    SKILL_REGEX_PATTERNS[original_kw] = re.compile(pattern_str, re.IGNORECASE)

# CRAWLER_SETTINGS_FILE = os.path.join(PROJECT_ROOT, 'crawler', 'crawler', 'settings.py') # Not actively used for options loading

TAGS_TO_EXCLUDE_GENERIC = [
    '其他', '其它', '公司提供', '员工福利', '福利待遇', '待遇从优',
    '详情面议', '面议', '工作餐', '包吃', '包住', '包吃住', '食宿补贴', '住宿补贴', # These can be too generic
    '班车', '交通方便', '地铁沿线', '不加班', '偶尔加班', # These are good but maybe too many if not top-level
    # Add more generic or unhelpful tags here
]

# Compile a regex for characters to remove or replace in tags
NON_ALPHANUMERIC_CHINESE_REGEX = re.compile(r'[^\w\s\u4e00-\u9fff\+\#\.\-]') # Allows alphanumeric, whitespace, CJK, +, #, ., -

def clean_tag(tag):
    """Cleans an individual tag."""
    if not isinstance(tag, str):
        tag = str(tag)
    tag = tag.strip().lower() # Lowercase and strip whitespace
    tag = NON_ALPHANUMERIC_CHINESE_REGEX.sub('', tag) # Remove unwanted characters
    # Optional: Replace multiple spaces with a single space
    tag = re.sub(r'\s+', ' ', tag).strip()
    return tag

def get_cleaned_company_tags_from_data(df_jobs, top_n=50, min_freq=5):
    """
    Extracts, cleans, and gets frequent company tags from the 'tags_list' column.
    """
    if 'tags_list' not in df_jobs.columns:
        return []

    all_tags_flat = []
    for tag_tuple in df_jobs['tags_list'].dropna():
        if isinstance(tag_tuple, (list, tuple)):
            for tag in tag_tuple:
                cleaned = clean_tag(tag)
                if cleaned and cleaned not in TAGS_TO_EXCLUDE_GENERIC and len(cleaned) > 1 and len(cleaned) < 15: # Basic length filter
                    all_tags_flat.append(cleaned)

    if not all_tags_flat:
        return []

    tag_counts = Counter(all_tags_flat)
    
    # Get tags that meet min_freq and then take top_n from those
    frequent_tags = [tag for tag, count in tag_counts.items() if count >= min_freq]
    
    # If still too many after min_freq, take top_n based on original counts
    if len(frequent_tags) > top_n:
        # Sort all tags by frequency to pick the true top_n from those meeting min_freq
        # This ensures we don't just pick alphabetically if many have the same min_freq
        sorted_frequent_tags = sorted(frequent_tags, key=lambda t: tag_counts[t], reverse=True)
        return sorted_frequent_tags[:top_n]
    elif frequent_tags: # If fewer than top_n but some exist
        return sorted(frequent_tags, key=lambda t: tag_counts[t], reverse=True) # Sort them by freq
    
    # Fallback if min_freq filters out too much, just take top_n of all cleaned tags
    # This might happen with sparse data
    if not frequent_tags and tag_counts:
        print(f"Warning: min_freq={min_freq} for company tags filtered out all tags. Falling back to top_n of all cleaned tags.")
        return [tag for tag, count in tag_counts.most_common(top_n)]

    return []

# --- Helper function for major standardization ---
@st.cache_data
def _load_standard_majors(target_options_path=DEFAULT_OPTIONS_FILE_PATH):
    standard_majors_lower_sorted = []
    try:
        if os.path.exists(target_options_path):
            with open(target_options_path, 'r', encoding='utf-8') as f:
                target_options_data = json.load(f)
            
            college_major_list = target_options_data.get('collegmajor') 
            
            if isinstance(college_major_list, list):
                raw_majors = []
                for item in college_major_list:
                    if isinstance(item, dict) and 'name' in item and isinstance(item['name'], str):
                        raw_majors.append(item['name'])
                
                if raw_majors:
                    valid_majors = [m.lower() for m in raw_majors if m.strip()]
                    standard_majors_lower_sorted = sorted(list(set(valid_majors)), key=len, reverse=True)
                    if not standard_majors_lower_sorted and streamlit_app_dir: # Check if in Streamlit context
                        st.warning(f"'{os.path.basename(target_options_path)}' yielded no valid major names after processing.")
                elif streamlit_app_dir:
                    st.warning(f"No major names extracted from 'collegmajor' in '{os.path.basename(target_options_path)}'.")
            elif streamlit_app_dir:
                st.warning(f"'collegmajor' key in '{os.path.basename(target_options_path)}' is not a list or is missing.")
        elif streamlit_app_dir:
            st.warning(f"Standard majors file '{os.path.basename(target_options_path)}' not found. Major processing will be limited.")
    except json.JSONDecodeError:
        if streamlit_app_dir: st.error(f"Error decoding JSON from '{os.path.basename(target_options_path)}'.")
    except Exception as e:
        if streamlit_app_dir: st.error(f"Error loading majors from '{os.path.basename(target_options_path)}': {e}")
    
    return standard_majors_lower_sorted

STOPWORDS = {"的", "与", "和", "等", "及", "中", "具有", "能力", "经验", "负责", "熟练", "掌握", "进行", "相关", "优先", "良好"} # Add more

def extract_skills_advanced(text_series, predefined_skills=None, min_skill_len=2):
    if predefined_skills is None:
        predefined_skills = set() # PREDEFINED_SKILLS loaded globally or passed

    def extract_from_text(text):
        if pd.isna(text) or not isinstance(text, str) or not text.strip():
            return tuple()
        
        text_lower = text.lower()
        found_skills = set()

        # 1. Match predefined skills (case-insensitive)
        for skill in predefined_skills:
            if skill in text_lower: # Simple substring match for predefined
                found_skills.add(skill.strip()) # Use original casing from dict if desired, or always lower

        # 2. Use Jieba for other terms (optional, can be noisy without good post-filtering)
        # words = jieba.lcut(text)
        # for word in words:
        #     word_cleaned = word.strip().lower()
        #     if len(word_cleaned) >= min_skill_len and word_cleaned not in STOPWORDS and not word_cleaned.isnumeric():
        #         # Add more filtering here: e.g., check if it's a noun, part of an N-gram, etc.
        #         # This part can become complex to get good results without a dictionary
        #         if any(char.isalpha() for char in word_cleaned): # crude filter for things that might be skills
        #             found_skills.add(word_cleaned)
        
        return tuple(sorted(list(found_skills)))

    return text_series.apply(extract_from_text)

def get_word_counts_from_list_column(df, column_name, top_n=None, min_freq=1): # Added min_freq with default
    """
    Counts occurrences of items within a column containing lists/tuples of items.
    Filters by minimum frequency before selecting top N.
    """
    if column_name not in df.columns:
        # st.warning(f"Column '{column_name}' not found in DataFrame.") # Optional warning
        return pd.DataFrame(columns=['item', 'count'])

    # Ensure the column is not all NaNs or empty lists/tuples
    if df[column_name].isnull().all() or not df[column_name].apply(lambda x: isinstance(x, (list, tuple)) and len(x) > 0).any():
        # st.info(f"Column '{column_name}' is empty or contains no valid lists/tuples of items.") # Optional info
        return pd.DataFrame(columns=['item', 'count'])

    all_items = []
    for item_list in df[column_name].dropna(): # Drop NaNs before iterating
        if isinstance(item_list, (list, tuple)):
            all_items.extend([item for item in item_list if isinstance(item, str) and item.strip()]) # Add only non-empty strings
        # elif isinstance(item_list, str): # If some rows have single strings instead of lists
            # all_items.append(item_list) 
            
    if not all_items:
        return pd.DataFrame(columns=['item', 'count'])

    item_counts = Counter(all_items)
    
    # Filter by min_freq
    filtered_counts = {item: count for item, count in item_counts.items() if count >= min_freq}
    
    if not filtered_counts:
        return pd.DataFrame(columns=['item', 'count'])

    # Convert to DataFrame
    df_counts = pd.DataFrame(list(filtered_counts.items()), columns=['item', 'count'])
    df_counts = df_counts.sort_values(by='count', ascending=False).reset_index(drop=True)

    if top_n:
        return df_counts.head(top_n)
    return df_counts

def _map_to_standard_major(major_text, standard_majors_list):
    """
    Maps a raw major text to a standard major from the list.
    major_text: Raw major string, expected to be lowercased and stripped.
    standard_majors_list: List of standard majors, lowercased, sorted by length desc.
    """
    if not major_text or major_text == '未知': 
        return '未知'
    
    for std_major in standard_majors_list:
        if std_major in major_text: 
            return std_major 
    return '其他专业' 
# --- End of Helper function for major standardization ---


@st.cache_data
def load_scrapy_default_targets():
    # 定义所有期望的键和它们对应的 "不限" 选项的显示名称及默认结构
    default_options_config = {
        "cities": {"default_name": "🌍 不限省份/地区", "json_keys": ["provinces", "citys"], "options": []},
        "categories": {"default_name": "📚 不限类别", "json_keys": ["jobcategoryItems", "categories"], "options": []},
        "industries": {"default_name": "🏭 不限行业", "json_keys": ["industriesNew", "mainindustries"], "options": []},
        "workExperiences": {
            "default_name": "⏳ 不限工作经验",
            "json_keys": ["workExperiences"],
            "options": [{"name": label, "code": str(idx)} for idx, label in enumerate(PREPROCESS_WORK_YEAR_LABELS)]
        },
        "degrees": {
            "default_name": "🎓 不限学历",
            "json_keys": ["degrees", "educationLevels"],
            "options": [{"name": label, "code": str(idx)} for idx, label in enumerate(PREPROCESS_DEGREES_ORDERED)]
        },
        "scales": {
            "default_name": "⚖️ 不限公司规模",
            "json_keys": ["scales", "companyScales"],
             # 使用 PREPROCESS_SCALES_ORDERED，但移除 "未知" 因为用户通常不按 "未知" 筛选
            "options": [{"name": label, "code": str(idx)} for idx, label in enumerate(cat for cat in PREPROCESS_SCALES_ORDERED if cat != "未知")]
        },
        "corpProps": { # 这个在你的 JSON 里有
            "default_name": "🏛️ 不限公司性质",
            "json_keys": ["corpProps"],
            "options": [] # 将由 JSON 文件填充
        }
    }

    targets = {}
    # 1. 为所有期望的键使用 default_options_config 中的配置进行初始化
    for key, config in default_options_config.items():
        # 初始列表包含 "不限" 选项
        current_key_options = [{"code": "", "name": config["default_name"]}]
        # 如果 config 中有预定义的 fallback options，追加它们
        if config["options"]:
            # 避免重复添加与 "不限" 名称相同的项（如果fallback options里包含了它）
            for option_item in config["options"]:
                if option_item["name"] != config["default_name"]:
                    current_key_options.append(option_item)
        targets[key] = current_key_options

    # 2. 尝试从 target_options.json 加载并覆盖/合并
    if os.path.exists(DEFAULT_OPTIONS_FILE_PATH):
        try:
            with open(DEFAULT_OPTIONS_FILE_PATH, 'r', encoding='utf-8') as f:
                loaded_options_from_file = json.load(f)

            for key, config in default_options_config.items():
                loaded_list_for_key = None
                for json_key_attempt in config["json_keys"]:
                    if json_key_attempt in loaded_options_from_file and \
                       isinstance(loaded_options_from_file[json_key_attempt], list) and \
                       loaded_options_from_file[json_key_attempt]:
                        loaded_list_for_key = loaded_options_from_file[json_key_attempt]
                        print(f"Info: Successfully loaded '{json_key_attempt}' for key '{key}' from JSON.")
                        break
                
                if loaded_list_for_key:
                    valid_items_from_json = []
                    # JSON 中的 "不限" 选项是否已找到并处理（以避免重复添加）
                    default_option_handled_from_json = False

                    for item_json in loaded_list_for_key:
                        if isinstance(item_json, dict) and item_json.get('name') and 'code' in item_json:
                            name_val = str(item_json['name']).strip()
                            code_val = str(item_json['code'])
                            
                            # 如果JSON项是 "不限" 选项
                            if name_val == config["default_name"]:
                                # 使用JSON中的code（如果它不是空），否则保持code为""
                                valid_items_from_json.insert(0, {"name": name_val, "code": code_val if code_val else ""})
                                default_option_handled_from_json = True
                                continue # 跳过，避免重复添加到末尾

                            processed_item = None
                            if key == "cities" and "citys" in config["json_keys"] and "level" in item_json:
                                if str(item_json.get("level")).lower() in ["省", "直辖市", "自治区", "特别行政区"]:
                                     processed_item = {"name": name_val, "code": code_val}
                            # 对于 corpProps，其 JSON 中的 "不限" 可能有 code，也可能没有
                            elif key == "corpProps" and name_val == "不限" and code_val == "": # 这是 utils/app.py 期望的
                                valid_items_from_json.insert(0, {"name": config["default_name"], "code": ""}) # 使用规范的 "不限"
                                default_option_handled_from_json = True
                                continue
                            else:
                                processed_item = {"name": name_val, "code": code_val}
                            
                            if processed_item:
                                valid_items_from_json.append(processed_item)
                    
                    if valid_items_from_json:
                        # 如果JSON加载成功，用JSON的数据（但确保 "不限" 在最前面且规范）
                        final_list_for_key = []
                        if not default_option_handled_from_json:
                            final_list_for_key.append({"code": "", "name": config["default_name"]})
                        
                        # 添加JSON中非 "不限" 的项，并去重（基于name）
                        seen_names = {config["default_name"]} if default_option_handled_from_json else set()
                        if default_option_handled_from_json and valid_items_from_json[0]["name"] == config["default_name"]:
                            final_list_for_key.append(valid_items_from_json[0]) # 添加已处理的 JSON "不限"
                            start_index_json = 1
                        else:
                            start_index_json = 0

                        for vi in valid_items_from_json[start_index_json:]:
                            if vi["name"] not in seen_names:
                                final_list_for_key.append(vi)
                                seen_names.add(vi["name"])
                        targets[key] = final_list_for_key
                # 如果 loaded_list_for_key 为 None 或处理后 valid_items_from_json 为空，
                # targets[key] 会保持其初始化的值 (包含 "不限" 和可能的硬编码 fallback options)
        
        except json.JSONDecodeError:
            msg = f"解析 JSON 文件 '{os.path.basename(DEFAULT_OPTIONS_FILE_PATH)}' 失败。将使用内置默认爬取选项。"
            if 'streamlit' in sys.modules and hasattr(st, 'warning'): st.warning(msg)
            else: print(f"Warning: {msg}")
        except Exception as e:
            msg = f"加载爬取选项时发生错误: {e}。将使用内置默认爬取选项。"
            if 'streamlit' in sys.modules and hasattr(st, 'warning'): st.warning(msg)
            else: print(f"Warning: {msg}")
    else:
        msg = f"爬取选项文件 '{os.path.basename(DEFAULT_OPTIONS_FILE_PATH)}' 未找到。将使用内置默认爬取选项。"
        if 'streamlit' in sys.modules and hasattr(st, 'warning'): st.warning(msg)
        else: print(f"Warning: {msg}")
        # 此时 targets 字典已经包含了所有键的默认 "不限" + fallback options

    # 3. 最后，再次确保每个列表的 "不限" 选项是唯一的，并且格式正确，且位于最前
    for key, config in default_options_config.items():
        current_list = targets.get(key, []) 
        
        final_unique_list = []
        default_option = {"code": "", "name": config["default_name"]}
        
        final_unique_list.append(default_option) # 强制 "不限" 在第一位
        
        seen_names_in_final = {config["default_name"]} # 记录已加入 final_list 的 name

        for item in current_list:
            item_name = item.get("name")
            # 跳过与已添加的规范 "不限" 选项 name 相同的项 (因为 "不限" 已被强制加入)
            if item_name == config["default_name"]:
                continue
            
            if item_name and item_name not in seen_names_in_final:
                 # 确保 item 是字典且有 code
                if isinstance(item, dict) and 'code' in item:
                    final_unique_list.append(item)
                    seen_names_in_final.add(item_name)
        
        targets[key] = final_unique_list
        
    return targets

@st.cache_data
def load_stopwords(filepath=STOPWORDS_FILE):
    stopwords = set()
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                stopwords.add(line.strip())
    else:
        stopwords = {"的", "了", "和", "与", "或", "也", "等", "在", "是", "我们", "以及", " ", "\n", "\t",
                     "公司", "有限", "科技", "股份", "集团", "企业", "北京", "上海", "深圳", "广州", 
                     "要求", "负责", "相关", "工作", "经验", "优先", "能力", "熟悉", "掌握", "岗位", "职责"}
    return stopwords

def parse_and_map_majors_from_text_util(text, official_names_set_local): # Renamed to avoid conflict if copied
    if pd.isna(text) or not isinstance(text, str): return tuple()
    text_cleaned = str(text).strip().lower()
    no_specific_major_phrases = ['不限专业', '不限', '专业不限', '无', '相关专业', '不要求']
    if not text_cleaned or any(phrase in text_cleaned for phrase in no_specific_major_phrases):
        return tuple()
    text_cleaned_no_prefix = re.sub(r'【.*?】', '', text_cleaned) 
    text_cleaned_no_prefix = re.sub(r'（.*?）', '', text_cleaned_no_prefix) 
    text_cleaned_no_prefix = re.sub(r'\(.*?\)', '', text_cleaned_no_prefix)
    found_official_majors = set()
    for official_major in official_names_set_local:
        if re.search(r'\b' + re.escape(official_major) + r'\b', text_cleaned_no_prefix):
            found_official_majors.add(official_major)
    if not found_official_majors:
        delimiters = r'[、,\s，；或/及]+' 
        parts = [p.strip() for p in re.split(delimiters, text_cleaned_no_prefix) if p.strip()]
        for part in parts:
            if part in official_names_set_local:
                found_official_majors.add(part)
    return tuple(sorted(list(found_official_majors)))

# --- REMOVE THE FIRST preprocess_jobs_data DEFINITION ---
# # --- Your existing preprocess_jobs_data function ---
# @st.cache_data
# def preprocess_jobs_data(df_jobs_raw): # 确保这个函数在这里
#     if df_jobs_raw.empty:
#         return pd.DataFrame()
#     df = df_jobs_raw.copy()

#     # 确保所有必要的列都存在，并进行类型转换和填充
#     required_cols_defaults = {
#         'job_id': None, 'job_name': '未知职位', 'job_catory': '未知类别', 'job_industry': '未知行业',
#         'high_month_pay': 0.0, 'low_month_pay': 0.0, 'publish_date': None, 'update_date': None,
#         'company_name': '未知公司',
#         'area_code_name': '未知地区',
#         'prinvce_code_nme': '未知省份',
#         'company_scale': '未知规模',
#         'degree_name': '不限', 'major_required': '', 'company_property': '未知性质',
#         'company_tags': '', 'source_url': '#', 'head_count': 1
#     }
#     for col, default_val in required_cols_defaults.items():
#         if col not in df.columns:
#             df[col] = default_val
#         elif col in ['major_required', 'company_tags', 'job_name', 'job_catory', 'job_industry',
#                      'company_name', 'area_code_name', 'prinvce_code_nme', 'company_scale',
#                      'degree_name', 'company_property']:
#             if default_val is not None:
#                  df[col] = df[col].fillna(str(default_val))
#             df[col] = df[col].astype(str)

#     for col in ['low_month_pay', 'high_month_pay']:
#         df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

#     df['avg_month_pay'] = df.apply(
#         lambda row: (row['low_month_pay'] + row['high_month_pay']) / 2 if row['low_month_pay'] > 0 and row['high_month_pay'] > 0 else \
#                     row['high_month_pay'] if row['high_month_pay'] > 0 else \
#                     row['low_month_pay'] if row['low_month_pay'] > 0 else 0.0,
#         axis=1
#     )

#     for date_col in ['publish_date', 'update_date']:
#         if date_col in df.columns:
#             df[date_col] = pd.to_numeric(df[date_col], errors='coerce')
#             df[f'{date_col}_dt'] = pd.to_datetime(df[date_col], unit='ms', errors='coerce', utc=True)
    
#     location_suffixes_to_remove = ['市', '省', '自治区', '特别行政区', '地区', '盟', '州', '县', '区', '回族', '维吾尔', '壮族', '藏族', '苗族', '土家族', '布依族', '侗族', '瑶族', '白族', '哈尼族', '傣族', '傈僳族', '彝族']
#     temp_city_clean = df['area_code_name'].astype(str)
#     for suffix in location_suffixes_to_remove:
#         temp_city_clean = temp_city_clean.str.replace(suffix, '', regex=False)
#     df['city_clean'] = temp_city_clean.str.strip()
#     city_empty_mask = (df['city_clean'] == '') | (df['area_code_name'] == required_cols_defaults['area_code_name'])
#     df.loc[city_empty_mask, 'city_clean'] = df.loc[city_empty_mask, 'area_code_name'].astype(str).str.strip()
#     df.loc[df['city_clean'] == '', 'city_clean'] = required_cols_defaults['area_code_name']

#     temp_province_clean = df['prinvce_code_nme'].astype(str)
#     for suffix in location_suffixes_to_remove:
#         temp_province_clean = temp_province_clean.str.replace(suffix, '', regex=False)
#     df['province_clean'] = temp_province_clean.str.strip()
#     province_empty_mask = (df['province_clean'] == '') | (df['prinvce_code_nme'] == required_cols_defaults['prinvce_code_nme'])
#     df.loc[province_empty_mask, 'province_clean'] = df.loc[province_empty_mask, 'prinvce_code_nme'].astype(str).str.strip()
#     df.loc[df['province_clean'] == '', 'province_clean'] = required_cols_defaults['prinvce_code_nme']
    
#     def clean_scale(scale_str):
#         if pd.isna(scale_str) or not isinstance(scale_str, str): return "未知"
#         scale_str = scale_str.strip()
#         if not scale_str or scale_str.lower() in ['nan', 'none', 'null', '未知']: return "未知"
#         if "以上" in scale_str:
#             match = re.search(r'(\d+)', scale_str)
#             return f"{match.group(1)}+人" if match else scale_str
#         return scale_str
#     df['company_scale_cleaned'] = df['company_scale'].apply(clean_scale)
#     scale_order = ["1-49人", "50-99人", "100-499人", "500-999人", "1000-9999人", "10000+人", "未知"]
#     df['company_scale_cat'] = pd.Categorical(df['company_scale_cleaned'], categories=scale_order, ordered=True)

#     degree_order = ['不限', '初中及以下','中专/中技','高中','大专','本科','硕士','博士','博士后','本科及以上', '硕士及以上','学历不限']
#     df['degree_name_cat'] = pd.Categorical(df['degree_name'].fillna('不限').astype(str), categories=degree_order, ordered=True)

#     common_none_terms = ['none', 'null', '无', '']
#     standard_majors_list = _load_standard_majors()
#     df['major_required_cleaned'] = df['major_required'].astype(str).str.lower().str.strip()
#     df['major_required_cleaned'].replace(common_none_terms + ['不限', '未知'], '未知', inplace=True)
#     if standard_majors_list:
#         df['processed_major'] = df['major_required_cleaned'].apply(
#             lambda x: _map_to_standard_major(x, standard_majors_list)
#         )
#     else:
#         df['processed_major'] = df['major_required_cleaned'].apply(lambda x: '其他专业' if x and x != '未知' else '未知')

#     def split_raw_majors(text):
#         if not text or text.lower().strip() in common_none_terms + ['不限', '未知']: return tuple()
#         text_cleaned = text.replace("或相关专业", " 相关专业").replace("及相关专业", " 相关专业")
#         delimiters = r"[\s,，、;/]+"
#         raw_majors = [m.strip() for m in re.split(delimiters, text_cleaned) if m.strip() and m.strip().lower() not in common_none_terms and len(m.strip()) > 1]
#         return tuple(m for m in raw_majors if m)
#     df['majors_list'] = df['major_required'].apply(split_raw_majors)

#     df['company_tags'] = df['company_tags'].astype(str).fillna('')
#     df['tags_list'] = df['company_tags'].apply(
#         lambda x: tuple(t.strip() for t in x.split('，') if t.strip() and t.strip().lower() not in common_none_terms)
#         if x.strip() and x.strip().lower() not in common_none_terms else tuple()
#     )
    
#     # --- 创建用于技能提取的组合文本列 ---
#     df['job_name_and_major_text'] = df['job_name'].fillna('') + " " + df['major_required'].fillna('')
#     # 可以在这里加上 job_description (如果你的 JSON 中有这个字段的话)
#     # if 'job_description' in df.columns:
#     #     df['job_name_and_major_text'] += " " + df['job_description'].fillna('')
        
#     return df
# --- END OF REMOVAL ---


@st.cache_data
def extract_skills_from_text_series(
    text_series: pd.Series,
    skill_regex_patterns: dict # 传入预编译的 skill_original_case -> regex_pattern 映射
) -> pd.Series:
    """
    从给定的文本 Series 中提取技能。
    返回一个 Series，每行是一个包含该行文本中识别出的技能（原始大小写）的元组。
    """
    if text_series.empty:
        return pd.Series([tuple() for _ in range(len(text_series))], index=text_series.index, dtype=object)

    def find_skills_in_one_text(text_content: str):
        if pd.isna(text_content) or not text_content.strip():
            return tuple()
        
        # 使用预编译的正则表达式进行匹配
        # 这里的 skill_regex_patterns 应该是 {original_skill_name: compiled_regex_object}
        found_skills_set = set()
        for original_skill, compiled_pattern in skill_regex_patterns.items():
            if compiled_pattern.search(text_content): # re.IGNORECASE 已在编译时设置
                found_skills_set.add(original_skill)
        return tuple(sorted(list(found_skills_set)))

    return text_series.astype(str).apply(find_skills_in_one_text)


@st.cache_data
def get_skill_frequency(
    df_with_extracted_skills: pd.DataFrame, # DataFrame 包含一个技能元组列表的列
    skill_list_column: str, # 存技能元组列表的列名，例如 'extracted_skills'
    top_n: int = 20
) -> pd.DataFrame:
    """
    计算技能列表中各项技能的出现频率。
    """
    if df_with_extracted_skills.empty or skill_list_column not in df_with_extracted_skills.columns:
        return pd.DataFrame(columns=['skill', 'count'])

    all_skills_flat_list = []
    for skills_tuple in df_with_extracted_skills[skill_list_column].dropna():
        if isinstance(skills_tuple, tuple) and skills_tuple: # 确保是元组且非空
            all_skills_flat_list.extend(list(skills_tuple))
            
    if not all_skills_flat_list:
        return pd.DataFrame(columns=['skill', 'count'])
        
    skill_counts = Counter(all_skills_flat_list)
    top_skills = skill_counts.most_common(top_n)
    
    return pd.DataFrame(top_skills, columns=['skill', 'count'])


@st.cache_data
def get_skill_cooccurrence_optimized(
    df_with_extracted_skills: pd.DataFrame, # DataFrame 包含一个技能元组列表的列
    skill_list_column: str, # 存技能元组列表的列名，例如 'extracted_skills'
    top_n_cooc_pairs: int = 15,
    min_cooc_frequency: int = 2,
    min_skills_in_one_text: int = 2 # 这个参数现在由 skill_list_column 的内容长度决定
) -> pd.DataFrame:
    """
    计算技能列表中各项技能的共现频率。
    df_with_extracted_skills: DataFrame, 其中一列 (skill_list_column) 包含已提取的技能元组。
    """
    if df_with_extracted_skills.empty or skill_list_column not in df_with_extracted_skills.columns:
        return pd.DataFrame(columns=['skill_pair', 'count'])

    cooccurrence_counts = Counter()
    processed_texts_count = 0
    texts_meeting_min_skills_criteria = 0

    for skills_tuple in df_with_extracted_skills[skill_list_column].dropna():
        processed_texts_count +=1
        if isinstance(skills_tuple, tuple) and len(skills_tuple) >= min_skills_in_one_text:
            texts_meeting_min_skills_criteria +=1
            # 技能已经是原始大小写，并且已去重 (因为 extract_skills_from_text_series 返回 set转换的元组)
            # 直接对元组内的技能进行组合
            for combo in combinations(sorted(list(skills_tuple)), 2): # sorted确保顺序一致
                cooccurrence_counts[combo] += 1
    
    # Debugging (可以在 Streamlit 页面之外或临时取消注释)
    # print(f"DEBUG cooc_opt (from list col): Processed {processed_texts_count} skill lists.")
    # print(f"DEBUG cooc_opt (from list col): {texts_meeting_min_skills_criteria} lists had >= {min_skills_in_one_text} skills.")
    # print(f"DEBUG cooc_opt (from list col): Total unique co-occurring pairs found (before filtering): {len(cooccurrence_counts)}")
    # if cooccurrence_counts:
    #     print(f"DEBUG cooc_opt (from list col): Top 5 raw cooccurrence_counts: {dict(cooccurrence_counts.most_common(5))}")

    if not cooccurrence_counts:
        return pd.DataFrame(columns=['skill_pair', 'count'])

    frequent_cooccurrences = {
        pair: count for pair, count in cooccurrence_counts.items() if count >= min_cooc_frequency
    }
    if not frequent_cooccurrences:
        return pd.DataFrame(columns=['skill_pair', 'count'])

    top_common_combos = Counter(frequent_cooccurrences).most_common(top_n_cooc_pairs)
    if not top_common_combos:
        return pd.DataFrame(columns=['skill_pair', 'count'])

    combo_df = pd.DataFrame(top_common_combos, columns=['skill_pair_tuple', 'count'])
    combo_df['skill_pair'] = combo_df['skill_pair_tuple'].apply(lambda x: f"{x[0]} & {x[1]}")
    
    return combo_df[['skill_pair', 'count']].sort_values(by='count', ascending=False)


@st.cache_data
def extract_terms_jieba(text_series, top_n=25, custom_dict_path=USER_DICT_FILE, stopwords_path=STOPWORDS_FILE, min_len=2, min_freq=2):
    if text_series.empty:
        return pd.DataFrame(columns=['term', 'count'])

    if custom_dict_path and os.path.exists(custom_dict_path):
        try:
            jieba.load_userdict(custom_dict_path)
        except Exception as e:
            if streamlit_app_dir: st.warning(f"Could not load user dictionary: {e}")
    
    stopwords = load_stopwords(stopwords_path)
    all_words = []
    
    full_text = " ".join(text_series.dropna().astype(str).tolist())
    if not full_text.strip():
        return pd.DataFrame(columns=['term', 'count'])

    words = jieba.lcut(full_text, cut_all=False)
    for word in words:
        word = word.strip().lower()
        if word and word not in stopwords and len(word) >= min_len and \
           not word.isdigit() and not (len(word)==1 and 'a' <= word <= 'z'):
            all_words.append(word)
    
    if not all_words:
        return pd.DataFrame(columns=['term', 'count'])
        
    word_counts = Counter(all_words)
    if min_freq > 1:
        filtered_word_counts = {word: count for word, count in word_counts.items() if count >= min_freq}
        common_terms = Counter(filtered_word_counts).most_common(top_n)
    else:
        common_terms = word_counts.most_common(top_n)
    
    return pd.DataFrame(common_terms, columns=['term', 'count'])

"""
@st.cache_data
def get_skill_cooccurrence_optimized(
    df: pd.DataFrame,
    text_column_to_scan: str,
    skill_keywords_list: list,
    top_n_cooc_pairs: int = 15,
    min_cooc_frequency: int = 2, # 一个技能对至少要共现这么多次才被考虑
    min_skills_in_one_text: int = 2 # 一条文本中至少要识别出这么多技能才进行组合
) -> pd.DataFrame:
    
    计算技能在指定文本列中的共现频率。

    Args:
        df: 包含文本数据的 DataFrame。
        text_column_to_scan: DataFrame 中待扫描的文本列名。
        skill_keywords_list: 用于识别技能的关键词列表。
        top_n_cooc_pairs: 返回的热门共现技能对数量。
        min_cooc_frequency: 共现对的最小频率阈值。
        min_skills_in_one_text: 单个文本中需要识别出的最小技能数才进行共现计算。

    Returns:
        一个 DataFrame，包含 'skill_pair' 和 'count' 列。
    
    if df.empty or text_column_to_scan not in df.columns or not skill_keywords_list:
        # st.info("共现分析：输入数据或技能关键词列表为空。") # 可以在调用处处理
        return pd.DataFrame(columns=['skill_pair', 'count'])

    # 1. 为技能关键词构建高效的匹配模式
    #    确保与 extract_skills_from_job_names 中的正则构建逻辑一致
    skill_patterns_map = {} # skill_original_case -> pattern
    keyword_lower_to_original_map = {kw.lower(): kw for kw in skill_keywords_list}

    for original_kw in skill_keywords_list:
        kw_lower = original_kw.lower()
        pattern_str = ""
        if re.search(r'[\u4e00-\u9fff]', original_kw): # 中文或中英混合
            pattern_str = re.escape(original_kw)
        elif original_kw.isalnum(): # 纯英文/数字
            pattern_str = r'\b' + re.escape(original_kw) + r'\b'
        else: # 含特殊符号
            pattern_str = re.escape(original_kw)
        
        # 使用原始大小写的技能名作为 key，方便后续查找原始大小写
        skill_patterns_map[original_kw] = pattern_str
        
    # 构建一个大的正则表达式，一次性匹配所有技能
    # (?:pattern1|pattern2|...)
    # 使用 re.IGNORECASE，所以 pattern 本身不需要处理大小写，但在映射回原始大小写时需要
    # all_patterns_regex = r'(?:' + '|'.join(skill_patterns_map.values()) + r')'
    # 上面的方法在映射回原始大小写时复杂，改为逐个模式匹配，然后映射

    cooccurrence_counts = Counter()
    processed_texts_count = 0
    texts_meeting_min_skills_criteria = 0

    for text_content in df[text_column_to_scan].dropna().astype(str):
        processed_texts_count += 1
        found_skills_in_current_text_original_case = set()

        # 在当前文本中查找所有定义的技能关键词
        for original_skill_keyword, pattern in skill_patterns_map.items():
            # re.IGNORECASE 使得关键词列表中的大小写不重要，但我们想保留原始大小写用于输出
            if re.search(pattern, text_content, re.IGNORECASE):
                found_skills_in_current_text_original_case.add(original_skill_keyword)
        
        if len(found_skills_in_current_text_original_case) >= min_skills_in_one_text:
            texts_meeting_min_skills_criteria += 1
            # 对找到的技能（原始大小写）进行排序，以确保 ('A', 'B') 和 ('B', 'A') 被视为相同
            # list(found_skills_in_current_text_original_case) 确保是列表
            for combo in combinations(sorted(list(found_skills_in_current_text_original_case)), 2):
                cooccurrence_counts[combo] += 1

    # Debugging (可以在 Streamlit 页面之外或临时取消注释)
    # print(f"DEBUG cooc_opt: Processed {processed_texts_count} texts from column '{text_column_to_scan}'.")
    # print(f"DEBUG cooc_opt: {texts_meeting_min_skills_criteria} texts had >= {min_skills_in_one_text} skills.")
    # print(f"DEBUG cooc_opt: Total unique co-occurring pairs found (before filtering): {len(cooccurrence_counts)}")
    # if cooccurrence_counts:
    #     print(f"DEBUG cooc_opt: Top 5 raw cooccurrence_counts: {dict(cooccurrence_counts.most_common(5))}")


    if not cooccurrence_counts:
        # st.info("共现分析：未找到任何技能共现对。")
        return pd.DataFrame(columns=['skill_pair', 'count'])

    # 过滤掉频率过低的共现对
    frequent_cooccurrences = {
        pair: count for pair, count in cooccurrence_counts.items() if count >= min_cooc_frequency
    }

    if not frequent_cooccurrences:
        # st.info(f"共现分析：所有共现对的频率均低于设定的最小阈值 ({min_cooc_frequency})。")
        return pd.DataFrame(columns=['skill_pair', 'count'])

    # 获取 top N
    # Counter(frequent_cooccurrences) 确保 most_common 可以正确工作
    top_common_combos = Counter(frequent_cooccurrences).most_common(top_n_cooc_pairs)
    
    if not top_common_combos:
         # st.info(f"共现分析：过滤后无技能对满足Top N ({top_n_cooc_pairs}) 条件。")
        return pd.DataFrame(columns=['skill_pair', 'count'])

    combo_df = pd.DataFrame(top_common_combos, columns=['skill_pair_tuple', 'count'])
    combo_df['skill_pair'] = combo_df['skill_pair_tuple'].apply(lambda x: f"{x[0]} & {x[1]}")
    
    return combo_df[['skill_pair', 'count']].sort_values(by='count', ascending=False)
"""


@st.cache_data(ttl=3600) 
def load_json_data(file_path):
    actual_path_to_load = os.path.abspath(file_path)
    if not os.path.exists(actual_path_to_load):
        if streamlit_app_dir: st.error(f"Data file not found: {actual_path_to_load}")
        else: print(f"ERROR: Data file not found: {actual_path_to_load}")
        return pd.DataFrame()
    try:
        if actual_path_to_load.endswith('.jsonl'):
            records = []
            with open(actual_path_to_load, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError as e_line:
                        if streamlit_app_dir: st.warning(f"Skipping invalid JSON line: {e_line} - Line: {line.strip()[:100]}...")
            df = pd.DataFrame(records)
        elif actual_path_to_load.endswith('.json'):
            with open(actual_path_to_load, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data) # Assumes list of dicts or dict of dicts suitable for DataFrame
        else:
            if streamlit_app_dir: st.error(f"Unsupported file format: {actual_path_to_load}")
            return pd.DataFrame()
        return df
    except Exception as e:
        if streamlit_app_dir: st.error(f"Error loading data from {actual_path_to_load}: {e}")
        else: print(f"ERROR loading data from {actual_path_to_load}: {e}")
        return pd.DataFrame()

# --- This is the main preprocess_jobs_data function we will keep and modify ---

PROVINCE_DIRECT_MAP = {
    "北京市": "北京", "天津市": "天津", "上海市": "上海", "重庆市": "重庆",
    "内蒙古自治区": "内蒙古", "广西壮族自治区": "广西", "宁夏回族自治区": "宁夏",
    "新疆维吾尔自治区": "新疆", "西藏自治区": "西藏",
    "香港特别行政区": "香港", "澳门特别行政区": "澳门"
    #台湾省 -> 台湾 (if needed)
}

PROVINCE_SUFFIXES_TO_STRIP = ['省', '市', '自治区', '特别行政区'] # '市' for direct municipalities
CITY_SUFFIXES_TO_STRIP = ['市', '地区', '自治州', '盟', '县', '区'] # More comprehensive for city parts


@st.cache_data(ttl=3600)
def preprocess_jobs_data(df_jobs_raw):
    if df_jobs_raw.empty:
        return pd.DataFrame()

    df = df_jobs_raw.copy()

    PROVINCE_LEVEL_IDENTIFIERS = ['province', '省级', '省份', '直辖市', '自治区', '特别行政区']
    CITY_LEVEL_IDENTIFIERS = ['city', '市级', '城市', '地区', '自治州', '盟', '新区']

    required_cols_defaults = {
        'job_id': None, 'job_name': '未知职位', 'job_catory': '未知类别', 'job_industry': '未知行业',
        'high_month_pay': 0.0, 'low_month_pay': 0.0, 'publish_date': None, 'update_date': None,
        'company_name': '未知公司', 'area_code_name': '未知地区', 'prinvce_code_nme': '未知省份',
        'search_area_name': '未知地区', 'company_scale': '未知规模', 'degree_name': '学历不限',
        'major_required': '', 'company_property': '未知性质', 'company_tags': '',
        'source_url': '#', 'head_count': 1, 'level': 'unknown', 'work_year': '经验不限' # Added work_year
    }

    for col, default_val in required_cols_defaults.items():
        if col not in df.columns:
            df[col] = default_val
        else: # Fill NA for existing columns THEN convert type
            if col in ['major_required', 'company_tags', 'job_name', 'job_catory', 'job_industry',
                       'company_name', 'area_code_name', 'prinvce_code_nme', 'search_area_name',
                       'company_scale', 'degree_name', 'company_property', 'level', 'work_year', 'source_url']:
                df[col] = df[col].fillna(str(default_val)).astype(str)
            elif col in ['high_month_pay', 'low_month_pay', 'head_count']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(default_val if isinstance(default_val, (int, float)) else 0)
            elif col in ['publish_date', 'update_date']:
                 df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['avg_month_pay'] = df.apply(
        lambda row: (row['low_month_pay'] + row['high_month_pay']) / 2 if row['low_month_pay'] > 0 and row['high_month_pay'] > 0 else \
                    row['high_month_pay'] if row['high_month_pay'] > 0 else \
                    row['low_month_pay'] if row['low_month_pay'] > 0 else 0.0,
        axis=1
    )
    df['avg_month_pay'] = pd.to_numeric(df['avg_month_pay'], errors='coerce').fillna(0.0)

    for date_col in ['publish_date', 'update_date']:
        if date_col in df.columns:
            df[f'{date_col}_dt'] = pd.to_datetime(df[date_col], unit='ms', errors='coerce', utc=True)

    # --- Geographical Name Cleaning ---
    df['province_clean'] = df['prinvce_code_nme'].astype(str)
    for full, short in PROVINCE_DIRECT_MAP.items():
        df['province_clean'] = df['province_clean'].str.replace(full, short, regex=False)
    for suffix in PROVINCE_SUFFIXES_TO_STRIP:
        df['province_clean'] = df['province_clean'].str.replace(suffix, '', regex=False)
    df['province_clean'] = df['province_clean'].str.strip()
    df.loc[df['province_clean'] == '', 'province_clean'] = '未知省份'

    df['city_clean'] = '未知城市' # Initialize column
    for index, row in df.iterrows():
        level_val = str(row['level']).strip().lower()
        original_search_area = str(row['search_area_name']).strip()
        original_prinvce_name = str(row['prinvce_code_nme']).strip()
        cleaned_province_name = str(row['province_clean']).strip()
        current_city_val = "未知城市"

        if any(prov_id in level_val for prov_id in PROVINCE_LEVEL_IDENTIFIERS):
            current_city_val = cleaned_province_name
        elif any(city_id in level_val for city_id in CITY_LEVEL_IDENTIFIERS):
            city_candidate = original_search_area
            if original_search_area.startswith(original_prinvce_name) and len(original_search_area) > len(original_prinvce_name):
                city_candidate = original_search_area[len(original_prinvce_name):].strip()
            
            if city_candidate == original_prinvce_name or not city_candidate:
                current_city_val = cleaned_province_name
            else:
                temp_city_name = city_candidate
                for city_suffix in CITY_SUFFIXES_TO_STRIP:
                    temp_city_name = temp_city_name.replace(city_suffix, '')
                current_city_val = temp_city_name.strip()
                if not current_city_val: # If stripping made it empty
                    current_city_val = city_candidate # Revert to pre-stripped version
                    if not current_city_val: current_city_val = cleaned_province_name # Ultimate fallback
        else: # Fallback for 'unknown' level or other levels
            if original_search_area == original_prinvce_name or original_search_area == cleaned_province_name:
                current_city_val = cleaned_province_name
            else:
                city_candidate = original_search_area
                # Attempt to remove province prefix from search_area if present
                if original_search_area.startswith(original_prinvce_name) and len(original_search_area) > len(original_prinvce_name):
                    city_candidate = original_search_area[len(original_prinvce_name):].strip()
                
                temp_city_name = city_candidate
                for city_suffix in CITY_SUFFIXES_TO_STRIP:
                    temp_city_name = temp_city_name.replace(city_suffix, '')
                current_city_val = temp_city_name.strip()
                if not current_city_val: current_city_val = cleaned_province_name # Fallback
        
        df.loc[index, 'city_clean'] = current_city_val if current_city_val else "未知城市"
    
    df.loc[df['city_clean'].isin(['', '未知地区', '未知城市']) & (df['province_clean'] != '未知省份'), 'city_clean'] = df['province_clean']
    df.loc[df['city_clean'] == '', 'city_clean'] = '未知城市'
    # --- End Geographical Name Cleaning ---

    # --- Company Scale ---
    # 使用您提供的 scale_order
    TARGET_SCALE_CATEGORIES_ORDERED = ["1-49人", "50-99人", "100-499人", "500-999人", "1000-9999人", "10000+人", "未知"]
    
    # 尝试从 target_options.json 加载 scales，如果存在且有效，则优先使用它
    # 否则回退到您指定的 TARGET_SCALE_CATEGORIES_ORDERED
    custom_scale_order_from_options = []
    if os.path.exists(DEFAULT_OPTIONS_FILE_PATH):
        try:
            with open(DEFAULT_OPTIONS_FILE_PATH, 'r', encoding='utf-8') as f:
                target_options_content = json.load(f) # Renamed to avoid conflict
            if 'scales' in target_options_content and isinstance(target_options_content['scales'], list):
                loaded_scales = []
                for item in target_options_content['scales']:
                    if isinstance(item, dict) and 'name' in item and isinstance(item['name'], str):
                        loaded_scales.append(item['name'])
                    elif isinstance(item, str): # 如果列表里直接是字符串
                        loaded_scales.append(item)
                
                if loaded_scales: # 如果成功从文件加载了有效的规模列表
                    if "未知" not in loaded_scales: # 确保 "未知" 类别存在
                        loaded_scales.append("未知")
                    TARGET_SCALE_CATEGORIES_ORDERED = loaded_scales # 覆盖默认值
                    print(f"Info: Company scale categories loaded from '{os.path.basename(DEFAULT_OPTIONS_FILE_PATH)}': {TARGET_SCALE_CATEGORIES_ORDERED}")
                else:
                    print(f"Info: 'scales' in '{os.path.basename(DEFAULT_OPTIONS_FILE_PATH)}' was empty or invalid. Using predefined scale order.")
            else:
                print(f"Info: 'scales' key not found or not a list in '{os.path.basename(DEFAULT_OPTIONS_FILE_PATH)}'. Using predefined scale order.")
        except Exception as e_scale_load:
            print(f"Warning: Error loading company scales from '{os.path.basename(DEFAULT_OPTIONS_FILE_PATH)}': {e_scale_load}. Using predefined scale order.")
            # 确保 TARGET_SCALE_CATEGORIES_ORDERED 仍然是您提供的列表
            if "未知" not in TARGET_SCALE_CATEGORIES_ORDERED: # 再次检查，以防万一
                TARGET_SCALE_CATEGORIES_ORDERED.append("未知")


    def clean_and_map_scale(raw_scale_str):
        if pd.isna(raw_scale_str): return "未知"
        s = str(raw_scale_str).strip().lower()
        if not s or s in ['nan', 'none', 'null', '保密', '不详', '未知', '不明确', '不限公司规模', '-1', '0']: return "未知"

        # 优先精确匹配 target_options.json 中定义的类别 (如果已加载)
        # 或您提供的 TARGET_SCALE_CATEGORIES_ORDERED
        for target_scale in TARGET_SCALE_CATEGORIES_ORDERED:
            if target_scale.lower() == s:
                return target_scale # 返回原始大小写的目标类别

        # 基于关键词的模糊匹配和范围映射 (映射到您提供的 scale_order)
        # "1-49人"
        if any(x in s for x in ["少于15", "1-15", "0-20", "20人以下", "1-49", "少于50人"]): return "1-49人" # 包含原 "少于50人"
        # "50-99人"
        if any(x in s for x in ["15-50", "20-99", "50-99"]): return "50-99人"
        # "100-499人"
        if any(x in s for x in ["50-150", "100-499", "150-499"]): return "100-499人"
        # "500-999人"
        if any(x in s for x in ["150-500", "500-999", "500人以下", "千人以下"]): return "500-999人" # 500人以下可能需要更细致判断，但这里归入
        # "1000-9999人"
        if any(x in s for x in ["500-2000", "1000-4999", "1000-9999", "1000-2000", "2000-5000", "5000-9999", "千人规模", "几千人"]): return "1000-9999人"
        # "10000+人"
        if any(x in s for x in ["2000人以上", "5000人以上", "10000人以上", "10000+", "万人以上", "上市公司", "大型企业"]): return "10000+人"
        
        # 正则表达式匹配数字范围
        m = re.match(r'(\d+)[人\s]*-?[至到]?\s*(\d+)\s*人?', s) # 匹配 "数字-数字人", "数字人-数字人", "数字 至/到 数字人"
        if m:
            low, high = int(m.group(1)), int(m.group(2))
            if high < 50: return "1-49人"
            if low >=1 and high <= 49: return "1-49人"
            if low >=50 and high <= 99: return "50-99人"
            if low >=100 and high <= 499: return "100-499人"
            if low >=500 and high <= 999: return "500-999人"
            if low >=1000 and high <= 9999: return "1000-9999人"
            if low >= 10000: return "10000+人"
            # 更宽松的范围判断
            if high <= 49: return "1-49人"
            if high <= 99: return "50-99人"
            if high <= 499: return "100-499人"
            if high <= 999: return "500-999人"
            if high <= 9999: return "1000-9999人"
            return "10000+人" # 默认更大的

        m_above = re.match(r'(\d+)\s*人?\s*(以上|\+)', s) # 匹配 "数字人以上", "数字+"
        if m_above:
            val = int(m_above.group(1))
            if val >= 10000: return "10000+人"
            if val >= 1000: return "1000-9999人" # 如果是1000人以上，大部分情况是这个档
            if val >= 500: return "500-999人"
            if val >= 100: return "100-499人"
            if val >= 50: return "50-99人"
            return "1-49人" # 例如 20人以上

        m_below = re.match(r'少于\s*(\d+)\s*人', s) # 匹配 "少于 数字 人"
        if m_below:
            val = int(m_below.group(1))
            if val <= 50 : return "1-49人" # 少于50人 归入 1-49人
            if val <= 100: return "50-99人"
            # ... 可以根据需要添加更多
            
        return "未知"

    df['company_scale_cleaned_mapped'] = df['company_scale'].apply(clean_and_map_scale)
    
    # 确保所有映射后的值都在 TARGET_SCALE_CATEGORIES_ORDERED 中，如果不在则设为"未知"
    # 这一步很重要，因为 clean_and_map_scale 可能产生不在目标列表中的中间值
    unique_cleaned_scales = df['company_scale_cleaned_mapped'].unique()
    for scale_val in unique_cleaned_scales:
        if scale_val not in TARGET_SCALE_CATEGORIES_ORDERED:
            df.loc[df['company_scale_cleaned_mapped'] == scale_val, 'company_scale_cleaned_mapped'] = "未知"
            
    df['company_scale_cat'] = pd.Categorical(
        df['company_scale_cleaned_mapped'], 
        categories=TARGET_SCALE_CATEGORIES_ORDERED, 
        ordered=True
    )
    # 再次填充可能因强制转换为Categorical产生的NaN（如果值不在categories中）
    df['company_scale_cat'] = df['company_scale_cat'].fillna("未知")


    # --- Degree Name ---
    TARGET_DEGREE_CATEGORIES_ORDERED = ['学历不限', '其他', '初中及以下', '中专', '中技', '中专/中技', '高中', '大专', '本科', '硕士', '博士', '博士后']
    custom_degree_order_from_options = []
    if os.path.exists(DEFAULT_OPTIONS_FILE_PATH):
        try:
            with open(DEFAULT_OPTIONS_FILE_PATH, 'r', encoding='utf-8') as f: target_options_content_degree = json.load(f)
            if 'degrees' in target_options_content_degree and isinstance(target_options_content_degree['degrees'], list):
                loaded_degrees = []
                for item in target_options_content_degree['degrees']:
                    if isinstance(item, dict) and 'name' in item and isinstance(item['name'], str): loaded_degrees.append(item['name'])
                    elif isinstance(item, str): loaded_degrees.append(item)
                if loaded_degrees:
                    if '学历不限' not in loaded_degrees and '不限' not in loaded_degrees : loaded_degrees.insert(0, '学历不限')
                    if '其他' not in loaded_degrees: loaded_degrees.insert(1, '其他')
                    TARGET_DEGREE_CATEGORIES_ORDERED = loaded_degrees
        except Exception: pass
    
    df['degree_name'] = df['degree_name'].fillna('学历不限').astype(str)
    df.loc[df['degree_name'].str.lower().isin(['不限', '', 'nan', 'none', 'null', '-1']), 'degree_name'] = '学历不限'
    def map_to_standard_degree(raw_degree_str):
        s_raw = str(raw_degree_str)
        s_lower = s_raw.lower()
        if s_lower in ['学历不限', '不限', '', 'nan', 'none', 'null', '-1', '0']: return '学历不限'
        for target_cat in TARGET_DEGREE_CATEGORIES_ORDERED: # 精确匹配（忽略大小写输入，但用目标类别的大小写）
            if target_cat.lower() == s_lower: return target_cat
        # 模糊匹配
        if '初中' in s_lower: return '初中及以下'
        if '中专' in s_lower or '中技' in s_lower: return '中专/中技' # 假设目标列表有 "中专/中技"
        if '高中' in s_lower: return '高中'
        if '大专' in s_lower or '专科' in s_lower: return '大专'
        if '本科' in s_lower or '学士' in s_lower: return '本科'
        if '硕士' in s_lower or ('研究生' in s_raw and '博士' not in s_raw): return '硕士'
        if '博士后' in s_lower: return '博士后' # 博士后优先于博士
        if '博士' in s_lower: return '博士'
        return '其他'
    df['degree_name_mapped'] = df['degree_name'].apply(map_to_standard_degree)
    unique_mapped_degrees = df['degree_name_mapped'].unique()
    for degree_val in unique_mapped_degrees:
        if degree_val not in TARGET_DEGREE_CATEGORIES_ORDERED:
            df.loc[df['degree_name_mapped'] == degree_val, 'degree_name_mapped'] = '其他'
            if '其他' not in TARGET_DEGREE_CATEGORIES_ORDERED: TARGET_DEGREE_CATEGORIES_ORDERED.append('其他') # 确保'其他'在列表中
    df['degree_name_cat'] = pd.Categorical(df['degree_name_mapped'], categories=TARGET_DEGREE_CATEGORIES_ORDERED, ordered=True)
    df['degree_name_cat'] = df['degree_name_cat'].fillna('其他')


    # --- Work Year ---
    df['work_year_numeric'] = pd.to_numeric(df['work_year'], errors='coerce') 
    df.loc[df['work_year'].isin(['不限', '经验不限', '无经验', '应届毕业生', '应届生', '在校生', '-1', '0', '无需经验']), 'work_year_numeric'] = 0
    def parse_work_year_text(text):
        if pd.isna(text) or isinstance(text, (int, float)): return text
        text_str = str(text).strip()
        if not text_str or text_str.lower() in ['不限', '经验不限', '无经验', '应届毕业生', '应届生', '在校生', '-1', '0', '无需经验']: return 0
        if "年以内" in text_str or "1年以下" in text_str or "一年以内" in text_str: return 0.5
        if "年以上" in text_str:
            match = re.search(r'(\d+)', text_str)
            return int(match.group(1)) if match else np.nan
        match_range = re.search(r'(\d+)[-\s至到]*(\d+)年', text_str)
        if match_range:
            return (int(match_range.group(1)) + int(match_range.group(2))) / 2
        match_single = re.search(r'(\d+)年', text_str)
        if match_single: return int(match_single.group(1))
        return np.nan
    
    # 优先使用 work_year_numeric 如果它已经是有效的数字，否则尝试从文本解析
    df['work_year_numeric'] = df.apply(
        lambda row: row['work_year_numeric'] if pd.notna(row['work_year_numeric']) else parse_work_year_text(row['work_year']),
        axis=1
    )
    df['work_year_numeric'] = pd.to_numeric(df['work_year_numeric'], errors='coerce').fillna(-1) # -1 代表"经验不限"进入特定bin

    bins = [-np.inf, 0, 1, 3, 5, 10, np.inf] 
    labels = ['经验不限', '1年以内', '1-3年', '3-5年', '5-10年', '10年以上']
    # 如果要完全匹配您之前的 bins/labels (即 -1 -> '经验不限', 0 -> '1年以内')
    bins = [-np.inf, -0.5, 0.5, 2.5, 4.5, 7.5, np.inf] # 调整 bins 使0落在 '1年以内'
    labels = ['经验不限', '1年以内', '1-3年', '3-5年', '5-10年', '10年以上']
    # current bins: -1 (经验不限), 0 (1年以内), 1,2 (1-3年), 3,4 (3-5年), 5-9 (5-10年), 10+ (10年以上)
    # The current bins=[-np.inf, 0, 1, 3, 5, 10, np.inf] and labels mean:
    #   val < 0  -> '经验不限' (includes our -1 for "经验不限")
    #   0 <= val < 1 -> '1年以内'
    #   1 <= val < 3 -> '1-3年'
    #   3 <= val < 5 -> '3-5年'
    #   5 <= val < 10 -> '5-10年'
    #   val >= 10 -> '10年以上'
    # This seems reasonable.
    df['work_year_cat'] = pd.cut(df['work_year_numeric'], bins=bins, labels=labels, right=False, include_lowest=True)
    df['work_year_cat'] = df['work_year_cat'].cat.reorder_categories(labels, ordered=True).fillna('经验不限')


    # --- Major, Tags, Skills Text ---
    common_none_terms = ['none', 'null', '无', '', 'nan', '-1']
    standard_majors_list = _load_standard_majors() # Cached
    df['major_required_cleaned'] = df['major_required'].astype(str).str.lower().str.strip()
    df['major_required_cleaned'].replace(common_none_terms + ['不限', '未知', '专业不限', '相关专业', '不要求', '其他'], '未知', inplace=True)
    if standard_majors_list:
        df['processed_major'] = df['major_required_cleaned'].apply(
            lambda x: _map_to_standard_major(x, standard_majors_list) if x != '未知' else '未知'
        )
    else:
        df['processed_major'] = df['major_required_cleaned'].apply(lambda x: '其他专业' if x and x != '未知' else '未知')

    def split_raw_majors(text):
        if not text or text.lower().strip() in common_none_terms + ['不限', '未知', '专业不限', '相关专业', '不要求', '其他']: return tuple()
        text_cleaned = text.replace("或相关专业", " 相关专业").replace("及相关专业", " 相关专业")
        delimiters = r"[\s,，、;/()（）]+" # 包括括号
        raw_majors = [m.strip() for m in re.split(delimiters, text_cleaned) if m.strip() and m.strip().lower() not in common_none_terms and len(m.strip()) > 1 and "相关专业" not in m and "专业" not in m] # 避免单独的"专业"
        return tuple(m for m in raw_majors if m)
    df['majors_list'] = df['major_required'].apply(split_raw_majors)

    df['company_tags'] = df['company_tags'].astype(str).fillna('')
    df['tags_list'] = df['company_tags'].apply(
        lambda x: tuple(t.strip() for t in x.split('，') if t.strip() and t.strip().lower() not in common_none_terms) 
        if x.strip() and x.strip().lower() not in common_none_terms else tuple()
    )

    df['job_name_and_major_text'] = df['job_name'].astype(str).fillna('') + " " + df['major_required'].astype(str).fillna('')
    if 'job_description' in df.columns:
        df['job_name_and_major_text'] += " " + df['job_description'].astype(str).fillna('')
    # 在这里调用 extract_skills_from_text_series
    df['extracted_skills_list'] = extract_skills_from_text_series(df['job_name_and_major_text'], SKILL_REGEX_PATTERNS)


    # --- Company Property ---
    if 'company_property' in df.columns and os.path.exists(DEFAULT_OPTIONS_FILE_PATH):
        try:
            with open(DEFAULT_OPTIONS_FILE_PATH, 'r', encoding='utf-8') as f: target_options_content_prop = json.load(f)
            if 'corpProps' in target_options_content_prop and isinstance(target_options_content_prop['corpProps'], list):
                prop_map = {str(item['code']): item['name'] for item in target_options_content_prop['corpProps'] if isinstance(item, dict) and 'code' in item and 'name' in item}
                # 先映射，对于无法映射的，保留原值，后续再统一处理
                df['company_property'] = df['company_property'].astype(str).map(prop_map).fillna(df['company_property'])
                valid_prop_names = list(prop_map.values()) + ['未知性质'] # 包括我们期望的未知值
                # 对于那些不是有效名称（也不为空/NaN）的值，设为 "未知性质"
                df.loc[~df['company_property'].isin(valid_prop_names) & df['company_property'].notna() & (df['company_property'] != ''), 'company_property'] = '未知性质'
                df['company_property'] = df['company_property'].fillna('未知性质') # 填充所有剩下的NaN
        except Exception: # 如果加载或映射失败
            df['company_property'] = df['company_property'].fillna('未知性质').astype(str)
            df.loc[df['company_property'].astype(str).str.match(r'^\d+$|^-$'), 'company_property'] = '未知性质'
    elif 'company_property' in df.columns: # 如果文件不存在但列存在
        df['company_property'] = df['company_property'].fillna('未知性质').astype(str)
        df.loc[df['company_property'].astype(str).str.match(r'^\d+$|^-$'), 'company_property'] = '未知性质' # 清理数字代码
    else: # 如果列也不存在
        df['company_property'] = '未知性质'
    df.loc[df['company_property'].isin(['', '-1', '0', '不详']), 'company_property'] = '未知性质' # 最终捕获


    # Final check for consistency in "未知" type values across key categorical columns
    unknown_synonyms_map = {
        'job_catory': '未知类别',
        'job_industry': '未知行业',
        'company_property': '未知性质' # 已经处理过了，但可以再次确保
    }
    raw_unknowns_to_catch = ['未知', '不详', '保密', '不明确', '其他', '', '-1', '0', 'null', 'none', 'nan'] # 更全面的列表

    for col_name, standard_unknown_val in unknown_synonyms_map.items():
        if col_name in df.columns:
            df[col_name] = df[col_name].astype(str).str.strip()
            for syn in raw_unknowns_to_catch:
                 # 使用 .str.lower() 来匹配，但替换为 standard_unknown_val (保留其大小写)
                df.loc[df[col_name].str.lower() == syn.lower(), col_name] = standard_unknown_val
            df.loc[df[col_name].str.strip() == '', col_name] = standard_unknown_val # 确保空字符串也被处理
            df[col_name] = df[col_name].fillna(standard_unknown_val) # 以防万一的 fillna

    return df

# --- Analysis functions ---
@st.cache_data
def get_top_n_counts(df, column_name, top_n=10):
    if df.empty or column_name not in df.columns:
        return pd.DataFrame(columns=[column_name, 'count'])
    
    # Ensure column is suitable for value_counts (e.g., not all NaN)
    if df[column_name].dropna().empty:
        return pd.DataFrame(columns=[column_name, 'count'])
        
    counts = df[column_name].value_counts().nlargest(top_n).reset_index()
    # Ensure correct column names after reset_index
    counts.columns = [column_name, 'count'] if len(counts.columns) == 2 else ['item', 'count'] # Fallback
    if counts.columns[0] != column_name and 'item' == counts.columns[0]: # Rename if needed
        counts.rename(columns={'item': column_name}, inplace=True)

    return counts

@st.cache_data
def get_average_salary(df, group_by_col):
    if df.empty or group_by_col not in df.columns or 'avg_month_pay' not in df.columns:
        return pd.DataFrame(columns=[group_by_col, 'average_salary', 'median_salary', 'job_count'])
    
    valid_salary_df = df[(df['avg_month_pay'] > 0) & df[group_by_col].notna()] # Also filter out NaN group_by keys
    if valid_salary_df.empty:
        return pd.DataFrame(columns=[group_by_col, 'average_salary', 'median_salary', 'job_count'])
    
    # Using observed=True is generally safer for categorical data if categories might not all be present
    result = valid_salary_df.groupby(group_by_col, observed=True).agg( 
        average_salary=('avg_month_pay', 'mean'),
        median_salary=('avg_month_pay', 'median'),
        job_count=('job_id', 'count') # Assuming job_id is unique identifier
    ).reset_index()

    result['average_salary'] = result['average_salary'].round(1)
    result['median_salary'] = result['median_salary'].round(1)
    return result.sort_values(by='average_salary', ascending=False)

@st.cache_data
def get_avg_salary_by_city(df_jobs): 
    return get_average_salary(df_jobs, 'city_clean')

@st.cache_data
def get_avg_salary_by_province(df_jobs):
    return get_average_salary(df_jobs, 'province_clean')

@st.cache_data
def get_avg_salary_by_category(df_jobs):
    return get_average_salary(df_jobs, 'job_catory')

@st.cache_data
def get_avg_salary_by_processed_major(df_jobs): # For standardized majors
    return get_average_salary(df_jobs, 'processed_major')


@st.cache_data
def get_word_counts_from_list_column(df, list_column_name, top_n=20, exclude_items=None): # Name was changed slightly in original, kept this more specific one
    if df.empty or list_column_name not in df.columns:
        return pd.DataFrame(columns=['item', 'count'])
    
    default_exclude = {'none', 'null', '无', '', '未知', '不限', '相关专业'} # Use a set for faster lookups
    current_exclude_items = default_exclude.copy()
    if exclude_items:
        current_exclude_items.update(str(item).lower().strip() for item in exclude_items)

    all_items_from_col = []
    # This column should contain iterables (lists/tuples of strings)
    for item_iterable in df[list_column_name].dropna():
        if isinstance(item_iterable, (list, tuple)): 
            for item in item_iterable:
                cleaned_item = str(item).strip() 
                # Add more filtering: e.g. min length, specific unwanted terms
                if cleaned_item and cleaned_item.lower() not in current_exclude_items and len(cleaned_item) > 1:
                    all_items_from_col.append(cleaned_item)
        # else: # If a row has a single string instead of a list/tuple
            # cleaned_item = str(item_iterable).strip()
            # if cleaned_item and cleaned_item.lower() not in current_exclude_items and len(cleaned_item) > 1:
            #     all_items_from_col.append(cleaned_item)
    
    if not all_items_from_col:
        return pd.DataFrame(columns=['item', 'count'])
        
    counts = Counter(all_items_from_col)
    top_items = counts.most_common(top_n)
    return pd.DataFrame(top_items, columns=['item', 'count'])


@st.cache_data
def get_time_series_data(df, time_col='publish_date_dt', freq='ME', value_col=None): # Default to Month End
    if df.empty or time_col not in df.columns or not pd.api.types.is_datetime64_any_dtype(df[time_col]):
        return pd.Series(dtype='float64' if value_col else 'int64')

    df_time = df.dropna(subset=[time_col])
    if df_time.empty:
        return pd.Series(dtype='float64' if value_col else 'int64')

    # Ensure time_col is UTC before resampling, or handle naive datetimes appropriately
    if df_time[time_col].dt.tz is None: # If naive
        # Assuming naive datetimes are effectively UTC or should be treated as such for resampling
        df_time_indexed = df_time.set_index(df_time[time_col].dt.tz_localize('UTC', ambiguous='NaT', nonexistent='NaT'))
    else: # Already timezone-aware
        df_time_indexed = df_time.set_index(df_time[time_col].dt.tz_convert('UTC'))


    if value_col and value_col in df_time_indexed.columns:
        series = df_time_indexed[value_col].resample(freq).mean()
    else: # Default to counting job_id
        series = df_time_indexed['job_id'].resample(freq).count() if 'job_id' in df_time_indexed else df_time_indexed.iloc[:,0].resample(freq).count()

    
    series = series.fillna(0) 

    if not series.empty: # Trim leading/trailing zeros
        try:
            first_valid_index = series.ne(0).idxmax() 
            last_valid_index = series.ne(0)[::-1].idxmax() 
            if pd.notna(first_valid_index) and pd.notna(last_valid_index) and first_valid_index <= last_valid_index:
                series = series[first_valid_index:last_valid_index]
            else: # All zeros or invalid range
                return pd.Series(dtype=series.dtype)
        except ValueError: # Handles cases like all zeros
            return pd.Series(dtype=series.dtype)
            
    return series

@st.cache_data
def extract_skills_from_job_names(df_jobs, top_n=20): # This function seems to be a precursor to the SKILL_REGEX_PATTERNS approach. Consider deprecating or aligning.
    if df_jobs.empty:
        return pd.DataFrame(columns=['skill', 'count'])

    # Ensure both columns exist, default to empty string if not
    job_names_series = df_jobs.get('job_name', pd.Series(dtype=str)).dropna().astype(str)
    major_required_series = df_jobs.get('major_required', pd.Series(dtype=str)).dropna().astype(str)

    if job_names_series.empty and major_required_series.empty:
        return pd.DataFrame(columns=['skill', 'count'])
            
    # More comprehensive list, consider moving to a config file or separate list
    keywords = [
        'Python', 'Java', 'Go', 'Golang', 'C++', 'C#', 'JavaScript', 'JS', 'TypeScript', 'TS', 
        'React', 'Vue', 'Angular', 'Node.js', 'Node', 'Spring', 'Django', 'Flask', 'FastAPI',
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQLServer', 'NoSQL',
        'AWS', 'Azure', 'GCP', '阿里云', '腾讯云', '华为云', '云计算', '云原生', 'Cloud',
        'Docker', 'Kubernetes', 'K8S', 'CI/CD', 'DevOps', 'Jenkins', 'Git', 'Linux', 'Unix', 'Shell',
        '数据分析', '数据挖掘', '大数据', 'Spark', 'Hadoop', 'Flink', 'Kafka', 'Hive', 'HBase',
        '机器学习', '深度学习', 'AI', '人工智能', 'NLP', '自然语言处理', 'CV', '计算机视觉', '推荐算法',
        '算法', '架构', '架构师', '前端', '后端', '全栈', '测试', '软件测试', '自动化测试', '性能测试', '运维', 'SRE',
        '产品经理', '项目经理', 'PM', '运营', '市场', '销售', 'BD', '客服', 'HR', '人事', '行政', '财务', '会计', '法务',
        'UI', 'UX', '设计', '平面设计', '交互设计', '游戏开发', 'UE4', 'UE5', 'Unity', 'U3D',
        '移动开发', 'iOS', 'Android', 'Flutter', 'React Native', '小程序', '写作',
        '嵌入式', '物联网', 'IoT', '芯片', 'FPGA', '驱动开发', '网络安全', '信息安全',
        # 可以考虑加入一些与专业强相关的通用技术词，例如：
        '计算机', '软件工程', '通信工程', '电子信息', '自动化', '机械', '数学', '统计' # 这些也可能出现在 major_required
    ]
    
    escaped_keywords = []
    for kw in keywords:
        if kw.isalnum(): # For simple alphanumeric keywords
            # For Chinese keywords or mixed, \b might not work as expected with re.IGNORECASE
            # if re.search(r'[\u4e00-\u9fff]', kw): # If it contains Chinese
            #     escaped_keywords.append(re.escape(kw)) # Match exactly, no word boundaries
            # else:
            escaped_keywords.append(r'\b' + re.escape(kw) + r'\b')
        else: # For keywords with special characters like C++, C#, Node.js
            escaped_keywords.append(re.escape(kw))

    regex_pattern = r'(?:' + '|'.join(escaped_keywords) + r')'
    
    found_skills_raw = []
    
    # Process job_name
    for name_text in job_names_series:
        if pd.notna(name_text) and name_text.strip():
            found_skills_raw.extend(re.findall(regex_pattern, name_text, re.IGNORECASE))
    
    # Process major_required
    # Define terms in major_required that usually mean "no specific skill constraint" from this field
    generic_major_placeholders = {'不限', '不限专业', '专业不限', '无专业限制', '相关专业', '', '无'}
    for major_text in major_required_series:
        if pd.notna(major_text) and major_text.strip():
            # Avoid extracting from very generic major requirements
            cleaned_major_text = major_text.strip()
            if cleaned_major_text.lower() not in [p.lower() for p in generic_major_placeholders]:
                # Check if it doesn't solely consist of placeholders
                is_placeholder_only = True
                for placeholder in generic_major_placeholders:
                    if placeholder.lower() not in cleaned_major_text.lower():
                        is_placeholder_only = False
                        break
                if not is_placeholder_only or len(cleaned_major_text) > 5 : # Arbitrary length to allow short specific majors
                    found_skills_raw.extend(re.findall(regex_pattern, cleaned_major_text, re.IGNORECASE))
    
    if not found_skills_raw:
        return pd.DataFrame(columns=['skill', 'count'])

    normalized_skill_counts = Counter()
    keyword_lower_map = {kw.lower(): kw for kw in keywords} 

    for skill_match in found_skills_raw:
        # Normalize: try to match to original keyword casing, otherwise use the match itself
        # This handles cases where regex might pick up "python" but keyword is "Python"
        original_case_skill = keyword_lower_map.get(skill_match.lower(), skill_match)
        normalized_skill_counts[original_case_skill] += 1
            
    common_skills = normalized_skill_counts.most_common(top_n)
    return pd.DataFrame(common_skills, columns=['skill', 'count'])

# --- Plotting functions ---
def plot_bar_chart(df, x_col, y_col, title, x_label, y_label, color=None, orientation='v', text_auto=True):
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        if streamlit_app_dir: st.write(f"图表 '{title}' 无数据显示或缺少必要列。")
        return
    
    df_plot = df.copy()
    # Ensure data types are suitable for plotting
    if orientation == 'h':
        df_plot[x_col] = df_plot[x_col].astype(str) # Y-axis categories
        df_plot[y_col] = pd.to_numeric(df_plot[y_col], errors='coerce').fillna(0) # X-axis values
        fig = px.bar(df_plot, y=x_col, x=y_col, title=title, labels={x_col: x_label, y_col: y_label}, 
                     color=color, orientation='h', text_auto=text_auto if pd.api.types.is_numeric_dtype(df_plot[y_col]) else None)
        fig.update_yaxes(categoryorder='total ascending') # Sort bars by value
    else: # Vertical bar chart
        df_plot[x_col] = df_plot[x_col].astype(str) # X-axis categories
        df_plot[y_col] = pd.to_numeric(df_plot[y_col], errors='coerce').fillna(0) # Y-axis values
        fig = px.bar(df_plot, x=x_col, y=y_col, title=title, labels={x_col: x_label, y_col: y_label}, 
                     color=color, text_auto=text_auto if pd.api.types.is_numeric_dtype(df_plot[y_col]) else None)
        fig.update_layout(xaxis_tickangle=-45)
    if streamlit_app_dir: st.plotly_chart(fig, use_container_width=True)

def plot_pie_chart(df, names_col, values_col, title, hole=0.0): # Ensure hole is float
    if df.empty or names_col not in df.columns or values_col not in df.columns:
        if streamlit_app_dir: st.write(f"饼图 '{title}' 无数据显示或缺少必要列。")
        return
    df_plot = df.copy()
    df_plot[names_col] = df_plot[names_col].astype(str)
    df_plot[values_col] = pd.to_numeric(df_plot[values_col], errors='coerce').fillna(0)
    fig = px.pie(df_plot, names=names_col, values=values_col, title=title, hole=hole)
    if streamlit_app_dir: st.plotly_chart(fig, use_container_width=True)

def plot_line_chart(series, title, x_label="日期", y_label="数量/值", default_lookback_days=None):
    if not isinstance(series, pd.Series) or series.empty:
        if streamlit_app_dir: st.info(f"折线图 '{title}' 无有效数据可供展示。") 
        return

    plot_series = series.copy() 
    plot_series.index.name = x_label # Set index name for clearer hover label

    # Apply lookback if specified
    if default_lookback_days and not plot_series.empty and isinstance(plot_series.index, pd.DatetimeIndex):
        max_date_in_series = plot_series.index.max()
        if pd.notna(max_date_in_series): 
            cutoff_date = max_date_in_series - pd.Timedelta(days=default_lookback_days)
            min_date_in_series = plot_series.index.min()
            # Ensure cutoff is not before the actual start of data
            if pd.notna(min_date_in_series) and cutoff_date < min_date_in_series:
                cutoff_date = min_date_in_series 
            plot_series = plot_series[plot_series.index >= cutoff_date]
    
    if plot_series.empty: 
        if streamlit_app_dir: st.info(f"在选定的回溯期内，图表 '{title}' 无数据显示。")
        return

    fig = px.line(plot_series, y=plot_series.name if plot_series.name else y_label, title=title, labels={'value': y_label}) # Use series name if available
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="近1月", step="month", stepmode="backward"),
                dict(count=3, label="近3月", step="month", stepmode="backward"),
                dict(count=6, label="近6月", step="month", stepmode="backward"),
                dict(count=1, label="今年", step="year", stepmode="todate"),
                dict(count=1, label="近1年", step="year", stepmode="backward"),
                dict(step="all", label="全部")
            ])
        )
    )
    if streamlit_app_dir: st.plotly_chart(fig, use_container_width=True)

def plot_scatter_mapbox(df, lat_col, lon_col, size_col=None, color_col=None, text_col=None, map_title="Job Distribution on Map"):
    if df.empty or lat_col not in df.columns or lon_col not in df.columns:
        if streamlit_app_dir: st.write("地图数据不完整或缺少经纬度列。")
        return
    
    df_map = df.copy()
    # Ensure lat/lon are numeric and drop NaNs
    df_map[lat_col] = pd.to_numeric(df_map[lat_col], errors='coerce')
    df_map[lon_col] = pd.to_numeric(df_map[lon_col], errors='coerce')
    df_map.dropna(subset=[lat_col, lon_col], inplace=True)

    if df_map.empty: 
        if streamlit_app_dir: st.write("未找到有效的地理坐标用于地图绘制。"); return

    # Prepare size and color columns
    if size_col and size_col in df_map.columns: 
        df_map[size_col] = pd.to_numeric(df_map[size_col], errors='coerce').fillna(1)
    else: size_col = None # Ensure it's None if not valid

    if color_col and color_col in df_map.columns:
        df_map[color_col] = df_map[color_col].astype(str) # Treat color as categorical for map
        if df_map[color_col].nunique() > 20: # Limit distinct colors for clarity
             if streamlit_app_dir: st.info("颜色编码的类别过多，地图将不使用颜色区分。")
             color_col = None 
    else: color_col = None


    hover_data_dict = {lat_col: False, lon_col: False} # Don't show lat/lon in hover by default
    custom_hover_cols = ['city_clean', 'province_clean', 'job_count', 'average_salary', 'median_salary'] 
    for h_col in custom_hover_cols:
        if h_col in df_map.columns:
            if pd.api.types.is_numeric_dtype(df_map[h_col]): # Check if column is numeric
                hover_data_dict[h_col] = ':.1f' if 'salary' in h_col else True # Format numerics
            else:
                hover_data_dict[h_col] = True # Show strings as is
    
    # Determine text to display on map markers
    effective_text_col = None
    if text_col and text_col in df_map.columns : effective_text_col = text_col
    elif 'city_clean' in df_map.columns : effective_text_col = 'city_clean'


    fig = px.scatter_mapbox(df_map, lat=lat_col, lon=lon_col,
                            size=size_col, color=color_col,
                            text=effective_text_col,
                            size_max=20 if size_col else 8, zoom=3, height=600, title=map_title,
                            hover_name=effective_text_col if effective_text_col else None, # Use determined text col for hover name
                            hover_data=hover_data_dict
                           )
    fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":30,"l":0,"b":0})
    if streamlit_app_dir: st.plotly_chart(fig, use_container_width=True)


@st.cache_data
def calculate_time_deltas(df_jobs): # Already corrected in previous step
    if df_jobs.empty:
        return df_jobs.assign(time_delta_days=pd.NA, publish_to_update_hours=pd.NA, job_age_days=pd.NA)

    df = df_jobs.copy()
    date_cols_to_process = []

    for col_name in ['publish_date_dt', 'update_date_dt']:
        if col_name in df.columns:
            date_cols_to_process.append(col_name)
        else:
            df[col_name] = pd.NaT # Add as NaT if missing

    for col in date_cols_to_process:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        if df[col].dt.tz is not None:
            df[col] = df[col].dt.tz_convert('UTC')
        else:
            df[col] = df[col].dt.tz_localize('UTC', ambiguous='NaT', nonexistent='NaT')

    df['time_delta_days'] = pd.NA
    df['publish_to_update_hours'] = pd.NA
    df['job_age_days'] = pd.NA

    if 'publish_date_dt' in df.columns and 'update_date_dt' in df.columns:
        valid_dates_mask = df['publish_date_dt'].notna() & df['update_date_dt'].notna()
        if valid_dates_mask.any():
            delta = (df.loc[valid_dates_mask, 'update_date_dt'] - df.loc[valid_dates_mask, 'publish_date_dt'])
            df.loc[valid_dates_mask, 'time_delta_days'] = delta.dt.total_seconds() / (24 * 60 * 60)
            df.loc[valid_dates_mask, 'publish_to_update_hours'] = delta.dt.total_seconds() / (60 * 60)

    now_utc = datetime.now(timezone.utc)
    if 'publish_date_dt' in df.columns:
        valid_publish_mask = df['publish_date_dt'].notna()
        if valid_publish_mask.any():
            df.loc[valid_publish_mask, 'job_age_days'] = (now_utc - df.loc[valid_publish_mask, 'publish_date_dt']).dt.total_seconds() / (24 * 60 * 60)
    
    if 'time_delta_days' in df.columns: df.loc[df['time_delta_days'] < 0, 'time_delta_days'] = pd.NA
    if 'publish_to_update_hours' in df.columns: df.loc[df['publish_to_update_hours'] < 0, 'publish_to_update_hours'] = pd.NA
    if 'job_age_days' in df.columns: df.loc[df['job_age_days'] < 0, 'job_age_days'] = pd.NA
    
    return df

@st.cache_data
def get_job_freshness_distribution(df_with_age, bins=None):
    if df_with_age.empty or 'job_age_days' not in df_with_age.columns:
        return pd.DataFrame(columns=['freshness_range', 'count'])
    
    # Define labels matching the number of bins - 1
    default_labels = ['无效/未来', '1天内', '1-3天', '3-7天', '1-2周', '2周-1个月', '1-2个月', '2-3个月', '3-6个月', '半年-1年', '1年以上']
    if bins is None:
        # Bins: -inf (for <0), 0 (for exactly 0), 1 (for <1 day), 3, 7, 14, 30, 60, 90, 180, 365, +inf
        default_bins = [-float('inf'), 0, 1, 3, 7, 14, 30, 60, 90, 180, 365, float('inf')]
    else: # If custom bins are provided, ensure labels match
        default_labels = [f"Range {i+1}" for i in range(len(bins)-1)]


    job_age_days_series = pd.to_numeric(df_with_age['job_age_days'], errors='coerce')
    nan_count = job_age_days_series.isnull().sum()

    # Process only non-NaN values for pd.cut
    df_temp = pd.DataFrame({'job_age_days': job_age_days_series.dropna()})
    
    if df_temp.empty: # All were NaN or non-numeric
        if nan_count > 0: # If only NaNs, return a df with '未知' category
            return pd.DataFrame([{'freshness_range': '未知', 'count': nan_count}])
        return pd.DataFrame(columns=['freshness_range', 'count']) # No data at all

    # Apply pd.cut
    df_temp['freshness_range'] = pd.cut(
        df_temp['job_age_days'], 
        bins=default_bins, 
        labels=default_labels, 
        right=False,        # [lower, upper) interval
        include_lowest=True # Ensures the lowest value in bins is included
    )
    
    freshness_counts_df = df_temp['freshness_range'].value_counts().reset_index()
    freshness_counts_df.columns = ['freshness_range', 'count']
    
    if nan_count > 0: # Add NaN count as '未知' if there were any
        unknown_df = pd.DataFrame([{'freshness_range': '未知', 'count': nan_count}])
        freshness_counts_df = pd.concat([freshness_counts_df, unknown_df], ignore_index=True)

    # Set categorical order for proper sorting in charts
    final_labels_for_ordering = default_labels[:]
    if nan_count > 0 and '未知' not in final_labels_for_ordering : 
        final_labels_for_ordering.append('未知')
    
    # Filter categories to only those present in the data to avoid issues with pd.Categorical
    present_categories = [l for l in final_labels_for_ordering if l in freshness_counts_df['freshness_range'].unique()]
    
    freshness_counts_df['freshness_range'] = pd.Categorical(
        freshness_counts_df['freshness_range'], 
        categories=present_categories, 
        ordered=True
    )
    return freshness_counts_df.sort_values('freshness_range')