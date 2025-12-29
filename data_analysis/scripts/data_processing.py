# data_analysis/scripts/data_processing.py
"""
import pandas as pd
import numpy as np
import json
import os
import re
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
from collections import Counter
import traceback

# --- Path Setup ---
current_script_path = os.path.abspath(__file__)
scripts_dir = os.path.dirname(current_script_path)
data_analysis_dir = os.path.dirname(scripts_dir)
PROJECT_ROOT = os.path.dirname(data_analysis_dir)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

CRAWLER_ROOT_DIR = os.path.join(PROJECT_ROOT, 'crawler')
CRAWLER_MODULE_DIR_DA = os.path.join(CRAWLER_ROOT_DIR, 'crawler')
DATA_DIR_INSIDE_CRAWLER_DA = os.path.join(CRAWLER_MODULE_DIR_DA, 'data')
JOBS_FILE_DA = os.path.join(DATA_DIR_INSIDE_CRAWLER_DA, 'jobs.json')
TARGET_OPTIONS_FILE_DA = os.path.join(DATA_DIR_INSIDE_CRAWLER_DA, 'target_options.json') # For majors
MODELS_DIR = os.path.join(data_analysis_dir, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

# --- Import Shared Constants/Functions ---
try:
    from streamlit_app.utils import (
        DEFAULT_SKILL_KEYWORDS,
        preprocess_jobs_data as shared_preprocess_jobs_data
    )
    print("Successfully imported from streamlit_app.utils")
except ImportError as e:
    print(f"CRITICAL WARNING: Could not import from streamlit_app.utils: {e}.")
    print("Model training might use inconsistent preprocessing if utils.preprocess_jobs_data is not available.")
    print("Using fallback definitions and simplified preprocessing.")
    DEFAULT_SKILL_KEYWORDS = ['python', 'java', 'sql', '数据分析', '机器学习', 'c++', '前端', '后端', '测试', '运维', '产品经理', '项目管理', 'react', 'vue', 'angular', 'node.js', 'spring boot', 'django', 'flask', 'mongodb', 'redis', 'docker', 'kubernetes', 'aws', 'azure', 'linux']
    def shared_preprocess_jobs_data(df_raw, **kwargs):
        print("Warning: Using placeholder shared_preprocess_jobs_data. Data might not be fully preprocessed as in Streamlit app.")
        return df_raw.copy()


# --- Feature Engineering Helpers ---
TAGS_TO_EXCLUDE_GENERIC_DP = ['其他', '其它', '公司提供', '员工福利', '福利待遇', '待遇从优', '详情面议', '面议', '工作餐', '包吃', '包住', '包吃住', '食宿补贴', '住宿补贴', '班车', '交通方便', '地铁沿线', '不加班', '偶尔加班', '无', 'nan', '', '年假', '社保']
NON_ALPHANUMERIC_CHINESE_REGEX_DP = re.compile(r'[^\w\s\u4e00-\u9fff\+\#\.\-\&]')

# Constants for province extraction
CHINA_PROVINCES_REFERENCE = [
    "北京", "上海", "天津", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
    "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
    "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海",
    "内蒙古", "广西", "西藏", "宁夏", "新疆", "台湾", "香港", "澳门"
]
_POTENTIAL_LOCATION_COLUMNS_FOR_PROVINCE_EXTRACTION = ['province', 'city', 'work_place', 'location', 'company_address', 'address']

def get_standard_province_from_row(row):
    
   # Attempts to extract a standard province name from a DataFrame row.
   #  Looks in predefined potential location columns.
   # Returns a standard province name or '全国' if not found or ambiguous.
    
    province_name_map = {}
    for p in CHINA_PROVINCES_REFERENCE:
        province_name_map[p] = p 
        if p not in ["北京", "上海", "天津", "重庆", "内蒙古", "广西", "西藏", "宁夏", "新疆", "香港", "澳门", "台湾"]:
            province_name_map[p + "省"] = p
        if p in ["北京", "上海", "天津", "重庆"]:
            province_name_map[p + "市"] = p
        if p in ["内蒙古", "广西", "西藏", "宁夏", "新疆"]:
            province_name_map[p + "自治区"] = p
            if p == "新疆": province_name_map["新疆维吾尔自治区"] = p
            if p == "广西": province_name_map["广西壮族自治区"] = p
            if p == "宁夏": province_name_map["宁夏回族自治区"] = p
    
    sorted_map_keys = sorted(province_name_map.keys(), key=len, reverse=True)
    sorted_provinces_ref = sorted(CHINA_PROVINCES_REFERENCE, key=len, reverse=True)

    for col_name in _POTENTIAL_LOCATION_COLUMNS_FOR_PROVINCE_EXTRACTION:
        if col_name in row and pd.notna(row[col_name]):
            loc_str = str(row[col_name]).strip()
            if not loc_str:
                continue

            for map_key in sorted_map_keys:
                if loc_str.startswith(map_key): # Check if the location string starts with a known (potentially suffixed) province name
                    return province_name_map[map_key]
            
            for prov_ref in sorted_provinces_ref: # More general check if a base province name is contained
                if prov_ref in loc_str:
                    return prov_ref
    return '全国'


def clean_tag_dp(tag):
    if not isinstance(tag, str): tag = str(tag)
    tag = tag.strip().lower(); tag = NON_ALPHANUMERIC_CHINESE_REGEX_DP.sub('', tag)
    return re.sub(r'\s+', ' ', tag).strip()

def get_processed_tags_string_for_model(tags_input_series, top_n=30, min_freq=20):
    if not isinstance(tags_input_series, pd.Series) or tags_input_series.empty:
        return pd.Series([""] * len(tags_input_series), index=tags_input_series.index if isinstance(tags_input_series, pd.Series) else None, dtype=str)
    all_cleaned_tags_flat = []
    for item in tags_input_series.dropna():
        current_tags_for_job = []
        if isinstance(item, (list, tuple)): current_tags_for_job = item
        elif isinstance(item, str) and item.strip(): current_tags_for_job = [t.strip() for t in re.split(r'[,;，；\s|/]', item) if t.strip()]
        for tag in current_tags_for_job:
            cleaned = clean_tag_dp(tag)
            if cleaned and cleaned not in TAGS_TO_EXCLUDE_GENERIC_DP and 1 < len(cleaned) < 15:
                all_cleaned_tags_flat.append(cleaned)
    if not all_cleaned_tags_flat: return pd.Series([""] * len(tags_input_series), index=tags_input_series.index, dtype=str)
    tag_counts = Counter(all_cleaned_tags_flat)
    frequent_tags_set = {tag for tag, count in tag_counts.most_common(top_n * 2) if count >= min_freq}
    if len(frequent_tags_set) > top_n: frequent_tags_set = set(list(frequent_tags_set)[:top_n])
    elif not frequent_tags_set and tag_counts: frequent_tags_set = {tag for tag, _ in tag_counts.most_common(top_n)}
    print(f"Info: Using {len(frequent_tags_set)} tags as standard for 'company_tags_string': {list(frequent_tags_set)[:5]}...")
    def get_job_specific_tags_str(job_item):
        job_tags_present = []
        tags_to_check = []
        if isinstance(job_item, (list, tuple)): tags_to_check = job_item
        elif isinstance(job_item, str) and job_item.strip(): tags_to_check = [t.strip() for t in re.split(r'[,;，；\s|/]', job_item) if t.strip()]
        for tag in tags_to_check:
            cleaned = clean_tag_dp(tag)
            if cleaned in frequent_tags_set: job_tags_present.append(cleaned)
        return ",".join(sorted(list(set(job_tags_present))))
    return tags_input_series.apply(get_job_specific_tags_str)

def _extract_standard_major(major_text_cleaned, standard_majors_list_lower_sorted):
    if not isinstance(major_text_cleaned, str) or major_text_cleaned.lower() in ['未知', '不限', '']: return '不限专业'
    major_text_cleaned_lower = major_text_cleaned.lower()
    for std_major in standard_majors_list_lower_sorted:
        if std_major in major_text_cleaned_lower: return std_major
    return '其他专业'

# --- Standardized list for company scale (for OrdinalEncoder if used, or consistent OHE categories) ---
COMPANY_SCALE_ORDERED_CATEGORIES = [
    '未知规模', '少于50人', '50-150人', '150-499人', '500-999人', '1000-4999人', '5000人以上'
]
SCALE_MAP_TO_STANDARD = {
    re.compile(r"少于15人|1-49人|0-20人|20人以下"): "少于50人",
    re.compile(r"15-50人|50-99人|20-99人"): "50-150人",
    re.compile(r"50-150人|100-499人"): "150-499人",
    re.compile(r"150-500人|500-999人"): "500-999人",
    re.compile(r"500-2000人|1000-4999人|1000-9999人"): "1000-4999人",
    re.compile(r"2000人以上|5000以上|10000人以上"): "5000人以上",
}
def standardize_company_scale_feature(scale_input):
    if not isinstance(scale_input, str) or pd.isna(scale_input): return "未知规模"
    scale_str = str(scale_input).strip().lower()
    for pattern, standard_name in SCALE_MAP_TO_STANDARD.items():
        if pattern.search(scale_str):
            return standard_name
    if scale_str in [cat.lower() for cat in COMPANY_SCALE_ORDERED_CATEGORIES]:
        for cat_ordered in COMPANY_SCALE_ORDERED_CATEGORIES:
            if cat_ordered.lower() == scale_str:
                return cat_ordered
    return "未知规模"


def load_and_clean_data(file_path=JOBS_FILE_DA, target_options_path=TARGET_OPTIONS_FILE_DA):
    print(f"DEBUG: Loading raw data from: {os.path.abspath(file_path)}")
    if not os.path.exists(file_path): print(f"Error: Data file not found at {file_path}"); return pd.DataFrame()
    try:
        df_raw = pd.read_json(file_path, lines=file_path.endswith('.jsonl'), encoding='utf-8')
    except Exception as e: print(f"Error loading JSON data: {e}"); return pd.DataFrame()
    if df_raw.empty: print("Warning: Loaded raw data is empty."); return df_raw
    print(f"Successfully loaded {len(df_raw)} raw records.")

    print("Info: Applying shared_preprocess_jobs_data from streamlit_app.utils...")
    df = shared_preprocess_jobs_data(df_raw)
    
    if df.empty: print("Warning: Data is empty after shared_preprocess_jobs_data."); return df
    print(f"Shape after shared_preprocess_jobs_data: {df.shape}")

    if 'avg_month_pay' not in df.columns or df['avg_month_pay'].isnull().all():
        print("Error: 'avg_month_pay' is missing or all null after shared preprocessing. Cannot proceed.")
        return pd.DataFrame()
    df = df[df['avg_month_pay'] > 0].copy()
    if df.empty: print("Warning: No valid salary data (avg_month_pay > 0)."); return df

    # 1. Province (ensure 'province_clean' is the column name)
    if 'province_clean' not in df.columns:
        print("Warning: 'province_clean' not found from shared_preprocess_jobs_data. Attempting to derive.")
        # The function get_standard_province_from_row is now defined above
        df['province_clean_temp_derived'] = df.apply(lambda row: get_standard_province_from_row(row), axis=1)
        df.rename(columns={'province_clean_temp_derived': 'province_clean'}, inplace=True)
    # Standardize province_clean regardless of its source (shared_preprocess or derived)
    df['province_clean'] = df['province_clean'].astype(str).str.lower().str.strip().replace(['nan', 'none', 'null', ''], '全国')
    df.loc[df['province_clean'] == '', 'province_clean'] = '全国' # Ensure empty strings also become '全国'


    # 2. Company Scale (ensure 'company_scale_feature' is the column name)
    scale_source_col = None
    if 'company_scale_cat' in df.columns and df['company_scale_cat'].notna().any() and df['company_scale_cat'].astype(str).nunique() > 1:
        scale_source_col = 'company_scale_cat'
    elif 'company_scale_cleaned' in df.columns and df['company_scale_cleaned'].notna().any() and df['company_scale_cleaned'].astype(str).nunique() > 1:
        scale_source_col = 'company_scale_cleaned'
    elif 'company_scale' in df.columns:
        scale_source_col = 'company_scale'
    
    if scale_source_col:
        df['company_scale_feature'] = df[scale_source_col].astype(str).apply(standardize_company_scale_feature)
        print(f"Info: Created 'company_scale_feature' from '{scale_source_col}'.")
    else:
        df['company_scale_feature'] = "未知规模"
        print("Warning: No suitable source for company_scale_feature, defaulted to '未知规模'.")
    df['company_scale_feature'] = pd.Categorical(df['company_scale_feature'], categories=COMPANY_SCALE_ORDERED_CATEGORIES, ordered=True)
    df['company_scale_feature'] = df['company_scale_feature'].fillna('未知规模')


    # 3. Degree Name (ensure 'degree_name' is the column name)
    if 'degree_name' not in df.columns: df['degree_name'] = '学历不限'
    df['degree_name'] = df['degree_name'].astype(str).str.lower().str.strip().replace(['nan', 'none', 'null', '', '不限', '无', '未知'], '学历不限')

    # 4. Processed Major (ensure 'processed_major' is the column name)
    standard_majors_lower_sorted = []
    try:
        if os.path.exists(target_options_path):
            with open(target_options_path, 'r', encoding='utf-8') as f: target_data = json.load(f)
            major_list_json = target_data.get('collegmajor', [])
            if isinstance(major_list_json, list):
                raw_majors = [item['name'] for item in major_list_json if isinstance(item, dict) and 'name' in item and isinstance(item['name'], str) and item['name'].strip()]
                if raw_majors: valid_majors = [m.lower().strip() for m in raw_majors if m.strip()]; standard_majors_lower_sorted = sorted(list(set(valid_majors)), key=len, reverse=True)
        if not standard_majors_lower_sorted: print("Warning: No standard majors for mapping from target_options.json.")
    except Exception as e: print(f"Warning: Error loading/processing majors: {e}")
    
    if 'major_required' not in df.columns: df['major_required'] = ''
    df['processed_major'] = df['major_required'].astype(str).apply(lambda x: _extract_standard_major(x, standard_majors_lower_sorted))
    df['processed_major'] = df['processed_major'].astype(str).str.lower().str.strip()


    # 5. Skills Text (ensure 'skills_text_for_model' is the column name)
    if 'extracted_skills_list' in df.columns and df['extracted_skills_list'].apply(lambda x: isinstance(x, (list, tuple)) and len(x)>0).any():
        print("Info: Using 'extracted_skills_list' (filtered by DEFAULT_SKILL_KEYWORDS) for skills_text_for_model.")
        default_skills_lower_set = {skill.lower() for skill in DEFAULT_SKILL_KEYWORDS}
        df['skills_text_for_model'] = df['extracted_skills_list'].apply(
            lambda x_list: " ".join(sorted(list(set(str(s).lower().strip() for s in x_list if str(s).lower().strip() in default_skills_lower_set)))).strip()
            if isinstance(x_list, (list, tuple)) else "" )
    else:
        print("Info: Generating 'skills_text_for_model' from 'job_name' & 'major_required' using DEFAULT_SKILL_KEYWORDS.")
        df['source_text_for_skills'] = df['job_name'].fillna('') + " " + df['major_required'].fillna('')
        keywords_lower = [kw.lower() for kw in DEFAULT_SKILL_KEYWORDS]
        df['skills_text_for_model'] = df['source_text_for_skills'].apply(
            lambda text: " ".join(sorted(list(set(kw for kw in keywords_lower if kw in str(text).lower())))) )
        df.drop(columns=['source_text_for_skills'], inplace=True, errors='ignore')
    df['skills_text_for_model'] = df['skills_text_for_model'].astype(str).str.lower().str.strip()


    # 6. Company Tags String (ensure 'company_tags_string' is the column name)
    tags_source_column = 'tags_list' if 'tags_list' in df.columns and df['tags_list'].apply(lambda x: isinstance(x, (list, tuple))).any() else 'company_tags'
    if tags_source_column not in df.columns:
        print(f"Warning: Tags source column '{tags_source_column}' not found. Defaulting tags_string to empty.")
        df['company_tags_string'] = ""
    else:
        print(f"Info: Using column '{tags_source_column}' for 'company_tags_string' generation.")
        df['company_tags_string'] = get_processed_tags_string_for_model(df[tags_source_column])
    df['company_tags_string'] = df['company_tags_string'].astype(str).str.lower().str.strip()

    # 7. Other categoricals (ensure correct names and cleaning)
    for col_name, default_unknown in [('job_catory', '未知职位类别'), ('company_property', '未知公司性质'), ('job_industry', '未知行业')]:
        if col_name not in df.columns: df[col_name] = default_unknown
        df[col_name] = df[col_name].astype(str).str.lower().str.strip().replace(['nan', 'none', 'null', '', '不限', '无'], default_unknown)
        df.loc[df[col_name] == '', col_name] = default_unknown # Ensure empty strings also become default


    # 8. Numerical (ensure 'head_count' is the name)
    if 'head_count' not in df.columns: df['head_count'] = 1
    df['head_count'] = pd.to_numeric(df['head_count'], errors='coerce').fillna(1).astype(int)


    # --- Create combined_text_features for model input ---
    df['combined_text_features'] = (
        df['job_name'].fillna('未知职位') + " " +
        df['job_catory'].fillna('未知职位类别') + " " +
        df['skills_text_for_model'].fillna('') + " " +
        df['company_tags_string'].fillna('') + " " +
        df['job_industry'].fillna('未知行业') + " " +
        df['processed_major'].fillna('不限专业')
    )
    df['combined_text_features'] = df['combined_text_features'].str.replace(r'\s+', ' ', regex=True).str.strip()

    final_model_input_features = [
        'combined_text_features',
        'job_catory',
        'province_clean',
        'degree_name',
        'company_scale_feature',
        'company_property',
        'processed_major',
        'head_count',
        'job_industry'
    ]
    
    cols_to_return_for_training = final_model_input_features + ['avg_month_pay']
    
    missing_final_cols = [col for col in final_model_input_features if col not in df.columns]
    if missing_final_cols:
        print(f"FATAL Error: Critical model input features are missing from DataFrame: {missing_final_cols}")
        print(f"Available columns before final selection: {df.columns.tolist()}")
        # Attempt to fill missing crucial columns with default placeholder if absolutely necessary
        # This is a last resort to prevent crashing but indicates a data pipeline issue.
        for col_to_fill in missing_final_cols:
            print(f"Attempting to fill missing column '{col_to_fill}' with a default placeholder.")
            if col_to_fill == 'province_clean': df[col_to_fill] = '全国'
            elif col_to_fill == 'company_scale_feature': df[col_to_fill] = '未知规模'
            # Add other critical columns with appropriate defaults if this strategy is chosen
            else: df[col_to_fill] = '未知' # Generic placeholder
            df[col_to_fill] = df[col_to_fill].astype(str) # Ensure string type for consistency
        # Re-check after attempting to fill
        missing_final_cols = [col for col in final_model_input_features if col not in df.columns]
        if missing_final_cols:
             print(f"FATAL Error persists: Critical model input features still missing: {missing_final_cols}")
             return pd.DataFrame()


    df_model_ready = df[cols_to_return_for_training].copy()

    print(f"Data processing complete. Shape of data for model training: {df_model_ready.shape}")
    if not df_model_ready.empty:
        print("Sample of df_model_ready head:"); print(df_model_ready.head())
        # Final check for NaNs in feature columns before passing to preprocessor
        feature_cols_in_model_ready = [col for col in final_model_input_features if col in df_model_ready.columns]
        for col in feature_cols_in_model_ready:
            if df_model_ready[col].isnull().any():
                print(f"Warning: Column '{col}' in df_model_ready contains NaNs before preprocessor fitting.")
                # Apply a generic fill for safety, though this should ideally be handled earlier
                if pd.api.types.is_numeric_dtype(df_model_ready[col]):
                    df_model_ready[col] = df_model_ready[col].fillna(df_model_ready[col].median() if df_model_ready[col].median() is not np.nan else 0)
                else: # Assume string/categorical
                    df_model_ready[col] = df_model_ready[col].fillna('未知_placeholder')
        print("NaN counts in df_model_ready (should be 0 for features after final checks):"); print(df_model_ready[feature_cols_in_model_ready].isnull().sum())
    return df_model_ready


def create_feature_transformer(df_train,
                               text_feature_col='combined_text_features',
                               categorical_cols=None, 
                               numerical_cols=None):
    if df_train.empty: print("Error: Training DataFrame for preprocessor is empty."); return None, []
    
    if categorical_cols is None:
        categorical_cols = ['job_catory', 'province_clean', 'degree_name', 'company_scale_feature', 
                            'company_property', 'processed_major', 'job_industry']
    if numerical_cols is None: numerical_cols = ['head_count']

    categorical_cols = [col for col in categorical_cols if col in df_train.columns]
    numerical_cols = [col for col in numerical_cols if col in df_train.columns]
    if text_feature_col not in df_train.columns: text_feature_col = None

    transformers_list = []
    if text_feature_col and df_train[text_feature_col].notna().any():
        # Ensure it's string type and fill NaNs before TF-IDF
        df_train.loc[:, text_feature_col] = df_train[text_feature_col].astype(str).fillna('')
        tfidf_vectorizer = TfidfVectorizer(max_features=300, ngram_range=(1, 1), min_df=10, token_pattern=r'(?u)\b\w+\b') # Allow single characters if they are words
        transformers_list.append((f'tfidf', tfidf_vectorizer, text_feature_col))
    else: print(f"Warning: Text feature column '{text_feature_col}' not used for TF-IDF.")

    valid_categorical_cols_for_ohe = []
    for col in categorical_cols:
        df_train.loc[:, col] = df_train[col].astype(str).fillna('未知_cat_placeholder') # Ensure string and fill NaNs
        MAX_OHE_CATEGORIES = 15 
        if col in ['province_clean', 'processed_major', 'job_catory', 'job_industry']: 
            counts = df_train[col].value_counts()
            if len(counts) > MAX_OHE_CATEGORIES:
                categories_to_keep = counts.nlargest(MAX_OHE_CATEGORIES -1).index # -1 for 'Other'
                df_train.loc[:, col] = df_train[col].apply(lambda x: x if x in categories_to_keep else f'其他_{col}')
                print(f"Info: Grouped less frequent in '{col}'. Kept top {MAX_OHE_CATEGORIES-1} and '其他_{col}'.")
        if df_train[col].nunique(dropna=False) > 1 : valid_categorical_cols_for_ohe.append(col)
        else: print(f"Info: Categorical column '{col}' has no/low variance; skipping OHE.")

    if valid_categorical_cols_for_ohe:
        print("\nFinal Cardinality for OHE:"); [print(f"  {c}: {df_train[c].nunique(dropna=False)}") for c in valid_categorical_cols_for_ohe]
        # min_frequency=0.01 can be quite high, ensure it doesn't eliminate too many. Max_categories is more direct.
        onehot_encoder = OneHotEncoder(handle_unknown='infrequent_if_exist', sparse_output=True, min_frequency=5, max_categories=MAX_OHE_CATEGORIES)
        transformers_list.append(('onehot', onehot_encoder, valid_categorical_cols_for_ohe))
    else: print("Warning: No valid categorical columns for OneHotEncoding.")

    valid_numerical_cols = []
    for col in numerical_cols:
        df_train.loc[:, col] = pd.to_numeric(df_train[col], errors='coerce')
        median_val = df_train[col].median()
        df_train.loc[:, col] = df_train[col].fillna(median_val if pd.notna(median_val) else 0)
        if pd.api.types.is_numeric_dtype(df_train[col]) and df_train[col].notna().any():
            if df_train[col].nunique() < 2: print(f"Warning: Num col '{col}' has low variance.")
            valid_numerical_cols.append(col)
        else: print(f"Info: Num col '{col}' not suitable for scaling.")
    if valid_numerical_cols:
        num_pipeline = Pipeline([('scaler', StandardScaler(with_mean=False))])
        transformers_list.append(('num', num_pipeline, valid_numerical_cols))
    else: print("Warning: No valid numerical columns for Scaling.")

    if not transformers_list: print("Error: No transformers added."); return None, []
    
    preprocessor = ColumnTransformer(transformers=transformers_list, remainder='drop', sparse_threshold=0.3)
    print("Fitting preprocessor...")
    try:
        df_fit_subset = df_train.copy() 
        
        final_cols_for_fitting = []
        if text_feature_col and text_feature_col in df_fit_subset.columns: final_cols_for_fitting.append(text_feature_col)
        final_cols_for_fitting.extend(col for col in valid_categorical_cols_for_ohe if col in df_fit_subset.columns)
        final_cols_for_fitting.extend(col for col in valid_numerical_cols if col in df_fit_subset.columns)
        final_cols_for_fitting = list(dict.fromkeys(final_cols_for_fitting)) # Unique and keep order

        if not final_cols_for_fitting:
            print("Error: No columns left for fitting preprocessor after validation checks.")
            return None, []

        df_fit_subset_final = df_fit_subset[final_cols_for_fitting]
        
        # Final explicit NaN handling on the subset for fitting, ensuring correct types
        if text_feature_col and text_feature_col in df_fit_subset_final.columns:
             df_fit_subset_final.loc[:, text_feature_col] = df_fit_subset_final[text_feature_col].astype(str).fillna('')
        for col in valid_categorical_cols_for_ohe:
            if col in df_fit_subset_final.columns:
                df_fit_subset_final.loc[:, col] = df_fit_subset_final[col].astype(str).fillna('未知_cat_placeholder')
        for col in valid_numerical_cols:
            if col in df_fit_subset_final.columns:
                df_fit_subset_final.loc[:, col] = pd.to_numeric(df_fit_subset_final[col], errors='coerce')
                median_fit = df_fit_subset_final[col].median()
                df_fit_subset_final.loc[:, col] = df_fit_subset_final[col].fillna(median_fit if pd.notna(median_fit) else 0)
            
        preprocessor.fit(df_fit_subset_final)
        print("Preprocessor fitted successfully.")
    except Exception as e:
        print(f"Error fitting preprocessor: {e}"); traceback.print_exc(); return None, []
    
    feature_names_out = []
    try:
        # df_for_get_names = df_fit_subset_final # Use the exact df subset used for fitting
        # Use a small sample of the data that was fit to get feature names
        # This data must have undergone the same transformations (like grouping rare categories)
        # as df_fit_subset_final
        if not df_fit_subset_final.empty:
            sample_for_names = df_fit_subset_final.head()

            # Ensure sample_for_names also has the 'Other_col' type categories if they were created
            # This should already be the case if df_fit_subset_final was correctly prepared.

            # We need to make sure the OHE in the preprocessor can generate names.
            # It uses the `input_features` argument for OHE.

            for name_trans, trans_obj, Pcols_list_internal in preprocessor.transformers_:
                if name_trans == 'remainder' or name_trans == '_drop': continue # Sklearn >= 1.1 uses _drop for remainder='drop'

                current_cols_for_names = [Pcols_list_internal] if isinstance(Pcols_list_internal, str) else Pcols_list_internal
                
                # Filter Pcols_list_internal to only those present in sample_for_names.columns
                # This ensures that get_feature_names_out gets the correct column names for OHE.
                valid_input_features_for_ohe = [col for col in current_cols_for_names if col in sample_for_names.columns]


                if hasattr(trans_obj, 'get_feature_names_out'):
                    if name_trans.startswith('tfidf'): # TFIDF doesn't take input_features param
                        feature_names_out.extend(trans_obj.get_feature_names_out())
                    elif isinstance(trans_obj, OneHotEncoder): # OHE needs input_features
                         if valid_input_features_for_ohe: # Only if there are valid columns for this OHE step
                            feature_names_out.extend(trans_obj.get_feature_names_out(input_features=valid_input_features_for_ohe))
                         else: # Fallback if OHE was on columns not in sample_for_names (should not happen)
                            # This part is tricky. If OHE was fitted on columns X,Y
                            # but sample_for_names only has X, get_feature_names_out([X]) might be wrong or fail.
                            # It's better to ensure sample_for_names has all columns the transformer expects.
                            # For now, we assume valid_input_features_for_ohe is correct.
                            print(f"Warning: OHE '{name_trans}' had no valid input features from sample_for_names for get_feature_names_out. Original cols: {Pcols_list_internal}")
                    elif isinstance(trans_obj, Pipeline) and name_trans == 'num': # For numerical pipeline
                         # The pipeline itself doesn't have get_feature_names_out, but its final step (scaler) doesn't change names.
                         # So, the original column names are the feature names.
                         feature_names_out.extend(valid_input_features_for_ohe) # Use the filtered list
                    else: # Other transformers that might have get_feature_names_out
                        try:
                            feature_names_out.extend(trans_obj.get_feature_names_out(input_features=valid_input_features_for_ohe if valid_input_features_for_ohe else None))
                        except TypeError: # some transformers might not accept input_features
                             feature_names_out.extend(trans_obj.get_feature_names_out())
                elif name_trans == 'num': # Specifically for the numerical pipeline if get_feature_names_out is not found on pipeline
                     feature_names_out.extend(valid_input_features_for_ohe)
                else: # Fallback for transformers without get_feature_names_out (e.g. simple scaler directly in ColumnTransformer)
                    feature_names_out.extend(valid_input_features_for_ohe)

        if not feature_names_out and not df_fit_subset_final.empty : # If still no names, generate generic ones
            print("Warning: Failed to get specific feature names. Generating generic names.")
            num_tf_features = preprocessor.transform(df_fit_subset_final.head(1)).shape[1]
            feature_names_out = [f"feature_{i}" for i in range(num_tf_features)]

    except Exception as e_fn:
        print(f"Warning: Could not get all feature names: {e_fn}"); traceback.print_exc()
        try: # Fallback: generate generic feature names based on transformed shape
            if 'df_fit_subset_final' in locals() and not df_fit_subset_final.empty:
                 num_tf_features = preprocessor.transform(df_fit_subset_final.head(1)).shape[1]
                 feature_names_out = [f"feature_{i}" for i in range(num_tf_features)]
            else: feature_names_out = [] # Should not happen if preprocessor fitted
        except Exception as e_gen_names:
             print(f"Error generating fallback feature names: {e_gen_names}")
             feature_names_out = []
    return preprocessor, feature_names_out


if __name__ == '__main__':
    print("--- Running data_processing.py ---")
    df_model_ready = load_and_clean_data()

    if not df_model_ready.empty and 'avg_month_pay' in df_model_ready.columns:
        target_col = 'avg_month_pay'
        X_for_preprocessor = df_model_ready.drop(columns=[target_col], errors='ignore')

        print(f"\nShape of X_for_preprocessor (input to create_feature_transformer): {X_for_preprocessor.shape}")
        if not X_for_preprocessor.empty:
            print("Columns in X_for_preprocessor (these go into the transformer):", X_for_preprocessor.columns.tolist())
            # Ensure no NaNs in X_for_preprocessor just before creating transformer, critical for fit.
            for col in X_for_preprocessor.columns:
                if X_for_preprocessor[col].isnull().any():
                    print(f"Warning: Column '{col}' in X_for_preprocessor has NaNs before create_feature_transformer.")
                    if pd.api.types.is_numeric_dtype(X_for_preprocessor[col]):
                        median_val = X_for_preprocessor[col].median()
                        X_for_preprocessor[col] = X_for_preprocessor[col].fillna(median_val if pd.notna(median_val) else 0)
                    else: # Assume string/categorical/text
                        X_for_preprocessor[col] = X_for_preprocessor[col].astype(str).fillna('未知_main_fill')


        preprocessor, transformed_feature_names = create_feature_transformer(X_for_preprocessor.copy()) # Pass a copy

        if preprocessor:
            joblib.dump(preprocessor, os.path.join(MODELS_DIR, 'salary_preprocessor.pkl'))
            print(f"\nPreprocessor saved to {os.path.join(MODELS_DIR, 'salary_preprocessor.pkl')}")
            
            with open(os.path.join(MODELS_DIR, 'salary_feature_names.json'), 'w', encoding='utf-8') as f:
                json.dump(list(transformed_feature_names), f) # Ensure it's a list for JSON
            print(f"Transformed feature names saved ({len(transformed_feature_names)} features). Sample: {list(transformed_feature_names)[:10]}")

            raw_input_cols = X_for_preprocessor.columns.tolist() 
            with open(os.path.join(MODELS_DIR, 'salary_feature_names_raw_input.json'), 'w', encoding='utf-8') as f:
                 json.dump(raw_input_cols, f)
            print(f"Raw input feature names for preprocessor saved ({len(raw_input_cols)} features).")
            print("Raw input features expected by preprocessor:", raw_input_cols)
        else:
            print("Preprocessor creation failed.")
    else:
        print("No data processed by load_and_clean_data or target 'avg_month_pay' not found.")

"""
# data_analysis/scripts/data_processing.py
import pandas as pd
import numpy as np
import json
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib # 用于保存和加载对象

