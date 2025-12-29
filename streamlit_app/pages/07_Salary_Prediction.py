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
import joblib
import os
import json
import time
import traceback
import numpy as np

from streamlit_app.utils import (
    load_json_data,
    preprocess_jobs_data,
    JOBS_FILE,
    DEFAULT_OPTIONS_FILE_PATH,
    _load_standard_majors as utils_load_standard_majors,
    _map_to_standard_major as utils_map_to_standard_major,
    DEFAULT_SKILL_KEYWORDS,
    get_cleaned_company_tags_from_data # <<< --- IMPORT THE NEW FUNCTION
)

# --- 页面配置 ---
if 'page_config_called_predictor' not in st.session_state:
    st.set_page_config(page_title="职位薪资预测器", layout="wide", page_icon="💸")
    st.session_state.page_config_called_predictor = True

# --- 路径定义 ---
MODELS_DIR_APP = os.path.join(project_root, 'data_analysis', 'models')
MODEL_PATH = os.path.join(MODELS_DIR_APP, 'salary_predictor_model.pkl')
PREPROCESSOR_PATH = os.path.join(MODELS_DIR_APP, 'salary_preprocessor.pkl')
FEATURE_NAMES_PATH = os.path.join(MODELS_DIR_APP, 'salary_feature_names.json')

# --- 加载模型、预处理器和特征名 ---
@st.cache_resource
def load_prediction_assets():
    model, preprocessor, feature_names_from_file = None, None, None
    model_ok, preprocessor_ok, features_ok = False, False, False
    try:
        if os.path.exists(MODEL_PATH): model = joblib.load(MODEL_PATH); model_ok = True
        if os.path.exists(PREPROCESSOR_PATH): preprocessor = joblib.load(PREPROCESSOR_PATH); preprocessor_ok = True
        if os.path.exists(FEATURE_NAMES_PATH):
            with open(FEATURE_NAMES_PATH, 'r', encoding='utf-8') as f: feature_names_from_file = json.load(f)
            features_ok = True
    except Exception as e: print(f"Error loading prediction assets: {e}")
    return model, preprocessor, feature_names_from_file, model_ok, preprocessor_ok, features_ok

model, preprocessor, feature_names_json, model_ok, preprocessor_ok, features_ok = load_prediction_assets()

