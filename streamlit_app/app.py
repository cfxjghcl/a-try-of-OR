import sys
import os
import threading # 用于异步爬取
import subprocess
import json
import time
import pandas as pd
from datetime import datetime

# --- sys.path 和路径定义 (保持不变) ---
# streamlit_app_dir: E:\MyProjects\pythonfinishwork\streamlit_app
streamlit_app_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(streamlit_app_dir)
SCRAPY_PROJECT_ROOT = os.path.join(PROJECT_ROOT, 'crawler')
SCRAPY_MODULE_DIR = os.path.join(SCRAPY_PROJECT_ROOT, 'crawler')
DATA_DIR = os.path.join(SCRAPY_MODULE_DIR, 'data') # 这个DATA_DIR是Scrapy项目内部的
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from streamlit_app.utils import (
    JOBS_FILE, DATA_DIR_INSIDE_CRAWLER, # DATA_DIR_INSIDE_CRAWLER 应该是 utils.py 中定义的指向 Scrapy 项目数据目录的路径
    load_json_data, preprocess_jobs_data,
    get_top_n_counts, get_average_salary,
    get_time_series_data, plot_line_chart,
    plot_bar_chart, plot_pie_chart,
    load_scrapy_default_targets,
    extract_skills_from_job_names # 确认这个函数是否仍然需要，或者使用在preprocess_jobs_data中生成的extracted_skills_list
)
import plotly.express as px

# --- 页面配置 ---
st.set_page_config(
    page_title="招聘市场洞察与实时爬取",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "# 招聘市场分析与实时爬取仪表盘"}
)

# --- 加载主数据和默认爬取选项 (缓存) ---
@st.cache_data(ttl=3600)
def load_main_app_data():
    df_jobs_raw = load_json_data(JOBS_FILE)
    df_jobs = preprocess_jobs_data(df_jobs_raw) if not df_jobs_raw.empty else pd.DataFrame()
    
    try:
        default_targets = load_scrapy_default_targets()
    except Exception as e:
        print(f"CRITICAL WARNING in app.py: Failed to load Scrapy default targets from utils: {e}")
        # 提供一个绝对最小的 fallback，确保字典结构存在
        default_targets = {
            "cities": [{"name": "🌍 不限省份/地区", "code": ""}],
            "categories": [{"name": "📚 不限类别", "code": ""}],
            "industries": [{"name": "🏭 不限行业", "code": ""}],
            "workExperiences": [{"name": "⏳ 不限工作经验", "code": ""}],
            "degrees": [{"name": "🎓 不限学历", "code": ""}],
            "scales": [{"name": "⚖️ 不限公司规模", "code": ""}],
            "corpProps": [{"name": "🏛️ 不限公司性质", "code": ""}]
        }
        # 可以考虑在这里添加一些具体的选项作为后备，如果上面的 utils 加载完全失败
        default_targets['cities'].extend([{"name": "北京市", "code": "11"}, {"name": "上海市", "code": "31"}])
        default_targets['categories'].extend([{"name": "计算机软件", "code": "010000"}, {"name": "互联网/电子商务", "code": "000104"}])

    return df_jobs, default_targets

df_jobs_main, default_crawl_targets = load_main_app_data()

# --- Session State 初始化 (保持不变) ---
if 'realtime_crawl_results_df' not in st.session_state:
    st.session_state.realtime_crawl_results_df = pd.DataFrame()
if 'realtime_crawl_message' not in st.session_state:
    st.session_state.realtime_crawl_message = ""
if 'is_crawling' not in st.session_state:
    st.session_state.is_crawling = False
if 'crawl_process_info' not in st.session_state:
    st.session_state.crawl_process_info = None
if 'crawl_output_file_path_session' not in st.session_state:
    st.session_state.crawl_output_file_path_session = None

# --- 侧边栏 (保持不变) ---
st.sidebar.title("🧭 导航与状态") # Added Emoji
st.sidebar.info("在此页面进行实时岗位爬取，或通过其他页面探索历史数据洞察。") # Adjusted text
st.sidebar.markdown("---")
if os.path.exists(JOBS_FILE):
    try:
        last_updated_time = datetime.fromtimestamp(os.path.getmtime(JOBS_FILE)).strftime('%Y-%m-%d %H:%M:%S')
        st.sidebar.caption(f"主要数据文件最后更新于:\n🗓️ {last_updated_time}") # Added Emoji
    except Exception: pass