# --- 路径定义 ---
# __file__ is data_analysis/scripts/data_processing.py
# scripts_dir is data_analysis/scripts/
scripts_dir = os.path.dirname(os.path.abspath(__file__))
# data_analysis_dir is data_analysis/
data_analysis_dir = os.path.dirname(scripts_dir)
# BASE_DIR_DA is PythonFinishWork/ (parent of data_analysis_dir)
BASE_DIR_DA = os.path.dirname(data_analysis_dir)

# 正确的路径拼接
CRAWLER_ROOT_DIR = os.path.join(BASE_DIR_DA, 'crawler')
CRAWLER_MODULE_DIR_DA = os.path.join(CRAWLER_ROOT_DIR, 'crawler')
DATA_DIR_INSIDE_CRAWLER_DA = os.path.join(CRAWLER_MODULE_DIR_DA, 'data')
JOBS_FILE_DA = os.path.join(DATA_DIR_INSIDE_CRAWLER_DA, 'jobs.json') # 或 jobs.jsonl

MODELS_DIR = os.path.join(data_analysis_dir, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)
# 可选：为 LabelEncoders 等创建子目录
# LABEL_ENCODERS_DIR = os.path.join(MODELS_DIR, 'label_encoders')
# os.makedirs(LABEL_ENCODERS_DIR, exist_ok=True)