# --- 加载原始数据以获取选项列表 ---
@st.cache_data(ttl=3600)
def load_and_get_options_for_predictor():
    df_jobs_raw = load_json_data(JOBS_FILE)
    if df_jobs_raw.empty: return {"error": "Raw job data is empty"}, []

    df_jobs_for_options = preprocess_jobs_data(df_jobs_raw.copy())
    if df_jobs_for_options.empty: return {"error": "Processed job data is empty"}, []

    options = {}
    if 'province_clean' in df_jobs_for_options.columns and df_jobs_for_options['province_clean'].notna().any():
        province_vals = sorted(df_jobs_for_options['province_clean'].dropna().astype(str).unique().tolist())
        options['province_options'] = ["选择省份..."] + [val for val in province_vals if val.strip() != '']
    else:
        options['province_options'] = ["选择省份...", "北京", "上海", "广东", "浙江", "江苏"]

    company_scale_options_list = ["选择或输入..."]
    # Prioritize company_scale_cat if it's well-defined
    if 'company_scale_cat' in df_jobs_for_options.columns and \
       pd.api.types.is_categorical_dtype(df_jobs_for_options['company_scale_cat']) and \
       not df_jobs_for_options['company_scale_cat'].cat.categories.empty:
        cat_list = [str(cat).strip() for cat in df_jobs_for_options['company_scale_cat'].cat.categories if str(cat).strip()]
        company_scale_options_list.extend(cat_list)
    elif 'company_scale_cleaned' in df_jobs_for_options.columns and df_jobs_for_options['company_scale_cleaned'].notna().any():
        unique_scales = sorted(df_jobs_for_options['company_scale_cleaned'].dropna().astype(str).unique().tolist())
        company_scale_options_list.extend([val for val in unique_scales if val.strip() != ''])
    
    if len(company_scale_options_list) == 1: # Only "选择或输入..."
        company_scale_options_list.extend(['少于15人', '15-50人', '50-150人', '150-500人', '500-2000人', '2000人以上'])


    for col_key, display_name_col, fallback_options_if_empty in [
        ('job_catory', 'job_catory', ["技术", "产品", "设计", "运营", "市场"]),
        ('degree_name', 'degree_name', ["不限", "大专", "本科", "硕士", "博士"]),
        ('company_scale', 'company_scale_cat', company_scale_options_list[1:]), # Use populated list
        ('company_property', 'company_property', ["民营公司", "上市公司", "国企", "外资企业"])
    ]:
        if display_name_col in df_jobs_for_options.columns and df_jobs_for_options[display_name_col].notna().any():
            if col_key == 'company_scale':
                options[col_key] = company_scale_options_list # Already prepared
            else:
                unique_vals = []
                if pd.api.types.is_categorical_dtype(df_jobs_for_options[display_name_col]) and \
                   not df_jobs_for_options[display_name_col].cat.categories.empty:
                    cat_list_vals = [str(cat).strip() for cat in df_jobs_for_options[display_name_col].cat.categories if str(cat).strip()]
                    unique_vals = cat_list_vals
                else:
                    unique_vals_raw = sorted(df_jobs_for_options[display_name_col].dropna().astype(str).unique().tolist())
                    unique_vals = [val for val in unique_vals_raw if str(val).strip() != '']
                
                options[col_key] = ["选择或输入..."] + unique_vals if unique_vals else (["选择或输入..."] + fallback_options_if_empty)
        else:
             options[col_key] = ["选择或输入..."] + fallback_options_if_empty


    standard_majors_list_for_dropdown = []
    standard_majors_for_mapping_internal = utils_load_standard_majors(DEFAULT_OPTIONS_FILE_PATH)
    if standard_majors_for_mapping_internal:
        try:
            if os.path.exists(DEFAULT_OPTIONS_FILE_PATH):
                with open(DEFAULT_OPTIONS_FILE_PATH, 'r', encoding='utf-8') as f:
                    target_options_data = json.load(f)
                college_major_list = target_options_data.get('collegmajor')
                if isinstance(college_major_list, list):
                    temp_majors = set()
                    for item in college_major_list:
                        if isinstance(item, dict) and 'name' in item and isinstance(item['name'], str) and item['name'].strip():
                            temp_majors.add(item['name'].strip())
                    standard_majors_list_for_dropdown = sorted(list(temp_majors))
                elif not standard_majors_list_for_dropdown:
                     standard_majors_list_for_dropdown = sorted([m.title() for m in standard_majors_for_mapping_internal if isinstance(m, str)])
        except Exception as e:
            print(f"Error loading original major names for dropdown: {e}")
            standard_majors_list_for_dropdown = sorted([m.title() for m in standard_majors_for_mapping_internal if isinstance(m, str)])
    options['major_required_dropdown'] = ["选择专业..."] + standard_majors_list_for_dropdown if standard_majors_list_for_dropdown else ["选择专业..."]

    # --- MODIFIED: Use get_cleaned_company_tags_from_data ---
    cleaned_tags = get_cleaned_company_tags_from_data(df_jobs_for_options, top_n=70, min_freq=3) # Adjust top_n and min_freq
    if cleaned_tags:
        options['company_tags'] = ["选择福利..."] + sorted(cleaned_tags)
    else:
        # Fallback if no tags are found after cleaning or from data
        options['company_tags'] = ["选择福利...", "五险一金", "年底双薪", "带薪年假", "弹性工作", "定期体检"]
        print("Warning: No company tags derived from data. Using fallback tags.")
    # --- END MODIFICATION ---

    options['skill_keywords_for_predictor'] = DEFAULT_SKILL_KEYWORDS if DEFAULT_SKILL_KEYWORDS else []
    return options, standard_majors_for_mapping_internal