else:
    st.sidebar.warning(f"⚠️ 核心数据文件 ({os.path.basename(JOBS_FILE)}) 未找到。") # Added Emoji

# --- 主页面内容 ---
st.title("📊 招聘市场洞察仪表盘") # Simplified title
st.markdown("""
欢迎使用本仪表盘！您可以在此：
- **🚀 实时爬取**最新的岗位数据并进行即时分析。
- **📈 探索历史数据**，通过多个维度洞察招聘市场趋势。
""")
st.divider()

# --- 异步爬取函数 (保持不变) ---
def run_scrapy_in_thread(scrapy_cmd_args_list, crawler_root_path, output_file_abs_path_for_thread):
    st.session_state.is_crawling = True
    st.session_state.crawl_process_info = None
    st.session_state.crawl_output_file_path_session = output_file_abs_path_for_thread
    print(f"\n[{datetime.now()}] THREAD: Launching Scrapy command:")
    print(f"Executing: {' '.join(scrapy_cmd_args_list)}")
    print(f"In CWD: {crawler_root_path}")
    print(f"Outputting Scrapy items to: {output_file_abs_path_for_thread}\n")
    process = None
    try:
        process = subprocess.Popen(
            scrapy_cmd_args_list, cwd=crawler_root_path,
            stdout=None, stderr=subprocess.PIPE, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0 # Hides console window on Windows
        )
        try:
            _, stderr_output = process.communicate(timeout=180) # 3 minutes timeout
            returncode = process.returncode
        except subprocess.TimeoutExpired:
            print(f"[{datetime.now()}] THREAD: Scrapy process timed out. Terminating...")
            process.terminate()
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: process.kill()
            returncode = -99 # Custom code for timeout
            stderr_output = "爬取操作超时 (超过3分钟)。"
        st.session_state.crawl_process_info = {'stderr': stderr_output, 'returncode': returncode}
    except FileNotFoundError:
        print(f"[{datetime.now()}] THREAD: Scrapy command not found.")
        st.session_state.crawl_process_info = {'error_type': 'filenotfound', 'stderr': 'Scrapy 命令未找到。请确保 Scrapy 已安装并配置在系统路径中。'}
    except Exception as e:
        print(f"[{datetime.now()}] THREAD: Exception during Scrapy Popen/communicate: {e}")
        st.session_state.crawl_process_info = {'error_type': 'exception', 'stderr': f'执行实时爬取时发生意外错误: {e}'}
    finally:
        st.session_state.is_crawling = False
        st.rerun() # Trigger a rerun to update the UI