def load_and_clean_data(file_path=JOBS_FILE_DA):
    
    #加载原始JSON/JSONL数据，并进行基础清洗和转换。
    #返回一个准备好进行特征工程的DataFrame。
    
    print(f"DEBUG: [data_processing.py] Attempting to load data from: {os.path.abspath(file_path)}")
    if not os.path.exists(file_path):
        print(f"Error: Data file not found at {file_path}")
        return pd.DataFrame()
    
    try:
        if file_path.endswith('.jsonl'):
            df = pd.read_json(file_path, lines=True, encoding='utf-8')
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path, encoding='utf-8')
        else:
            print(f"Error: Unsupported file format for {file_path}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error loading JSON data from {file_path}: {e}")
        return pd.DataFrame()

    if df.empty:
        print("Warning: Loaded data is empty.")
        return df
    
    print(f"Successfully loaded {len(df)} records from {file_path}")

    # 1. 确保关键列存在，并填充缺失值
    # (与 streamlit_app/utils.py 中的 preprocess_jobs_data 类似，但这里更侧重模型输入)
    required_cols_defaults = {
        'job_id': None, 'job_name': '未知', 'job_catory': '未知', 'job_industry': '未知',
        'high_month_pay': 0.0, 'low_month_pay': 0.0, 
        # 'publish_date': None, 'update_date': None, # 日期先不在这里转datetime，后续特征工程处理
        'company_name': '未知', 'area_code_name': '未知', 'company_scale': '未知',
        'degree_name': '不限', 'major_required': '', 'company_property': '未知',
        'company_tags': '', 'head_count': 1 # 假设招聘人数至少为1，如果缺失
    }
    for col, default_val in required_cols_defaults.items():
        if col not in df.columns:
            df[col] = default_val
        elif default_val is not None: # 对已存在的列，填充其NaN值
             if df[col].isnull().any():
                if isinstance(default_val, (int, float)):
                    df[col].fillna(default_val, inplace=True)
                else: # string or other
                    df[col].fillna(str(default_val), inplace=True)


    # 2. 处理薪资
    for col in ['low_month_pay', 'high_month_pay']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['avg_month_pay'] = df.apply(
        lambda row: (row['low_month_pay'] + row['high_month_pay']) / 2 if row['low_month_pay'] > 0 and row['high_month_pay'] > 0 else \
                    row['high_month_pay'] if row['high_month_pay'] > 0 else \
                    row['low_month_pay'] if row['low_month_pay'] > 0 else np.nan, # 无效薪资标记为NaN
        axis=1
    )
    # 过滤掉没有有效平均薪资的行 (这是目标变量，必须有效)
    df.dropna(subset=['avg_month_pay'], inplace=True)
    df = df[df['avg_month_pay'] > 0] # 确保薪资是正数

    if df.empty:
        print("Warning: No valid salary data after cleaning (all avg_month_pay were NaN or <=0).")
        return df

    # 3. 文本数据简单清洗 (转换为小写，去多余空格)
    text_cols_to_clean = ['job_name', 'job_catory', 'job_industry', 'company_name', 'area_code_name',
                          'major_required', 'company_tags', 'company_property', 'degree_name', 'company_scale']
    for col in text_cols_to_clean:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().str.strip()
            # 将明确表示空或“无”的常见字符串替换为统一的“未知”，以便后续处理
            df[col].replace(['nan', 'none', 'null', '', '不限', '无'], '未知', inplace=True)
        else: # 如果列在原始数据中完全不存在
            df[col] = '未知'


    # 4. 创建合并的文本特征 (用于TF-IDF等)
    # 确保所有参与合并的列都是字符串类型，并处理可能的NaN
    df['combined_text_features'] = (
        df.get('job_name', pd.Series(['未知'] * len(df), index=df.index)).fillna('未知').astype(str) + " " +
        df.get('job_catory', pd.Series(['未知'] * len(df), index=df.index)).fillna('未知').astype(str) + " " +
        df.get('major_required', pd.Series([''] * len(df), index=df.index)).fillna('').astype(str) + " " + # 专业和标签允许空
        df.get('company_tags', pd.Series([''] * len(df), index=df.index)).fillna('').astype(str) + " " +
        df.get('job_industry', pd.Series(['未知'] * len(df), index=df.index)).fillna('未知').astype(str) # 也加入行业信息
    )
    
    # 5. 数值型特征转换与填充 (例如 head_count)
    if 'head_count' in df.columns:
        df['head_count'] = pd.to_numeric(df['head_count'], errors='coerce').fillna(1) # 缺失的招聘人数默认为1
    else:
        df['head_count'] = 1


    print(f"Data loaded and cleaned. Shape: {df.shape}")
    # print("Sample of cleaned data:")
    # print(df[['job_name', 'avg_month_pay', 'combined_text_features', 'area_code_name', 'degree_name', 'head_count']].head())
    return df