# ... (rest of your 06_Salary_Predictor.py script remains the same from where session state is initialized)
# The UI for company_tags multiselect will automatically use the new options['company_tags']
# Make sure to test the options population and the multiselect behavior.
# Initialize session state, define run_prediction_and_update_state, and the UI layout as before.
# The key change is in load_and_get_options_for_predictor for 'company_tags'.

options_data, standard_majors_for_mapping = load_and_get_options_for_predictor()
if "error" in options_data: 
    st.error(f"无法加载预测器选项: {options_data['error']}")
    st.stop()


# --- Session State 初始化 ---
default_inputs_predict = {
    'rt_skills_input': [],
    'rt_job_catory': options_data.get('job_catory', ["选择或输入..."])[0],
    'rt_province_input': options_data.get('province_options', ["选择省份..."])[0], 
    'rt_degree_name': options_data.get('degree_name', ["选择或输入..."])[0],
    'rt_company_scale': options_data.get('company_scale', ["选择或输入..."])[0],
    'rt_major_multiselect': [],
    'rt_company_tags': [], # Default is empty list for multiselect
    'rt_company_property': options_data.get('company_property', ["选择或输入..."])[0],
}
for key, default_value in default_inputs_predict.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

if 'predicted_salary_display' not in st.session_state:
    st.session_state.predicted_salary_display = "请填写特征并点击“预测薪资”按钮。"
if 'prediction_in_progress' not in st.session_state:
    st.session_state.prediction_in_progress = False


# --- 页面内容 ---
st.title("💸 职位薪资预测器")
st.markdown("选择或输入以下职位特征，模型将尝试预测平均月薪 (K)。")
st.divider()

if not model_ok: st.error(f"薪资预测模型文件未找到或加载失败 ({MODEL_PATH})。")
if not preprocessor_ok: st.error(f"预处理器文件未找到或加载失败 ({PREPROCESSOR_PATH})。")