# --- 实时爬取模块 ---
st.header("🚀 实时岗位数据爬取与分析")
with st.expander("展开进行实时爬取", expanded=True):
    with st.form(key="realtime_crawl_form_main_v6"): # Incremented key
        st.markdown("**🎯 根据您的需求定制爬取目标:**")
        
        # 第一行筛选：关键词，省份，类别 (保持不变或微调)
        form_row1_col1, form_row1_col2, form_row1_col3 = st.columns([2,2,2])
        with form_row1_col1:
            rt_keyword_input = st.text_input("📝 输入职位关键词 (可选)", placeholder="例如: python, 数据分析", key="rt_keyword_input_v6")
        with form_row1_col2:
            city_options_list_rt = default_crawl_targets.get('cities', [])
            city_display_names_rt = ["🌍 不限省份/地区"] + sorted(list(set(c['name'] for c in city_options_list_rt if c.get('name'))))
            default_city_index_rt = 0
            rt_selected_city_name_form = st.selectbox("📍 选择目标省份/地区:", city_display_names_rt, index=default_city_index_rt, key="rt_city_select_v6")
        with form_row1_col3:
            category_options_list_rt = default_crawl_targets.get('categories', [])
            category_display_names_rt = ["📚 不限类别"] + sorted(list(set(c['name'] for c in category_options_list_rt if c.get('name'))))
            default_cat_index_rt = 0
            rt_selected_category_name_form = st.selectbox("🏷️ 选择目标职位类别:", category_display_names_rt, index=default_cat_index_rt, key="rt_category_select_v6")

        st.markdown("---") # 分隔符，更清晰
        st.markdown("**更多筛选条件 (可选):**")
        
        # 第二行筛选：行业，工作经验
        form_row2_col1, form_row2_col2 = st.columns(2)
        with form_row2_col1:
            industry_options_list_rt = default_crawl_targets.get('industries', []) # 假设 utils 已更新
            industry_display_names_rt = ["🏭 不限行业"] + sorted(list(set(i['name'] for i in industry_options_list_rt if i.get('name'))))
            default_industry_index_rt = 0
            rt_selected_industry_name_form = st.selectbox(
                "🏢 选择目标行业:", 
                industry_display_names_rt, 
                index=default_industry_index_rt, 
                key="rt_industry_select_v6"
            )
        with form_row2_col2:
            work_exp_options_list_rt = default_crawl_targets.get('workExperiences', [])
            work_exp_display_names_rt = [item['name'] for item in work_exp_options_list_rt if item.get('name')]
            rt_selected_work_exp_name_form = st.selectbox(
                "🛠️ 选择工作经验要求:", 
                options=work_exp_display_names_rt,
                index=0,
                key="rt_work_exp_select_v6_new"
            )
            
        # 第三行筛选：学历，公司规模，公司性质
        form_row3_col1, form_row3_col2, form_row3_col3 = st.columns(3)
        with form_row3_col1:
            # 学历
            degree_options_list_rt = default_crawl_targets.get('degrees', []) 
            degree_display_names_rt = [item['name'] for item in degree_options_list_rt if item.get('name')]
            # default_degree_index_rt 应该总是 0，因为 "不限学历" 保证是第一个
            rt_selected_degree_name_form = st.selectbox(
                "📜 选择学历要求:", 
                options=degree_display_names_rt, 
                index=0, 
                key="rt_degree_select_v6_new" # 建议更新key以便刷新
            )
        with form_row3_col2:
            # 公司规模
            scale_options_list_rt = default_crawl_targets.get('scales', [])
            scale_display_names_rt = [item['name'] for item in scale_options_list_rt if item.get('name')]
            rt_selected_scale_name_form = st.selectbox(
                "📈 选择公司规模:", 
                options=scale_display_names_rt,
                index=0,
                key="rt_scale_select_v6_new"
            )
        with form_row3_col3:
            property_options_list_rt = default_crawl_targets.get('corpProps', []) # 假设 utils 已更新 (corpProps 是常用键名)
            property_display_names_rt = ["🏛️ 不限公司性质"] + sorted(list(set(p['name'] for p in property_options_list_rt if p.get('name'))))
            default_property_index_rt = 0
            rt_selected_property_name_form = st.selectbox(
                "⚖️ 选择公司性质:", # Emoji may need adjustment
                property_display_names_rt, 
                index=default_property_index_rt, 
                key="rt_property_select_v6"
            )

        rt_submit_button = st.form_submit_button(label="⚡ 开始实时爬取分析", type="primary", use_container_width=True, disabled=st.session_state.is_crawling)

    if rt_submit_button:
        if not st.session_state.is_crawling:
            st.session_state.is_crawling = True
            st.session_state.realtime_crawl_message = "⏳ 正在启动实时爬取，请稍候... (详细日志请查看终端)"
            st.session_state.realtime_crawl_results_df = pd.DataFrame()
            st.session_state.crawl_process_info = None

            # --- 构造 Scrapy 命令参数 ---
            scrapy_cmd_args = ['scrapy', 'crawl', 'jobs', '-a', f'run_type=realtime_app_home_v5'] # 更新 run_type 版本

            # 关键词
            if rt_keyword_input.strip(): 
                scrapy_cmd_args.extend(['-a', f'target_keywords_str={rt_keyword_input.strip()}'])

            # 省份/地区 (target_cities_json)
            target_cities_param_list = []
            if rt_selected_city_name_form != "🌍 不限省份/地区":
                city_code = next((c['code'] for c in default_crawl_targets.get('cities', []) if c['name'] == rt_selected_city_name_form), None)
                if city_code is not None: 
                    target_cities_param_list = [{"code": city_code, "name": rt_selected_city_name_form}]
                    scrapy_cmd_args.extend(['-a', f'target_cities_json={json.dumps(target_cities_param_list)}'])
            
            # 职位类别 (target_categories_json)
            target_categories_param_list = []
            if rt_selected_category_name_form != "📚 不限类别":
                cat_code = next((c['code'] for c in default_crawl_targets.get('categories', []) if c['name'] == rt_selected_category_name_form), None)
                if cat_code is not None: 
                    target_categories_param_list = [{"code": cat_code, "name": rt_selected_category_name_form}]
                    scrapy_cmd_args.extend(['-a', f'target_categories_json={json.dumps(target_categories_param_list)}'])

            # 行业 (target_industries_json)
            if rt_selected_industry_name_form != "🏭 不限行业":
                industry_code = next((i['code'] for i in default_crawl_targets.get('industries', []) if i['name'] == rt_selected_industry_name_form), None)
                if industry_code is not None:
                    # 假设爬虫期望的参数名是 target_industries_json 或类似
                    scrapy_cmd_args.extend(['-a', f'target_industries_json={json.dumps([{"code": industry_code, "name": rt_selected_industry_name_form}])}'])
            
            # 工作经验 (target_workexp_json or target_workexp_code)
            if rt_selected_work_exp_name_form != "⏳ 不限工作经验":
                work_exp_code = next((w['code'] for w in default_crawl_targets.get('workExperiences', []) if w['name'] == rt_selected_work_exp_name_form), None)
                if work_exp_code is not None:
                    # 假设爬虫期望的参数名是 target_workexp_code 或 target_workexp_json
                    scrapy_cmd_args.extend(['-a', f'target_workexp_code={work_exp_code}']) 
                    # 或者 scrapy_cmd_args.extend(['-a', f'target_workexp_json={json.dumps([{"code": work_exp_code, "name": rt_selected_work_exp_name_form}])}'])

            # 学历 (target_degree_json or target_degree_code)
            if rt_selected_degree_name_form != "🎓 不限学历":
                degree_code = next((d['code'] for d in default_crawl_targets.get('degrees', []) if d['name'] == rt_selected_degree_name_form), None)
                if degree_code is not None:
                    scrapy_cmd_args.extend(['-a', f'target_degree_code={degree_code}'])

            # 公司规模 (target_scale_json or target_scale_code)
            if rt_selected_scale_name_form != "⚖️ 不限公司规模":
                scale_code = next((s['code'] for s in default_crawl_targets.get('scales', []) if s['name'] == rt_selected_scale_name_form), None)
                if scale_code is not None:
                    scrapy_cmd_args.extend(['-a', f'target_scale_code={scale_code}'])

            # 公司性质 (target_property_json or target_property_code)
            if rt_selected_property_name_form != "🏛️ 不限公司性质":
                prop_code = next((p['code'] for p in default_crawl_targets.get('corpProps', []) if p['name'] == rt_selected_property_name_form), None)
                if prop_code is not None:
                    scrapy_cmd_args.extend(['-a', f'target_property_code={prop_code}'])
            
            # --- 输出文件和执行线程 (与之前类似) ---
            timestamp_str = str(int(time.time()))
            REALTIME_OUTPUT_FILENAME = f"jobs_realtime_{timestamp_str}.jsonl"
            REALTIME_OUTPUT_FILE_ABS_PATH = os.path.join(DATA_DIR_INSIDE_CRAWLER, REALTIME_OUTPUT_FILENAME)
            
            relative_output_path_for_scrapy_o = os.path.join('crawler', 'data', REALTIME_OUTPUT_FILENAME)
            scrapy_cmd_args.extend(['-o', relative_output_path_for_scrapy_o, '-L', 'INFO'])
            os.makedirs(os.path.dirname(REALTIME_OUTPUT_FILE_ABS_PATH), exist_ok=True)

            CRAWLER_PROJECT_ROOT_APP = SCRAPY_PROJECT_ROOT

            thread = threading.Thread(target=run_scrapy_in_thread, args=(scrapy_cmd_args, CRAWLER_PROJECT_ROOT_APP, REALTIME_OUTPUT_FILE_ABS_PATH))
            thread.start()
            st.rerun()