def create_feature_transformer(df_train, 
                               text_feature_col='combined_text_features', 
                               categorical_cols=None, 
                               numerical_cols=None):
    #创建并拟合一个 ColumnTransformer 用于特征处理。
    #返回拟合好的 transformer 和处理后的特征名称。
    #df_train: 用于拟合预处理器的训练DataFrame。
    
    if df_train.empty:
        print("Error: Training DataFrame for preprocessor is empty.")
        return None, []

    # 默认的类别和数值特征列 (应基于你的数据探索来确定)
    if categorical_cols is None:
        categorical_cols = ['job_catory', 'job_industry', 'area_code_name', 
                            'company_scale', 'degree_name', 'company_property']
    if numerical_cols is None:
        numerical_cols = ['head_count'] # 确保 head_count 是数值型

    transformers_list = []
    
    # 文本特征处理 (TF-IDF)
    if text_feature_col in df_train.columns and df_train[text_feature_col].notna().any():
        # 可以考虑使用 jieba 进行中文分词，并传入 tokenizer 给 TfidfVectorizer
        # from sklearn.feature_extraction.text import HashingVectorizer # 也可以考虑
        tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,  # 限制特征数量，防止维度爆炸
            ngram_range=(1, 2),   # 同时考虑单个词和二元词组
            stop_words=None,      # 可以传入中文停用词列表
            min_df=2,             # 词语至少在2个文档中出现
            token_pattern=r"(?u)\b\w\w+\b" # 默认的token pattern可能不适合中文
        )
        transformers_list.append((f'tfidf_{text_feature_col}', tfidf_vectorizer, text_feature_col))
    else:
        print(f"Warning: Text feature column '{text_feature_col}' not found or all NaN in df_train.")


    # 类别特征处理 (One-Hot Encoding)
    valid_categorical_cols = [col for col in categorical_cols if col in df_train.columns and df_train[col].notna().any()]
    if valid_categorical_cols:
        onehot_encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False, drop=None)
        transformers_list.append(('onehot', onehot_encoder, valid_categorical_cols))
    else:
        print("Warning: No valid categorical columns found or all NaN in df_train for OneHotEncoding.")

    # 数值特征处理 (StandardScaler)
    valid_numerical_cols = [col for col in numerical_cols if col in df_train.columns and pd.api.types.is_numeric_dtype(df_train[col]) and df_train[col].notna().any()]
    if valid_numerical_cols:
        # 确保数值列是float，并处理NaN (在load_and_clean_data中已做部分处理)
        for col in valid_numerical_cols: # 再次确保
            df_train[col] = pd.to_numeric(df_train[col], errors='coerce').fillna(df_train[col].median())
        
        num_pipeline = Pipeline([('scaler', StandardScaler())])
        transformers_list.append(('num', num_pipeline, valid_numerical_cols))
    else:
        print("Warning: No valid numerical columns found or all NaN in df_train for Scaling.")


    if not transformers_list:
        print("Error: No transformers were added to ColumnTransformer. Check column names, types, and content.")
        return None, []

    preprocessor = ColumnTransformer(transformers=transformers_list, remainder='drop')
    
    print("Fitting preprocessor...")
    try:
        # 确保传递给 fit 的 DataFrame 不包含 NaN (除了文本列，TF-IDF可以处理)
        # 对于类别和数值列，应在 load_and_clean_data 或此处填充
        cols_for_fit = []
        if text_feature_col in df_train.columns: cols_for_fit.append(text_feature_col)
        cols_for_fit.extend(valid_categorical_cols)
        cols_for_fit.extend(valid_numerical_cols)
        
        df_fit_subset = df_train[cols_for_fit].copy() # 只取实际参与转换的列
        # 再次检查并填充这些特定列的NaN，以防万一
        for col in valid_categorical_cols:
            df_fit_subset[col].fillna('未知', inplace=True) # OHE 可以处理 '未知'
        for col in valid_numerical_cols:
            df_fit_subset[col].fillna(df_fit_subset[col].median(), inplace=True)


        if df_fit_subset.empty:
            print("Error: DataFrame subset for fitting preprocessor is empty.")
            return None, []
            
        preprocessor.fit(df_fit_subset)
        print("Preprocessor fitted successfully.")
    except Exception as e:
        print(f"Error fitting preprocessor: {e}")
        print("DataFrame info for fitting subset:")
        df_fit_subset.info()
        for col in df_fit_subset.columns:
            print(f"NaN count in {col}: {df_fit_subset[col].isnull().sum()}")
        return None, []

    # 获取特征名称
    feature_names_out = []
    try:
        for name, trans, Pcols in preprocessor.transformers_: # Pcols is the original column names list
            if name == 'remainder': continue # Skip remainder
            if hasattr(trans, 'get_feature_names_out'):
                if isinstance(trans, TfidfVectorizer):
                    feature_names_out.extend([f"tfidf_{fn}" for fn in trans.get_feature_names_out()])
                elif isinstance(trans, OneHotEncoder):
                    feature_names_out.extend(trans.get_feature_names_out(Pcols))
            elif isinstance(trans, Pipeline) and name == 'num': # For numerical pipeline
                feature_names_out.extend(Pcols) # Original numerical column names
            else: # Fallback for other transformers, or if get_feature_names_out is not available
                 # This might happen if trans is just a scaler not in a pipeline
                if isinstance(Pcols, str): Pcols = [Pcols] # Ensure Pcols is a list
                feature_names_out.extend(Pcols)


    except Exception as e_fn:
        print(f"Warning: Could not get all feature names from preprocessor: {e_fn}")
        # Fallback, though less informative
        try:
            num_transformed_features = preprocessor.transform(df_fit_subset.head(1)).shape[1]
            feature_names_out = [f"feature_{i}" for i in range(num_transformed_features)]
        except Exception as e_transform_fallback:
            print(f"Error during fallback feature name generation: {e_transform_fallback}")
            feature_names_out = []


    return preprocessor, feature_names_out