def run_prediction_and_update_state():
    st.session_state.prediction_in_progress = True
    st.session_state.predicted_salary_display = "正在预测中..."

    if not model or not preprocessor:
        st.session_state.predicted_salary_display = "模型或预处理器未加载成功。"
        st.session_state.prediction_in_progress = False
        return

    selected_majors_text = " ".join(st.session_state.rt_major_multiselect).lower().strip()
    final_processed_major_for_model = utils_map_to_standard_major(selected_majors_text, standard_majors_for_mapping)
    tags_str = ",".join(st.session_state.rt_company_tags) if st.session_state.rt_company_tags else ""
    skills_input_list = st.session_state.rt_skills_input
    skills_input_str = " ".join(skills_input_list).lower().strip()
    
    selected_province = str(st.session_state.rt_province_input if st.session_state.rt_province_input not in ["选择省份..."] else "全国").lower().strip()

    input_data_dict = {
        'job_name': ["综合技能描述"],
        'skills_text_for_model': [skills_input_str],
        'job_catory': [str(st.session_state.rt_job_catory if st.session_state.rt_job_catory not in ["选择或输入..."] else "未知").lower().strip()],
        'job_industry': ['未知'],
        'company_name': ['未知公司'],
        'area_code_name': [selected_province], 
        'company_scale': [str(st.session_state.rt_company_scale if st.session_state.rt_company_scale not in ["选择或输入..."] else "未知").lower().strip()],
        'degree_name': [str(st.session_state.rt_degree_name if st.session_state.rt_degree_name not in ["选择或输入..."] else "不限").lower().strip()],
        'processed_major': [final_processed_major_for_model.lower().strip()],
        'company_property': [str(st.session_state.rt_company_property if st.session_state.rt_company_property not in ["选择或输入..."] else "未知").lower().strip()],
        'company_tags': [tags_str.lower().strip()],
        'head_count': [1],
    }

    combined_text_parts = [
        input_data_dict['skills_text_for_model'][0],
        input_data_dict['job_catory'][0],
        input_data_dict['company_tags'][0]
    ]
    combined_text = " ".join(filter(None, combined_text_parts)).strip()
    input_data_dict['combined_text_features'] = [combined_text]
    input_df = pd.DataFrame(input_data_dict)

    try:
        expected_feature_order = None
        if hasattr(preprocessor, 'feature_names_in_') and preprocessor.feature_names_in_ is not None:
            expected_feature_order = list(preprocessor.feature_names_in_)
        elif feature_names_json:
            expected_feature_order = feature_names_json
        else:
            if hasattr(preprocessor, 'transformers_') and preprocessor.transformers_:
                inferred_features = []
                for name, trans, columns in preprocessor.transformers_:
                    if isinstance(columns, str): inferred_features.append(columns)
                    else: inferred_features.extend(columns)
                if inferred_features: expected_feature_order = inferred_features

        if expected_feature_order:
            input_df_to_transform = pd.DataFrame(columns=expected_feature_order)
            for col in expected_feature_order:
                if col in input_df.columns:
                    input_df_to_transform[col] = input_df[col]
                else:
                    print(f"Critical Warning: Feature '{col}' expected by preprocessor but NOT in current input_df. Using placeholder.")
                    if col == 'head_count': input_df_to_transform[col] = [1]
                    elif col == 'combined_text_features': input_df_to_transform[col] = [""]
                    elif col == 'job_industry': input_df_to_transform[col] = ['未知']
                    elif col == 'job_name': input_df_to_transform[col] = ["综合技能描述"]
                    elif col == 'area_code_name' and 'province_options' in options_data:
                         input_df_to_transform[col] = [selected_province] 
                    else: input_df_to_transform[col] = ['未知']

            if 'skills_text_for_model' in input_df_to_transform.columns and 'skills_text_for_model' not in expected_feature_order:
                input_df_to_transform = input_df_to_transform.drop(columns=['skills_text_for_model'], errors='ignore')
        else:
            st.warning("无法确定预处理器期望的特征顺序。预测可能不准确或失败。")
            input_df_to_transform = input_df.copy()
            if 'skills_text_for_model' in input_df_to_transform.columns and 'skills_text_for_model' not in input_df_to_transform.columns.tolist():
                 pass
        
        # Debugging
        # st.write("Debug: DataFrame being sent to preprocessor.transform():")
        # st.dataframe(input_df_to_transform.head(1).style.set_properties(**{'white-space': 'pre-wrap', 'text-align': 'left'}))
        # st.write("Debug: Expected feature order by preprocessor:", expected_feature_order)
        # st.write("Debug: Columns in input_df_to_transform:", input_df_to_transform.columns.tolist())


        input_processed = preprocessor.transform(input_df_to_transform)
        prediction_val = model.predict(input_processed)
        predicted_salary = prediction_val[0]

        range_delta = predicted_salary * 0.15
        lower_bound = max(0.1, predicted_salary - range_delta)
        upper_bound = predicted_salary + range_delta
        st.session_state.predicted_salary_display = f"{predicted_salary:,.1f} K  (估算范围: {lower_bound:,.1f} K - {upper_bound:,.1f} K)"

    except Exception as e:
        print(f"Detailed Prediction error during run_prediction_and_update_state: {e}")
        traceback.print_exc()
        st.session_state.predicted_salary_display = f"预测出错: {str(e)[:150]}..."
    finally:
        st.session_state.prediction_in_progress = False