# --- 处理和显示实时爬取线程的结果 ---
if st.session_state.is_crawling:
    st.info("⚙️ **实时爬取正在进行中...** 请查看运行 Streamlit 的终端获取详细的 Scrapy 日志。完成后此区域会自动更新。")
elif st.session_state.get('crawl_process_info') is not None:
    process_info = st.session_state.crawl_process_info
    output_file = st.session_state.get('crawl_output_file_path_session')
    
    # 统一处理消息
    current_message = ""
    success_flag = False

    if process_info.get('error_type') == 'timeout': current_message = "❌ 实时爬取超时 (超过3分钟)。"
    elif process_info.get('error_type') == 'filenotfound': current_message = "❌ Scrapy 命令未找到。请检查环境配置。"
    elif process_info.get('error_type'): current_message = f"❌ 执行爬取时发生意外错误: {process_info.get('error_type')}"
    elif process_info.get('returncode') == 0:
        if output_file and os.path.exists(output_file):
            df_rt_raw = load_json_data(output_file) # load_json_data 应该能处理 .jsonl
            if not df_rt_raw.empty:
                st.session_state.realtime_crawl_results_df = preprocess_jobs_data(df_rt_raw)
                current_message = f"✅ 爬取完成！找到 {len(st.session_state.realtime_crawl_results_df)} 条岗位。"
                success_flag = True
            else:
                current_message = f"ℹ️ 爬取执行成功，但未能从临时输出文件 '{os.path.basename(output_file)}' 解析到有效数据。"
            try: 
                if os.path.exists(output_file): os.remove(output_file) # 删除临时文件
            except Exception as e_rm: print(f"Error removing temp file {output_file}: {e_rm}")
        else:
            current_message = f"⚠️ 爬取执行成功，但未找到预期的输出文件 '{os.path.basename(output_file if output_file else 'N/A')}'。"
    else:
        current_message = f"❌ 爬取失败 (错误代码: {process_info.get('returncode')})。详情请查看下方错误输出。"
    
    st.session_state.realtime_crawl_message = current_message

    if process_info.get('stderr') and not success_flag : # 只在有错误且爬取不完全成功时默认展开
        with st.expander("查看爬虫错误输出 (stderr)", expanded=True): # Expanded if error
            st.text_area("Scrapy 标准错误:", value=process_info['stderr'], height=150, key="stderr_display_v3")
            
    st.session_state.crawl_process_info = None # 清理，避免重复处理
    st.session_state.crawl_output_file_path_session = None
    # 不需要 st.rerun() 在这里，因为 run_scrapy_in_thread 的 finally 中已经有了

