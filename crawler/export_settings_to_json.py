# PythonFinishWork/crawler/export_settings_to_json.py
import json
import os
import sys

# __file__ is E:\MyProjects\pythonfinishwork\crawler\export_settings_to_json.py
# current_script_dir is E:\MyProjects\pythonfinishwork\crawler
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# project_root (PythonFinishWork) is the parent of current_script_dir
project_root = os.path.dirname(current_script_dir)

# Add project_root to sys.path so we can import 'crawler.crawler.settings'
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added to sys.path: {project_root}")


try:
    # 现在我们尝试从项目根目录的角度导入
    # 'crawler' 是 PythonFinishWork/crawler/
    # '.crawler' 是 PythonFinishWork/crawler/crawler/
    # '.settings' 是 PythonFinishWork/crawler/crawler/settings.py
    from crawler.crawler import settings as scrapy_settings
    print(f"Successfully imported settings from: {scrapy_settings.__file__}")
except ImportError as e:
    print(f"ImportError: {e}")
    print("Could not import 'crawler.crawler.settings'. Check your __init__.py files and PYTHONPATH.")
    print("Current sys.path:")
    for p in sys.path:
        print(p)
    # Provide a fallback or exit if settings cannot be loaded
    # For now, we'll use a dummy object to avoid further errors in this script
    class DummySettings:
        DEFAULT_TARGET_CITIES_LIST = [{"code": "fallback", "name": "Fallback City"}]
        DEFAULT_TARGET_KEYWORDS_LIST = [""]
        DEFAULT_TARGET_CATEGORY_CODES_LIST = [{"code": "fallback", "name": "Fallback Category"}]
        DEFAULT_TARGET_INDUSTRY_CODES_LIST = [{"code": "fallback", "name": "Fallback Industry"}]
    scrapy_settings = DummySettings()
    print("Using dummy fallback settings.")


output_data = {
    "cities": getattr(scrapy_settings, 'DEFAULT_TARGET_CITIES_LIST', []),
    "keywords": getattr(scrapy_settings, 'DEFAULT_TARGET_KEYWORDS_LIST', [""]),
    "categories": getattr(scrapy_settings, 'DEFAULT_TARGET_CATEGORY_CODES_LIST', []),
    "industries": getattr(scrapy_settings, 'DEFAULT_TARGET_INDUSTRY_CODES_LIST', [])
}

# 输出文件的路径应该是 PythonFinishWork/crawler/crawler/data/default_target_options.json
# current_script_dir is PythonFinishWork/crawler/
output_dir = os.path.join(current_script_dir, 'crawler', 'data') # Correct: PythonFinishWork/crawler/crawler/data/
os.makedirs(output_dir, exist_ok=True)
# 将输出文件名修改为 default_target_options.json 以匹配 utils.py 中的引用
output_file_path = os.path.join(output_dir, 'target_options.json') 

with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"Default target options exported to: {os.path.abspath(output_file_path)}")