if model_ok and preprocessor_ok and "error" not in options_data:
    st.subheader("📝 输入职位特征:")
    form_col1, form_col2 = st.columns(2)
    with form_col1:
        st.multiselect("擅长技能 (可多选):",
                       options=options_data.get('skill_keywords_for_predictor', []),
                       key="rt_skills_input",
                       help="选择你擅长的主要技能")

        st.selectbox("职位类别:", options_data.get('job_catory', ["选择或输入..."]), key="rt_job_catory",
                        index=options_data.get('job_catory', ["选择或输入..."]).index(st.session_state.rt_job_catory) if st.session_state.rt_job_catory in options_data.get('job_catory', ["选择或输入..."]) else 0)
        
        st.selectbox("工作地区 (省份):", options_data.get('province_options', ["选择省份..."]), key="rt_province_input",
                        index=options_data.get('province_options', ["选择省份..."]).index(st.session_state.rt_province_input) if st.session_state.rt_province_input in options_data.get('province_options', ["选择省份..."]) else 0)

        st.selectbox("学历要求:", options_data.get('degree_name', ["选择或输入..."]), key="rt_degree_name",
                        index=options_data.get('degree_name', ["选择或输入..."]).index(st.session_state.rt_degree_name) if st.session_state.rt_degree_name in options_data.get('degree_name', ["选择或输入..."]) else 0)

    with form_col2:
        st.selectbox("公司规模:", options_data.get('company_scale', ["选择或输入..."]), key="rt_company_scale",
                        index=options_data.get('company_scale', ["选择或输入..."]).index(st.session_state.rt_company_scale) if st.session_state.rt_company_scale in options_data.get('company_scale', ["选择或输入..."]) else 0)
        st.multiselect("专业要求 (可多选):", options_data.get('major_required_dropdown', ["选择专业..."]),
                        key="rt_major_multiselect")
        
        st.multiselect("公司福利标签 (可多选):", options_data.get('company_tags', ["选择福利..."]),
                        key="rt_company_tags")
                        
        st.selectbox("公司性质:", options_data.get('company_property', ["选择或输入..."]),
                        key="rt_company_property",
                        index=options_data.get('company_property', ["选择或输入..."]).index(st.session_state.rt_company_property) if st.session_state.rt_company_property in options_data.get('company_property', ["选择或输入..."]) else 0)

    st.divider()

    col_btn_pred, col_result_pred = st.columns([1,3])

    with col_btn_pred:
        st.button("预测薪资", key="predict_button_manual_only_v4", help="点击根据当前输入进行预测", type="primary", on_click=run_prediction_and_update_state)

    with col_result_pred:
        st.subheader("🔮 预测薪资结果:")
        current_display_text = st.session_state.predicted_salary_display

        if st.session_state.prediction_in_progress:
             st.info(current_display_text)
        elif not current_display_text or current_display_text == "请填写特征并点击“预测薪资”按钮。":
            st.info("请调整特征或点击“预测薪资”按钮。")
        elif "预测出错" in current_display_text or "模型或预处理器未加载成功" in current_display_text:
            st.error(current_display_text)
        else:
            st.success(f"**{current_display_text}**")
            try:
                salary_val_str = current_display_text.split("K")[0].strip()
                salary_val = float(salary_val_str.replace(',',''))
                max_salary_for_gauge = 60.0
                if salary_val > 0:
                    import plotly.graph_objects as go
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number", value = salary_val,
                        title = {'text': "预测月薪 (K)"},
                        gauge = {'axis': {'range': [0, max_salary_for_gauge]},
                                    'bar': {'color': "#1f77b4"},
                                    'steps' : [
                                        {'range': [0, max_salary_for_gauge * 0.4], 'color': "lightgray"},
                                        {'range': [max_salary_for_gauge * 0.4, max_salary_for_gauge * 0.7], 'color': "silver"}],
                                    'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': salary_val}}))
                    fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=60, b=20))
                    st.plotly_chart(fig_gauge, use_container_width=True)
            except Exception as e_gauge:
                print(f"Could not create gauge: {e_gauge}")
                pass
elif not model_ok or not preprocessor_ok :
    st.error("核心预测组件加载失败，薪资预测功能不可用。")

st.caption("免责声明：此薪资预测仅为演示目的，实际薪资受多种复杂因素影响。")