# --- 显示实时爬取的消息和结果图表 ---
if st.session_state.realtime_crawl_message and not st.session_state.is_crawling:
    st.subheader("📡 实时爬取状态与结果")
    if "✅" in st.session_state.realtime_crawl_message : st.success(st.session_state.realtime_crawl_message)
    elif "❌" in st.session_state.realtime_crawl_message : st.error(st.session_state.realtime_crawl_message)
    else: st.info(st.session_state.realtime_crawl_message)

    if not st.session_state.realtime_crawl_results_df.empty:
        df_rt_display = st.session_state.realtime_crawl_results_df
        rt_metric_col1, rt_metric_col2 = st.columns(2)
        with rt_metric_col1:
            st.metric("📈 找到岗位数", f"{len(df_rt_display):,}")
        with rt_metric_col2:
            rt_avg_salary_df = df_rt_display[df_rt_display['avg_month_pay'] > 0]
            rt_avg_sal = rt_avg_salary_df['avg_month_pay'].mean() if not rt_avg_salary_df.empty else 0
            st.metric("💰 平均月薪 (K)", f"{rt_avg_sal:,.1f}" if rt_avg_sal > 0 else "N/A")

        rt_chart_col1, rt_chart_col2 = st.columns(2)
        with rt_chart_col1:
            st.markdown("###### 🎓 学历要求分布")
            rt_degrees_df = get_top_n_counts(df_rt_display, 'degree_name_cat', 5) # 使用 degree_name_cat
            if not rt_degrees_df.empty:
                plot_pie_chart(rt_degrees_df, 'degree_name_cat', 'count', "实时结果-学历要求", hole=0.4) # Increased hole
            else: st.caption("无学历数据。")
        with rt_chart_col2:
            st.markdown("###### 🏷️ 主要职位类别分布")
            top_cats_rt = get_top_n_counts(df_rt_display, 'job_catory', 5)
            if not top_cats_rt.empty:
                plot_pie_chart(top_cats_rt, 'job_catory', 'count', "实时结果-职位类别", hole=0.4)
            else: st.caption("无职位类别数据。")
        
        # 技能提取，需要确认 df_rt_display 中是否有 'extracted_skills_list'
        if 'extracted_skills_list' in df_rt_display.columns:
            from streamlit_app.utils import get_skill_frequency # 确保导入
            st.markdown("###### 🛠️ 热门技能 (Top 5)")
            # 假设 get_skill_frequency 可以处理 'extracted_skills_list' 列
            rt_skills_df = get_skill_frequency(df_rt_display, 'extracted_skills_list', top_n=5)
            if not rt_skills_df.empty:
                plot_bar_chart(rt_skills_df, 'skill', 'count', "实时结果-主要技能", "技能", "频次", orientation='h')
            else: st.caption("无技能数据或未能提取。")
        else: # Fallback or if 'extract_skills_from_job_names' is preferred for this quick view
            st.markdown("###### 🛠️ 热门技能 (Top 5 - 基于职位名称)")
            rt_skills_df_legacy = extract_skills_from_job_names(df_rt_display, top_n=5) # 确认此函数是否仍然适用
            if not rt_skills_df_legacy.empty:
                 plot_bar_chart(rt_skills_df_legacy, 'skill' if 'skill' in rt_skills_df_legacy.columns else 'term', 'count', "实时结果-主要技能", "技能", "频次", orientation='h')
            else: st.caption("无技能数据。")


        if not rt_avg_salary_df.empty:
            st.subheader("实时结果 - 薪资分布直方图")
            # 增加薪资分箱以获得更细致的视图
            salary_bins_rt = [0, 5, 10, 15, 20, 25, 30, 40, 50, 200] # Max 200k for display
            salary_labels_rt = [f"{salary_bins_rt[i]}-{salary_bins_rt[i+1]}K" for i in range(len(salary_bins_rt)-1)]
            
            # 创建一个副本进行分箱，避免修改原始 session_state DataFrame
            df_rt_display_for_hist = rt_avg_salary_df.copy()
            df_rt_display_for_hist['salary_group_rt'] = pd.cut(df_rt_display_for_hist['avg_month_pay'], bins=salary_bins_rt, labels=salary_labels_rt, right=False)
            
            # 统计每个薪资组的数量
            salary_group_counts_rt = df_rt_display_for_hist['salary_group_rt'].value_counts().reset_index()
            salary_group_counts_rt.columns = ['salary_group_rt', 'count']
            # 确保薪资组是Categorical并按定义的顺序排序
            salary_group_counts_rt['salary_group_rt'] = pd.Categorical(salary_group_counts_rt['salary_group_rt'], categories=salary_labels_rt, ordered=True)
            salary_group_counts_rt.sort_values('salary_group_rt', inplace=True)


            fig_hist_rt = px.bar(salary_group_counts_rt, x="salary_group_rt", y="count", 
                                 title="实时结果 - 平均月薪分布 (K/月)", 
                                 labels={'salary_group_rt': '平均月薪范围 (K)', 'count': '岗位数量'},
                                 text_auto=True)
            fig_hist_rt.update_layout(bargap=0.2)
            st.plotly_chart(fig_hist_rt, use_container_width=True)

        with st.expander("📋 查看实时爬取数据样本 (最多100条)", expanded=False):
            display_cols_rt = ['job_name', 'company_name', 'province_clean', 'city_clean', 'avg_month_pay', 'degree_name_cat', 'work_year_cat']
            # 确保这些列都存在于 df_rt_display
            valid_display_cols_rt = [col for col in display_cols_rt if col in df_rt_display.columns]
            st.dataframe(df_rt_display[valid_display_cols_rt].head(100), use_container_width=True) # Added use_container_width
    st.divider()


