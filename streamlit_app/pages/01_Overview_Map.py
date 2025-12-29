import sys
import os

# --- sys.path modification ---
current_page_script_dir = os.path.dirname(os.path.abspath(__file__))
streamlit_app_dir = os.path.dirname(current_page_script_dir)
project_root = os.path.dirname(streamlit_app_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- end sys.path modification ---

import streamlit as st
import pandas as pd
import json
import numpy as np # For quantile calculation robustness
from streamlit_app.utils import (
    load_json_data, preprocess_jobs_data, JOBS_FILE, DEFAULT_OPTIONS_FILE_PATH,
    get_top_n_counts, # get_average_salary, # Not explicitly used, but part of utils
    plot_bar_chart, plot_pie_chart,
    SKILL_REGEX_PATTERNS, extract_skills_from_text_series, get_skill_frequency
)
import plotly.express as px
from datetime import datetime

# --- 数据加载与预处理 ---
@st.cache_data(ttl=3600)
def load_and_prep_map_page_data():
    df_jobs_raw = load_json_data(JOBS_FILE)
    expected_geo_cols = ['name', 'longitude', 'latitude', 'code',
                           'level_original_json', 'geo_match_key_province',
                           'geo_match_key_city', 'processed_level', 'display_name']

    if df_jobs_raw.empty:
        st.error("无法加载岗位数据 (jobs.json)，页面无法渲染。")
        return pd.DataFrame(), pd.DataFrame(columns=expected_geo_cols)

    df_jobs = preprocess_jobs_data(df_jobs_raw)
    if df_jobs.empty:
        st.warning("岗位数据预处理后为空。")
        return df_jobs, pd.DataFrame(columns=expected_geo_cols)

    if 'job_name_and_major_text' in df_jobs.columns and 'extracted_skills_list' not in df_jobs.columns:
        if SKILL_REGEX_PATTERNS:
            df_jobs['extracted_skills_list'] = extract_skills_from_text_series(
                df_jobs['job_name_and_major_text'], SKILL_REGEX_PATTERNS
            )
        else:
            df_jobs['extracted_skills_list'] = pd.Series([()] * len(df_jobs), index=df_jobs.index, dtype=object)
    elif 'extracted_skills_list' not in df_jobs.columns:
         df_jobs['extracted_skills_list'] = pd.Series([()] * len(df_jobs), index=df_jobs.index, dtype=object)

    raw_geo_data_list = []
    if os.path.exists(DEFAULT_OPTIONS_FILE_PATH):
        with open(DEFAULT_OPTIONS_FILE_PATH, 'r', encoding='utf-8') as f:
            target_options_data = json.load(f)
            if 'citys' in target_options_data and isinstance(target_options_data['citys'], list):
                raw_geo_data_list = target_options_data['citys']
    else:
        st.warning(f"地理数据文件 ({os.path.basename(DEFAULT_OPTIONS_FILE_PATH)}) 未找到。")
        return df_jobs, pd.DataFrame(columns=expected_geo_cols)

    df_geo_data = pd.DataFrame(raw_geo_data_list)

    required_json_cols_for_geo = ['name', 'longitude', 'latitude', 'code', 'level']
    if df_geo_data.empty or not all(col in df_geo_data.columns for col in required_json_cols_for_geo):
        st.warning(f"地理数据不完整或格式错误 (必须包含: {', '.join(required_json_cols_for_geo)})。")
        return df_jobs, pd.DataFrame(columns=expected_geo_cols)

    df_geo_data = df_geo_data.dropna(subset=['longitude', 'latitude', 'level', 'name', 'code'])
    df_geo_data['longitude'] = pd.to_numeric(df_geo_data['longitude'], errors='coerce')
    df_geo_data['latitude'] = pd.to_numeric(df_geo_data['latitude'], errors='coerce')
    df_geo_data['level_original_json'] = df_geo_data['level'].astype(str).str.strip()
    df_geo_data = df_geo_data.dropna(subset=['longitude', 'latitude'])

    valid_json_levels = ['省', '市', '区', '县', '直辖市', '自治区', '特别行政区', '自治州', '地区', '盟', '兵团', '县级市']
    df_geo_data = df_geo_data[df_geo_data['level_original_json'].isin(valid_json_levels)]

    if df_geo_data.empty:
        st.warning("地理数据中没有有效的经纬度或可识别的层级信息。")
        return df_jobs, pd.DataFrame(columns=expected_geo_cols)

    PROVINCE_LIKE_DIRECT_MAP = {
        "北京市": "北京", "天津市": "天津", "上海市": "上海", "重庆市": "重庆",
        "内蒙古自治区": "内蒙古", "广西壮族自治区": "广西", "宁夏回族自治区": "宁夏",
        "新疆维吾尔自治区": "新疆", "西藏自治区": "西藏",
        "香港特别行政区": "香港", "澳门特别行政区": "澳门", "台湾省": "台湾"
    }
    SHORT_PROVINCE_NAMES_SET = set(list(PROVINCE_LIKE_DIRECT_MAP.values()) + [
        "河北","山西","辽宁","吉林","黑龙江","江苏","浙江","安徽","福建","江西",
        "山东","河南","湖北","湖南","广东","海南","四川","贵州","云南","陕西",
        "甘肃","青海"
    ])

    def standardize_geo_keys_from_json(original_name_series_val,
                                       json_level_from_file_series_val,
                                       code_series_val, # code not actively used in current logic but kept for signature
                                       province_map_arg,
                                       short_province_names_set_arg):
        name_s = str(original_name_series_val).strip()
        level_s = str(json_level_from_file_series_val).strip()

        prov_key_std = ""
        city_key_std = ""
        processed_level = ""

        if level_s in ["省", "直辖市", "自治区", "特别行政区", "盟", "兵团"]:
            processed_level = "province"
        elif level_s in ["市", "地区", "自治州", "县级市"]:
            processed_level = "city"
        elif level_s in ["区", "县"]:
            processed_level = "district"
        else:
            processed_level = "unknown" # Should ideally not happen due to valid_json_levels filter

        # Priority 1: Direct map (e.g. "北京市" -> "北京" for province and city keys)
        if name_s in province_map_arg:
            short_name = province_map_arg[name_s]
            prov_key_std = short_name
            city_key_std = short_name
            processed_level = "province" # Ensure level is province for these
        
        # Priority 2: Process based on original JSON level
        elif processed_level == "province":
            key = name_s
            for suffix in ['省', '自治区', '盟', '兵团', '特别行政区']: key = key.replace(suffix, '')
            # Specific handling for cases like "内蒙古自治区" if not caught by direct map
            if "内蒙古" in key and name_s == "内蒙古自治区": key = "内蒙古" 
            prov_key_std = key.strip()
            city_key_std = prov_key_std # For provinces, city key is same as province key
        
        elif processed_level == "city":
            name_for_city_processing = name_s
            name_for_prov_extraction = name_s
            extracted_prov_short_name = ""

            # Attempt to extract province part if city name is prefixed (e.g. "河北省石家庄市")
            for prov_full, prov_short in province_map_arg.items():
                if name_for_prov_extraction.startswith(prov_full):
                    extracted_prov_short_name = prov_short
                    name_for_city_processing = name_for_prov_extraction.replace(prov_full, "", 1).strip()
                    break
            
            if not extracted_prov_short_name: # If not found via direct map prefixes
                prov_candidate = ""
                # Check for standard suffixes like "省" or "自治区"
                if "省" in name_for_prov_extraction:
                    parts = name_for_prov_extraction.split("省", 1)
                    prov_candidate = parts[0]
                    name_for_city_processing = parts[1] if len(parts) > 1 else ""
                elif "自治区" in name_for_prov_extraction:
                    parts = name_for_prov_extraction.split("自治区", 1)
                    prov_candidate = parts[0]
                    name_for_city_processing = parts[1] if len(parts) > 1 else ""
                    # Standardize自治区 names if they match known patterns
                    if prov_candidate + "自治区" in province_map_arg:
                         prov_candidate = province_map_arg[prov_candidate + "自治区"]
                    elif "内蒙古" in prov_candidate and name_s.startswith("内蒙古自治区"):
                        prov_candidate = "内蒙古"
                elif "盟" in name_for_prov_extraction and name_s.startswith("内蒙古"): # e.g. 内蒙古阿拉善盟
                    prov_candidate = "内蒙古" # Province is 内蒙古
                    name_for_city_processing = name_s.replace("内蒙古","",1).strip() # City is 阿拉善盟

                extracted_prov_short_name = prov_candidate.strip()
            
            prov_key_std = extracted_prov_short_name.strip()

            # Standardize city name by removing suffixes
            city_name_to_standardize = name_for_city_processing.strip()
            city_suffixes_to_strip = ['市', '地区', '自治州', '盟', '县级市'] #区/县 unlikely for city level, but harmless
            for suffix in city_suffixes_to_strip:
                city_name_to_standardize = city_name_to_standardize.replace(suffix, '')
            city_key_std = city_name_to_standardize.strip()

            # Fallback: if province key is missing, and city key is a known short province name, use it
            if not prov_key_std and city_key_std in short_province_names_set_arg:
                prov_key_std = city_key_std
            # Fallback: if city key is missing (e.g. stripped to empty), but prov key is known short name, use it
            if not city_key_std and prov_key_std in short_province_names_set_arg:
                 city_key_std = prov_key_std
        
        elif processed_level == "district":
            # For districts, we primarily care about their name and trying to link to a province/city
            # This logic can be complex if full hierarchical matching is needed.
            # Simplified: district name itself becomes city_key (after stripping suffix)
            # Province key extraction from district name is harder and less critical for current map.
            
            district_name_stripped = name_s
            for suffix in ['区', '县']:
                district_name_stripped = district_name_stripped.replace(suffix, '')
            city_key_std = district_name_stripped.strip() # Using district name as a placeholder for city_key

            # Try to find province for district
            for prov_full, prov_short in province_map_arg.items():
                if name_s.startswith(prov_full): # e.g. "北京市海淀区" starts with "北京市"
                    prov_key_std = prov_short
                    # If district is in a direct municipality, its conceptual "city" is the municipality itself
                    if prov_key_std == province_map_arg.get(prov_full): # Ensure it's from direct map
                         city_key_std = prov_short # e.g. 海淀区 is in city "北京"
                    break
            # Further province derivation for districts could be added if needed

        return prov_key_std, city_key_std, processed_level

    standardized_data_list = []
    for idx, row_series in df_geo_data.iterrows():
        standardized_keys_tuple = standardize_geo_keys_from_json(
            row_series['name'],
            row_series['level_original_json'],
            row_series['code'],
            PROVINCE_LIKE_DIRECT_MAP,
            SHORT_PROVINCE_NAMES_SET
        )
        standardized_data_list.append(standardized_keys_tuple)

    df_standardized_keys = pd.DataFrame(standardized_data_list,
                                        columns=['geo_match_key_province', 'geo_match_key_city', 'processed_level_temp'],
                                        index=df_geo_data.index)

    df_geo_data = pd.concat([df_geo_data.reset_index(drop=True), df_standardized_keys.reset_index(drop=True)], axis=1)
    df_geo_data['processed_level'] = df_geo_data['processed_level_temp']
    df_geo_data.drop(columns=['processed_level_temp'], inplace=True)
    df_geo_data['display_name'] = df_geo_data['name'] # Original name for display

    # Re-ensure direct municipalities are correctly leveled and keyed after general processing
    # This acts as a final override for known province-level entities.
    for dm_full, dm_short in PROVINCE_LIKE_DIRECT_MAP.items():
        mask = df_geo_data['name'] == dm_full
        if mask.any():
            df_geo_data.loc[mask, 'geo_match_key_province'] = dm_short
            df_geo_data.loc[mask, 'geo_match_key_city'] = dm_short
            df_geo_data.loc[mask, 'processed_level'] = 'province'

    df_geo_data_final = df_geo_data[df_geo_data['processed_level'].isin(['province', 'city'])].copy()

    # Filter for valid province and city entries for matching
    prov_mask_final = (df_geo_data_final['processed_level'] == 'province') & \
                      (df_geo_data_final['geo_match_key_province'].astype(str).str.strip() != '') & \
                      (df_geo_data_final['geo_match_key_province'].notna())
    city_mask_final = (df_geo_data_final['processed_level'] == 'city') & \
                      (df_geo_data_final['geo_match_key_city'].astype(str).str.strip() != '') & \
                      (df_geo_data_final['geo_match_key_city'].notna()) & \
                      (df_geo_data_final['geo_match_key_province'].astype(str).str.strip() != '') & \
                      (df_geo_data_final['geo_match_key_province'].notna())

    df_geo_data_final = df_geo_data_final[prov_mask_final | city_mask_final].copy()
    
    # Deduplicate based on essential keys to ensure one geo entity per key combination
    # Prefer 'province' level if a name appears as both city and province with same keys
    # (e.g. Beijing as province vs. Beijing as city)
    df_geo_data_final = df_geo_data_final.sort_values('processed_level', ascending=True) # province then city
    df_geo_data_final = df_geo_data_final.drop_duplicates(
        subset=['geo_match_key_province', 'geo_match_key_city', 'processed_level'], keep='first'
    )
    # Also, ensure (lat, lon) is unique for a given display name if that's an issue
    df_geo_data_final = df_geo_data_final.drop_duplicates(subset=['display_name', 'latitude', 'longitude'], keep='first')


    if df_geo_data_final.empty:
        st.warning("处理后，地理数据中没有可识别为'省'或'市'级别并用于匹配的有效条目。")
        return df_jobs, pd.DataFrame(columns=expected_geo_cols)

    return df_jobs, df_geo_data_final


# --- 主页面函数 ---
def show_overview_map_page():
    st.title("🗺️ 地域市场洞察")

    df_jobs_map, df_geo_data_map_processed = load_and_prep_map_page_data()

    if not df_geo_data_map_processed.empty:
        with st.sidebar.expander("Debug: Processed Geo Data (load_and_prep)", expanded=False):
            st.dataframe(df_geo_data_map_processed[['name','code','level_original_json',
                                                    'geo_match_key_province', 'geo_match_key_city',
                                                    'processed_level', 'longitude', 'latitude', 'display_name']]
                         .sample(min(20, len(df_geo_data_map_processed)),
                                 replace=len(df_geo_data_map_processed) < 20 if len(df_geo_data_map_processed) > 0 else False))
    else:
        st.sidebar.warning("Processed geo data (df_geo_data_map_processed) is empty.")

    if not df_jobs_map.empty:
        with st.sidebar.expander("Debug: Job Data Geo Keys (from utils)", expanded=False):
            sample_size = min(20, len(df_jobs_map))
            if sample_size > 0:
                st.dataframe(df_jobs_map[['prinvce_code_nme', 'province_clean', 'search_area_name', 'area_code_name', 'city_clean']].sample(sample_size))
            else:
                st.caption("Job data is empty, cannot sample.")


    if os.path.exists(JOBS_FILE):
        try:
            st.caption(f"数据源: `{os.path.basename(JOBS_FILE)}` (最后修改: {datetime.fromtimestamp(os.path.getmtime(JOBS_FILE)).strftime('%Y-%m-%d %H:%M:%S')})")
        except Exception: st.caption(f"数据源: `{os.path.basename(JOBS_FILE)}` (无法获取最后修改时间)")

    st.sidebar.header("全局洞察过滤器")
    selected_category_map_page = "所有类别"
    selected_degree_map_page = "所有学历"

    map_display_df_base = df_jobs_map.copy() if not df_jobs_map.empty else pd.DataFrame()

    if not map_display_df_base.empty:
        job_catory_col = 'job_catory' if 'job_catory' in map_display_df_base.columns else None
        degree_name_cat_col = 'degree_name_cat' if 'degree_name_cat' in map_display_df_base.columns else None

        if job_catory_col:
            unique_categories_map_raw = map_display_df_base[job_catory_col].astype(str).dropna().unique()
            unique_categories_map_cleaned = sorted([val for val in unique_categories_map_raw if val.lower() != 'nan' and val.strip() != ''])
            unique_categories_map = ["所有类别"] + unique_categories_map_cleaned
            selected_category_map_page = st.sidebar.selectbox("筛选职位类别:", unique_categories_map, index=0, key="map_page_cat_filter_v12") # incremented key
        else: st.sidebar.warning("缺少 'job_catory' 列。")

        if degree_name_cat_col:
            unique_degrees_map_raw = map_display_df_base[degree_name_cat_col].astype(str).dropna().unique()
            unique_degrees_map_cleaned = sorted([val for val in unique_degrees_map_raw if val.lower() != 'nan' and val.strip() != ''])
            unique_degrees_map = ["所有学历"] + unique_degrees_map_cleaned
            selected_degree_map_page = st.sidebar.selectbox("筛选学历要求:", unique_degrees_map, index=0, key="map_page_degree_filter_v12") # incremented key
        else: st.sidebar.warning("缺少 'degree_name_cat' 列。")

        map_display_df = map_display_df_base.copy()
        if job_catory_col and selected_category_map_page != "所有类别":
            map_display_df = map_display_df[map_display_df[job_catory_col] == selected_category_map_page]
        if degree_name_cat_col and selected_degree_map_page != "所有学历":
            map_display_df = map_display_df[map_display_df[degree_name_cat_col] == selected_degree_map_page]
    else:
        st.sidebar.warning("岗位数据未加载或预处理失败，无法应用过滤器。")
        map_display_df = pd.DataFrame()

    if df_jobs_map.empty:
        st.error("未能加载岗位数据，页面无法继续。")
        return

    if map_display_df.empty:
        if (selected_category_map_page != "所有类别" or selected_degree_map_page != "所有学历") and not df_jobs_map.empty:
            st.warning("当前全局筛选条件下没有匹配的岗位数据。")
        elif df_jobs_map.empty:
             pass # Error already shown
        else:
             st.warning("岗位数据为空。")

    st.metric("当前筛选后岗位总数", f"{len(map_display_df):,}" if not map_display_df.empty else "0")
    st.markdown("---")
    st.subheader("岗位地理分布交互地图")

    map_level_options = ['省份分布']
    if 'city_clean' in map_display_df.columns and \
       'processed_level' in df_geo_data_map_processed.columns and \
       not df_geo_data_map_processed[df_geo_data_map_processed['processed_level'] == 'city'].empty:
        map_level_options.append('城市热点')

    current_map_level = st.radio(
        "选择地图显示层级:", options=map_level_options, index=0, key="map_level_select_v12", horizontal=True
    )

    selected_province_for_city_map_display_name = None
    if current_map_level == '城市热点' and \
       'province_clean' in map_display_df.columns and \
       not df_geo_data_map_processed.empty and \
       'processed_level' in df_geo_data_map_processed.columns and \
       'geo_match_key_province' in df_geo_data_map_processed.columns and \
       'display_name' in df_geo_data_map_processed.columns:

        province_keys_with_jobs_in_df = sorted(map_display_df['province_clean'].dropna().unique().tolist())
        province_display_names_for_zoom = ["全国热点城市"]

        df_geo_provinces_for_zoom = df_geo_data_map_processed[df_geo_data_map_processed['processed_level'] == 'province']
        if not df_geo_provinces_for_zoom.empty :
            prov_map = df_geo_provinces_for_zoom.set_index('geo_match_key_province')['display_name'].to_dict()
            valid_display_names = [
                prov_map.get(p_key) for p_key in province_keys_with_jobs_in_df if p_key and prov_map.get(p_key)
            ]
            province_display_names_for_zoom.extend(sorted(list(set(filter(None, valid_display_names)))))

        selected_province_for_city_map_display_name = st.selectbox(
            "聚焦省份 (查看其内城市热点):", province_display_names_for_zoom, index=0, key="map_province_zoom_select_v12"
        )

    map_plot_data_final = pd.DataFrame()

    if not map_display_df.empty:
        if current_map_level == '省份分布':
            if 'province_clean' in map_display_df.columns and \
               not df_geo_data_map_processed.empty and 'processed_level' in df_geo_data_map_processed.columns and \
               'geo_match_key_province' in df_geo_data_map_processed.columns:

                province_aggregates = map_display_df.groupby('province_clean', observed=False).agg(
                    job_count=('job_id', 'count'),
                    avg_salary=('avg_month_pay', lambda x: x[x > 0].mean() if pd.Series(x[x > 0]).notna().any() else 0)
                ).reset_index()
                province_aggregates['avg_salary'] = province_aggregates['avg_salary'].fillna(0)

                df_provinces_geo_plot = df_geo_data_map_processed[df_geo_data_map_processed['processed_level'] == 'province'].copy()
                if not df_provinces_geo_plot.empty:
                     map_plot_data_final = pd.merge(
                        df_provinces_geo_plot, province_aggregates,
                        left_on='geo_match_key_province', right_on='province_clean', how='left' # Use left to keep all geo provinces
                    )

        elif current_map_level == '城市热点':
            if 'city_clean' in map_display_df.columns and \
               not df_geo_data_map_processed.empty and 'processed_level' in df_geo_data_map_processed.columns and \
               'geo_match_key_city' in df_geo_data_map_processed.columns and \
               'geo_match_key_province' in df_geo_data_map_processed.columns:

                df_for_city_map_plot = map_display_df.copy()

                if selected_province_for_city_map_display_name and selected_province_for_city_map_display_name != "全国热点城市":
                    province_key_to_filter_city = None
                    df_geo_provinces_for_map_city = df_geo_data_map_processed[df_geo_data_map_processed['processed_level'] == 'province']
                    if not df_geo_provinces_for_map_city.empty:
                        prov_map_rev = df_geo_provinces_for_map_city.set_index('display_name')['geo_match_key_province'].to_dict()
                        province_key_to_filter_city = prov_map_rev.get(selected_province_for_city_map_display_name)

                    if province_key_to_filter_city and 'province_clean' in df_for_city_map_plot.columns:
                        df_for_city_map_plot = df_for_city_map_plot[df_for_city_map_plot['province_clean'] == province_key_to_filter_city]

                city_aggregates = df_for_city_map_plot.groupby('city_clean', observed=False).agg(
                    job_count=('job_id', 'count'),
                    avg_salary=('avg_month_pay', lambda x: x[x > 0].mean() if pd.Series(x[x > 0]).notna().any() else 0)
                ).reset_index()
                city_aggregates['avg_salary'] = city_aggregates['avg_salary'].fillna(0)

                df_cities_geo_plot = df_geo_data_map_processed[df_geo_data_map_processed['processed_level'] == 'city'].copy()
                if not df_cities_geo_plot.empty:
                    map_plot_data_final = pd.merge(
                        df_cities_geo_plot, city_aggregates,
                        left_on='geo_match_key_city', right_on='city_clean', how='inner' # Inner to only show cities with jobs
                    )
                    if selected_province_for_city_map_display_name == "全国热点城市" or not selected_province_for_city_map_display_name:
                        map_plot_data_final = map_plot_data_final.sort_values('job_count', ascending=False).head(75)
                    elif not map_plot_data_final.empty:
                         map_plot_data_final = map_plot_data_final.sort_values('job_count', ascending=False)

    if not map_plot_data_final.empty and 'longitude' in map_plot_data_final.columns and 'latitude' in map_plot_data_final.columns:
        map_plot_data_final['job_count'] = map_plot_data_final['job_count'].fillna(0).astype(int)
        map_plot_data_final['avg_salary_k'] = map_plot_data_final['avg_salary'].fillna(0) # Salary is already in K
        map_plot_data_final = map_plot_data_final[map_plot_data_final['job_count'] > 0] # Only plot if jobs exist

        if not map_plot_data_final.empty:
            zoom_level = 3.5
            map_center = {"lat": 35.8617, "lon": 104.1954} # China center
            title_suffix = "省份" if current_map_level == '省份分布' else \
                           (selected_province_for_city_map_display_name if selected_province_for_city_map_display_name and selected_province_for_city_map_display_name != "全国热点城市" else "全国城市")

            if current_map_level == '城市热点' and selected_province_for_city_map_display_name and \
               selected_province_for_city_map_display_name != "全国热点城市" and \
               'processed_level' in df_geo_data_map_processed.columns and 'display_name' in df_geo_data_map_processed.columns:

                prov_geo_info = df_geo_data_map_processed[
                    (df_geo_data_map_processed['display_name'] == selected_province_for_city_map_display_name) &
                    (df_geo_data_map_processed['processed_level'] == 'province')
                ]
                if not prov_geo_info.empty:
                    map_center = {"lat": prov_geo_info['latitude'].iloc[0], "lon": prov_geo_info['longitude'].iloc[0]}
                    zoom_level = 5.0 if len(map_plot_data_final) > 10 else 6.0

            # --- MODIFICATION FOR MAP COLOR ---
            plot_args_for_color = {}
            if 'avg_salary_k' in map_plot_data_final.columns:
                valid_salaries = map_plot_data_final['avg_salary_k'].dropna()
                if len(valid_salaries) >= 2: # Need at least 2 points for a robust range
                    s_min = np.percentile(valid_salaries, 5)  # 5th percentile
                    s_max = np.percentile(valid_salaries, 95) # 95th percentile

                    if s_min >= s_max - 0.1: # If 90% of data is too concentrated, or s_min == s_max
                        s_min_actual = valid_salaries.min()
                        s_max_actual = valid_salaries.max()
                        if s_min_actual < s_max_actual - 0.1: # If actual range offers more spread
                            s_min, s_max = s_min_actual, s_max_actual
                    
                    if s_min < s_max - 0.1: # Ensure there's a meaningful range
                        plot_args_for_color['range_color'] = [s_min, s_max]
                    # If range is still too small, try median as midpoint
                    elif pd.notna(valid_salaries.median()):
                         plot_args_for_color['color_continuous_midpoint'] = valid_salaries.median()
                    # If neither, Plotly will use its default min/max and midpoint logic
                
                elif len(valid_salaries) == 1 and pd.notna(valid_salaries.iloc[0]): # Single data point
                    # Set midpoint to the single value to ensure it gets a color.
                    plot_args_for_color['color_continuous_midpoint'] = valid_salaries.iloc[0]
            # --- END MODIFICATION FOR MAP COLOR ---

            fig = px.scatter_map(
                map_plot_data_final, lat="latitude", lon="longitude", size="job_count", color="avg_salary_k",
                hover_name="display_name",
                custom_data=['geo_match_key_province', 'geo_match_key_city', 'display_name'],
                hover_data={"job_count": True, "avg_salary_k": ":.1f", "latitude": False, "longitude": False},
                color_continuous_scale=px.colors.sequential.Plasma, # Changed color scale
                **plot_args_for_color, # Adds range_color or color_continuous_midpoint
                size_max=30, zoom=zoom_level, center=map_center, height=600,
                title=f"岗位在 {title_suffix} 的分布与平均薪资"
            )
            fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, coloraxis_colorbar_title="平均月薪 (K)")
            st.plotly_chart(fig, use_container_width=True)
        else: st.info(f"当前筛选和地图层级 ('{current_map_level}') 下，过滤后无数据显示点。")
    elif map_display_df.empty and not df_jobs_map.empty :
        st.info("当前筛选条件下无岗位数据，无法在地图上显示。")
    else:
        st.warning("无法准备足够的地理或岗位数据进行地图绘制（合并后为空或缺少关键列）。")
    st.markdown("---")

    st.subheader("省份详细洞察")
    province_options_for_detail_display = []
    province_display_to_key_map_detail = {}

    if 'province_clean' in map_display_df.columns and not map_display_df.empty and \
       not df_geo_data_map_processed.empty and \
       'processed_level' in df_geo_data_map_processed.columns and \
       'geo_match_key_province' in df_geo_data_map_processed.columns and \
       'display_name' in df_geo_data_map_processed.columns:

        provinces_with_jobs_keys = sorted(map_display_df['province_clean'].dropna().unique().tolist())
        df_geo_provinces_for_selectbox = df_geo_data_map_processed[df_geo_data_map_processed['processed_level'] == 'province']

        if not df_geo_provinces_for_selectbox.empty:
            key_to_display_map = df_geo_provinces_for_selectbox.set_index('geo_match_key_province')['display_name'].to_dict()
            for p_key in provinces_with_jobs_keys:
                display_name = key_to_display_map.get(p_key)
                if display_name:
                    province_options_for_detail_display.append(display_name)
                    province_display_to_key_map_detail[display_name] = p_key
            province_options_for_detail_display = sorted(list(set(province_options_for_detail_display)))

    if province_options_for_detail_display:
        selected_province_display_name_detail = st.selectbox(
            "选择省份进行详细分析:", options=province_options_for_detail_display, index=0, key="map_page_province_detail_select_v12" # incremented key
        )
        selected_province_key_filter = province_display_to_key_map_detail.get(selected_province_display_name_detail)

        if selected_province_key_filter and 'province_clean' in map_display_df.columns:
            df_province_detail_selected = map_display_df[map_display_df['province_clean'] == selected_province_key_filter].copy()
            if not df_province_detail_selected.empty:
                st.markdown(f"#### {selected_province_display_name_detail} (全局筛选: {selected_category_map_page}, {selected_degree_map_page})")

                jobs_in_prov = len(df_province_detail_selected)
                avg_salary_prov_val = df_province_detail_selected[df_province_detail_selected['avg_month_pay'] > 0]['avg_month_pay'].mean()
                median_salary_prov_val = df_province_detail_selected[df_province_detail_selected['avg_month_pay'] > 0]['avg_month_pay'].median()

                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("该省岗位数量", f"{jobs_in_prov:,}")
                col_m2.metric("该省平均月薪 (K)", f"{avg_salary_prov_val:,.1f}" if pd.notna(avg_salary_prov_val) else "N/A")
                col_m3.metric("该省中位数月薪 (K)", f"{median_salary_prov_val:,.1f}" if pd.notna(median_salary_prov_val) else "N/A")

                detail_tabs_prov = st.tabs(["热门城市/地区排行", "职位类别", "核心技能", "公司画像"])

                with detail_tabs_prov[0]: # 热门城市/地区排行
                    if 'city_clean' in df_province_detail_selected.columns:
                        top_cities_in_prov_raw = get_top_n_counts(df_province_detail_selected, 'city_clean', top_n=11) # Fetch 11

                        # --- MODIFICATION TO FILTER PROVINCE FROM CITY LIST ---
                        if not top_cities_in_prov_raw.empty:
                            city_values_to_filter_df = top_cities_in_prov_raw[['city_clean']].copy()
                            # Normalize city_clean for comparison (strip and string type)
                            city_values_to_filter_df['city_clean_norm'] = city_values_to_filter_df['city_clean'].astype(str).str.strip()

                            province_short_key = str(selected_province_key_filter).strip()
                            province_display_name_full = str(selected_province_display_name_detail).strip()

                            province_self_names = {province_short_key} # e.g., "云南"
                            province_self_names.add(province_display_name_full) # e.g., "云南省"
                            
                            # Add variations like "云南" from "云南省"
                            for suffix in ['省', '市', '自治区', '特别行政区']:
                                if province_display_name_full.endswith(suffix) and len(province_display_name_full) > len(suffix):
                                    province_self_names.add(province_display_name_full[:-len(suffix)])
                            
                            province_self_names = {name for name in province_self_names if name and name.lower() != 'nan'}

                            mask_is_not_province_self = ~city_values_to_filter_df['city_clean_norm'].isin(list(province_self_names))
                            top_cities_in_prov = top_cities_in_prov_raw[mask_is_not_province_self.values].head(10)
                        else:
                            top_cities_in_prov = pd.DataFrame(columns=top_cities_in_prov_raw.columns) # Empty df
                        # --- END MODIFICATION ---

                        if not top_cities_in_prov.empty:
                            city_display_names_in_prov_map = {}
                            if not df_geo_data_map_processed.empty and \
                               'processed_level' in df_geo_data_map_processed.columns and \
                               'geo_match_key_city' in df_geo_data_map_processed.columns and \
                               'display_name' in df_geo_data_map_processed.columns and \
                               'geo_match_key_province' in df_geo_data_map_processed.columns:

                                df_geo_cities_in_prov_for_display = df_geo_data_map_processed[
                                    (df_geo_data_map_processed['processed_level'] == 'city') &
                                    (df_geo_data_map_processed['geo_match_key_province'] == selected_province_key_filter)
                                ]
                                if not df_geo_cities_in_prov_for_display.empty:
                                    city_display_names_in_prov_map = df_geo_cities_in_prov_for_display.set_index('geo_match_key_city')['display_name'].to_dict()

                            top_cities_in_prov_display = top_cities_in_prov.copy()
                            top_cities_in_prov_display['city_display'] = top_cities_in_prov_display['city_clean'].map(city_display_names_in_prov_map).fillna(top_cities_in_prov_display['city_clean'])

                            plot_bar_chart(top_cities_in_prov_display, 'city_display', 'count', f"Top 10 热门招聘城市/地区", "城市/地区", "岗位数", orientation='h')
                        else: st.info(f"省份'{selected_province_display_name_detail}'内无有效的市/区级数据或筛选后为空。")
                    else: st.caption("缺少城市数据 ('city_clean'列)。")

                with detail_tabs_prov[1]:
                    job_catory_col = 'job_catory' if 'job_catory' in df_province_detail_selected.columns else None
                    if job_catory_col:
                        top_cats_province = get_top_n_counts(df_province_detail_selected, job_catory_col, top_n=7)
                        plot_bar_chart(top_cats_province, job_catory_col, 'count', f"Top 7 职位类别", "职位类别", "岗位数", orientation='h')
                    else: st.caption("缺少职位类别数据。")

                with detail_tabs_prov[2]:
                    if 'extracted_skills_list' in df_province_detail_selected.columns:
                        top_skills_province = get_skill_frequency(df_province_detail_selected, 'extracted_skills_list', top_n=10)
                        if not top_skills_province.empty:
                            plot_bar_chart(top_skills_province, 'skill', 'count', f"Top 10 核心技能需求", "技能", "提及次数", orientation='h')
                        else: st.info(f"省份'{selected_province_display_name_detail}'当前筛选条件下无技能数据。")
                    else: st.caption("缺少技能数据 (extracted_skills_list)。")

                with detail_tabs_prov[3]:
                    col_comp_prov1, col_comp_prov2 = st.columns(2)
                    company_scale_col_map_detail = 'company_scale_cat' if 'company_scale_cat' in df_province_detail_selected.columns else None
                    company_prop_col_map_detail = 'company_property' if 'company_property' in df_province_detail_selected.columns else None
                    with col_comp_prov1:
                        if company_scale_col_map_detail:
                            scales_province = get_top_n_counts(df_province_detail_selected, company_scale_col_map_detail, top_n=7)
                            plot_pie_chart(scales_province, company_scale_col_map_detail, 'count', "公司规模分布", hole=0.3)
                        else: st.caption("缺少公司规模数据。")
                    with col_comp_prov2:
                        if company_prop_col_map_detail:
                            properties_province = get_top_n_counts(df_province_detail_selected, company_prop_col_map_detail, top_n=7)
                            plot_pie_chart(properties_province, company_prop_col_map_detail, 'count', "公司性质分布", hole=0.3)
                        else: st.caption("缺少公司性质数据。")
            else:
                st.info(f"在当前全局筛选下，省份 '{selected_province_display_name_detail}' (匹配键: {selected_province_key_filter}) 没有数据。")
        else:
            st.warning(f"无法为选择的省份 '{selected_province_display_name_detail}' 找到用于筛选的内部键或该省在岗位数据中无记录。")
    else:
        st.info("当前筛选条件下，无省份可供选择进行详细分析。")

# --- 主执行块 ---
if __name__ == "__main__":
    if 'page_config_called_overview_map' not in st.session_state:
        st.set_page_config(page_title="地域市场洞察", layout="wide", page_icon="🗺️")
        st.session_state.page_config_called_overview_map = True
    show_overview_map_page()