if __name__ == '__main__':
    print("--- Running data_processing.py ---")
    df = load_and_clean_data()
    
    if not df.empty and 'avg_month_pay' in df.columns:
        # 准备 X (特征) 和 y (目标)
        # 移除所有与薪资直接相关的列作为特征，以及ID类和原始文本列（如果已创建combined_text_features）
        target_col = 'avg_month_pay'
        potential_features = df.drop(columns=[target_col, 'low_month_pay', 'high_month_pay', 
                                              'job_id', 'company_id', 'source_url',
                                              'publish_date', 'update_date', # 使用解析后的日期特征
                                              'search_area_code', 'search_area_name', 
                                              'search_keyword', #'search_category_code', 
                                              'search_industry_code',
                                              'major_required', 'company_tags', # 已合并到 combined_text_features
                                              'job_name', #'area_code_name', # area_code_name 已被 one-hot, job_name 在 combined_text
                                              # 'job_catory', 'job_industry', # 这些会被one-hot或在combined_text
                                              # 'company_scale', 'degree_name', 'company_property' # 这些会被one-hot
                                              ], errors='ignore')
        y = df[target_col]

        print(f"Shape of X before creating transformer: {potential_features.shape}")
        # print("Columns in X before creating transformer:", potential_features.columns.tolist())

        # 创建并拟合预处理器 (在整个可用数据上拟合，因为这是 data_processing 脚本)
        # 在 train_salary_model.py 中，应该只在训练集上拟合
        preprocessor, feature_names = create_feature_transformer(potential_features.copy())

        if preprocessor:
            preprocessor_path = os.path.join(MODELS_DIR, 'salary_preprocessor_from_data_processing.pkl')
            joblib.dump(preprocessor, preprocessor_path)
            print(f"Preprocessor (fitted on all available data) saved to {preprocessor_path}")
            print(f"Number of features after preprocessing: {len(feature_names)}")
            if feature_names:
                 print("Sample feature names (first 10):", feature_names[:10])
            
            # 示例转换
            # X_processed_example = preprocessor.transform(potential_features.head())
            # print(f"Example processed data shape: {X_processed_example.shape}")
        else:
            print("Preprocessor creation failed in main block.")
    else:
        print("No data loaded or 'avg_month_pay' not found, skipping preprocessor creation.")