# --- 主数据概览部分 ---
st.header("📜 主数据库历史数据概览") # Added Emoji
if not df_jobs_main.empty:
    st.markdown("#### 关键指标")
    main_col1_metrics, main_col2_metrics, main_col3_metrics, main_col4_metrics = st.columns(4)
    main_col1_metrics.metric("🕒 历史总岗位数", f"{len(df_jobs_main):,}")
    # 使用 province_clean 统计省份数
    main_col2_metrics.metric("🗺️ 涉及省份数", df_jobs_main['province_clean'].nunique())
    main_col3_metrics.metric("🏷️ 职位类别数", df_jobs_main['job_catory'].nunique())
    
    avg_salary_overall_df_main = df_jobs_main[df_jobs_main['avg_month_pay'] > 0]
    avg_salary_overall_main = avg_salary_overall_df_main['avg_month_pay'].mean() if not avg_salary_overall_df_main.empty else 0
    main_col4_metrics.metric("💰 历史平均月薪 (K)", f"{avg_salary_overall_main:,.1f}" if avg_salary_overall_main > 0 else "N/A")
    st.markdown("---")

    st.subheader("📅 历史数据 - 趋势与分布") # Changed subheader
    
    # 热门趋势可视化优化
    trend_col1, trend_col2 = st.columns(2)
    with trend_col1:
        st.markdown("###### 📈 每日岗位发布数量趋势")
        if 'publish_date_dt' in df_jobs_main.columns:
            # 使用 'D' 表示每日频率
            daily_jobs_series_main = get_time_series_data(df_jobs_main, time_col='publish_date_dt', freq='D')
            if not daily_jobs_series_main.empty:
                # 动态决定回溯期，比如最多显示最近180天的数据，如果数据少于此则全部显示
                lookback_days_main = 180 if len(daily_jobs_series_main) > 180 else None 
                plot_line_chart(daily_jobs_series_main, "历史数据 - 每日岗位发布数量", y_label="岗位数量", default_lookback_days=lookback_days_main)
            else: st.caption("日岗位发布趋势数据不足。")
        else: st.caption("缺少发布日期信息，无法展示趋势。")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("###### 💼 热门招聘省份 (Top 10)")
        # 正确统计省份的岗位数
        top_provinces_main = get_top_n_counts(df_jobs_main, 'province_clean', top_n=10)
        if not top_provinces_main.empty:
            plot_bar_chart(top_provinces_main, 'province_clean', 'count', "历史数据 - 热门招聘省份", "省份", "岗位数量", orientation='h') # Horizontal for better readability
        else: st.caption("省份数据不足。")

    with trend_col2:
        st.markdown("###### 📊 整体平均月薪分布 (K/月)")
        if not avg_salary_overall_df_main.empty:
            # 为薪资分布创建更细致的分箱
            salary_bins = [0, 5, 8, 10, 12, 15, 18, 20, 25, 30, 40, 50, 70, 100, 500] # Max 500k for very high salaries
            salary_labels = [f"{salary_bins[i]}-{salary_bins[i+1]}K" for i in range(len(salary_bins)-1)]
            
            df_jobs_main_for_hist = avg_salary_overall_df_main.copy()
            df_jobs_main_for_hist['salary_group_main'] = pd.cut(df_jobs_main_for_hist['avg_month_pay'], bins=salary_bins, labels=salary_labels, right=False)
            
            salary_group_counts_main = df_jobs_main_for_hist['salary_group_main'].value_counts().reset_index()
            salary_group_counts_main.columns = ['salary_group_main', 'count']
            salary_group_counts_main['salary_group_main'] = pd.Categorical(salary_group_counts_main['salary_group_main'], categories=salary_labels, ordered=True)
            salary_group_counts_main.sort_values('salary_group_main', inplace=True)

            fig_hist_main = px.bar(salary_group_counts_main, x="salary_group_main", y="count", 
                                   title="历史数据 - 整体平均月薪分布", 
                                   labels={'salary_group_main': '平均月薪范围 (K)', 'count': '岗位数量'},
                                   text_auto=True) # Show counts on bars
            fig_hist_main.update_layout(bargap=0.2, xaxis_tickangle=-45)
            st.plotly_chart(fig_hist_main, use_container_width=True)
        else: st.caption("薪资数据不足以生成分布图。")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("###### 📚 热门职位类别 (Top 7)")
        top_categories_main = get_top_n_counts(df_jobs_main, 'job_catory', top_n=7)
        if not top_categories_main.empty:
            plot_pie_chart(top_categories_main, 'job_catory', 'count', "历史数据 - 热门职位类别", hole=0.4) # Increased hole
        else: st.caption("职位类别数据不足。")
        
    st.caption("更详细的历史数据分析请查看应用内的其他分析页面。")
else:
    st.info("ℹ️ 主数据库中暂无历史数据可供概览。")

st.divider()

# --- 近期热门/高薪岗位一览 ---
st.header("✨ 近期与高薪岗位聚焦 (基于历史数据)") # Adjusted header

if not df_jobs_main.empty and 'publish_date_dt' in df_jobs_main.columns:
    col_latest, col_high_salary = st.columns(2)

    with col_latest:
        st.subheader("🆕 最新发布的岗位 (Top 5)")
        latest_jobs_sample = df_jobs_main.sort_values(by='publish_date_dt', ascending=False).head(5)
        if not latest_jobs_sample.empty:
            for idx, row in latest_jobs_sample.iterrows():
                job_title = row.get('job_name', 'N/A')
                company = row.get('company_name', 'N/A')
                # 使用 province_clean 和 city_clean
                province = row.get('province_clean', '')
                city = row.get('city_clean', 'N/A')
                location_str = f"{province} - {city}" if province and province != city else city

                salary_avg = row.get('avg_month_pay', 0)
                salary_str = f"{salary_avg:.1f}K" if salary_avg > 0 else "面议"
                
                publish_dt = row.get('publish_date_dt')
                date_str = publish_dt.strftime('%Y-%m-%d') if pd.notna(publish_dt) else "未知日期"
                
                st.markdown(f"""
                <div style="border-left: 5px solid #007bff; padding: 10px; margin-bottom: 10px; background-color: #f8f9fa; border-radius: 3px;">
                    <strong>{job_title}</strong> @ <span style="color: #17a2b8;">{company}</span><br>
                    <small>📍 {location_str} | 💰 {salary_str} | 🗓️ {date_str}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("暂无最新岗位信息。")

    with col_high_salary:
        st.subheader("🏆 近期高薪岗位 (Top 5)")
        # 定义“近期”：比如最近30天内发布的
        from pandas.tseries.offsets import MonthEnd # For date calculations
        if 'publish_date_dt' in df_jobs_main.columns:
            # 确保 'publish_date_dt' 是 datetime 类型并且有时区信息（或统一处理）
            # preprocess_jobs_data 应该已经处理了时区为 UTC
            thirty_days_ago = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=30) # Use UTC now
            
            recent_high_salary_jobs = df_jobs_main[
                (df_jobs_main['publish_date_dt'] >= thirty_days_ago) & 
                (df_jobs_main['avg_month_pay'] > 0) # 确保有薪资数据
            ].sort_values(by='avg_month_pay', ascending=False).head(5)

            if not recent_high_salary_jobs.empty:
                for idx, row in recent_high_salary_jobs.iterrows():
                    job_title = row.get('job_name', 'N/A')
                    company = row.get('company_name', 'N/A')
                    province = row.get('province_clean', '')
                    city = row.get('city_clean', 'N/A')
                    location_str = f"{province} - {city}" if province and province != city else city

                    salary_avg = row.get('avg_month_pay', 0)
                    salary_str = f"{salary_avg:.1f}K" # 高薪岗位必然>0
                    
                    publish_dt = row.get('publish_date_dt')
                    date_str = publish_dt.strftime('%Y-%m-%d') if pd.notna(publish_dt) else "未知日期"

                    st.markdown(f"""
                    <div style="border-left: 5px solid #28a745; padding: 10px; margin-bottom: 10px; background-color: #f8f9fa; border-radius: 3px;">
                        <strong>{job_title}</strong> @ <span style="color: #17a2b8;">{company}</span><br>
                        <small>📍 {location_str} | 💰 <strong style="color: #dc3545;">{salary_str}</strong> | 🗓️ {date_str}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("近30天内暂无符合条件的高薪岗位。")
        else:
            st.caption("缺少发布日期，无法筛选近期高薪岗位。")
elif not df_jobs_main.empty:
    st.info("历史数据中缺少发布日期 (`publish_date_dt`)，无法展示近期岗位。")
else: # df_jobs_main is empty
    pass # 错误已在主数据概览部分处理

st.markdown("---")
st.info("💡 小提示: 本页的实时爬取功能会根据您的输入即时获取最新数据进行展示。")