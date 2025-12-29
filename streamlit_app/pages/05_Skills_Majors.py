import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os, sys
import matplotlib.font_manager as fm
import plotly.express as px

# --- sys.path modification (if you still need it here, though utils import should handle it) ---
# current_page_script_dir = os.path.dirname(os.path.abspath(__file__))
# streamlit_app_dir = os.path.dirname(current_page_script_dir)
# project_root = os.path.dirname(streamlit_app_dir)
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)
# --- end sys.path modification ---


# --- PAGE CONFIGURATION (MOVED TO THE TOP) ---
# Ensure this is called only once per app run for this page
if 'page_config_called_skills_majors' not in st.session_state:
    st.set_page_config(page_title="技能与专业洞察", layout="wide", page_icon="🛠️")
    st.session_state.page_config_called_skills_majors = True
# --- END PAGE CONFIGURATION ---


try:
    # Assuming your project structure is correct, direct import from utils should work
    # if the streamlit_app directory is the root for streamlit run, or project_root is in sys.path
    from streamlit_app.utils import (  # Changed to be more explicit if utils is in streamlit_app
        load_json_data,
        preprocess_jobs_data,
        extract_skills_from_text_series,
        get_skill_frequency,
        get_word_counts_from_list_column,
        get_top_n_counts,
        get_skill_cooccurrence_optimized,
        SKILL_REGEX_PATTERNS,
        plot_bar_chart,
        JOBS_FILE,
        ASSETS_DIR,
        get_average_salary,
    )
except ImportError as e:
    # Fallback if the above doesn't work (e.g. running script directly from pages folder)
    # This assumes utils.py is in a directory named 'utils' at the same level as 'pages'
    # or that the sys.path modification at the top of this script is active and correct.
    # For a multi-page app, it's better to structure imports from the app's root.
    try:
        from utils import ( # Try direct import if sys.path is already set up
            load_json_data,
            preprocess_jobs_data,
            extract_skills_from_text_series,
            get_skill_frequency,
            get_word_counts_from_list_column,
            get_top_n_counts,
            get_skill_cooccurrence_optimized,
            SKILL_REGEX_PATTERNS,
            plot_bar_chart,
            JOBS_FILE,
            ASSETS_DIR,
            get_average_salary,
        )
    except ImportError:
        st.error(f"Failed to import from utils.py: {e}. Ensure it's in the correct path relative to your Streamlit app's root and all names are defined.")
        st.error(f"Current sys.path: {sys.path}")
        st.error(f"Current working directory: {os.getcwd()}")
        st.stop()


@st.cache_data
def get_chinese_font_path_dynamically():
    # ... (rest of your function)
    if 'ASSETS_DIR' in globals() and os.path.exists(ASSETS_DIR):
        preferred_fonts_in_assets = ['simhei.ttf', 'msyh.ttf', 'SimHei.ttf', 'Microsoft YaHei.ttf']
        for font_name in preferred_fonts_in_assets:
            asset_font_path = os.path.join(ASSETS_DIR, font_name)
            if os.path.exists(asset_font_path): return asset_font_path
    font_family_preferences = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'Source Han Sans SC', 'STHeiti', 'Arial Unicode MS', 'Droid Sans Fallback', 'sans-serif']
    for font_family in font_family_preferences:
        try:
            font_path = fm.findfont(fm.FontProperties(family=font_family))
            if font_path: return font_path
        except Exception: continue
    return None

FONT_PATH_FOR_WORDCLOUD = get_chinese_font_path_dynamically()

@st.cache_data
def generate_wordcloud_from_freq_dict(freq_dict, title="词云图", max_words=100):
    # ... (rest of your function)
    if not freq_dict:
        return None
    if FONT_PATH_FOR_WORDCLOUD is None and 'font_missing_warning_shown' not in st.session_state:
        st.warning("未能自动找到合适的中文字体。词云图中的中文可能无法正确显示。建议：将中文字体文件（如 simhei.ttf）放置在项目的 `streamlit_app/assets/` 目录下。")
        st.session_state.font_missing_warning_shown = True # Set flag after showing once
    try:
        wordcloud = WordCloud(font_path=FONT_PATH_FOR_WORDCLOUD, width=800, height=400, background_color='white', max_words=max_words, collocations=False).generate_from_frequencies(freq_dict)
        return wordcloud
    except Exception as e:
        st.error(f"生成词云图 '{title}' 失败: {e}")
        if "ValueError: We need at least 1 word to plot a word cloud, got 0." in str(e): st.info(f"词云图 '{title}': 过滤后没有足够的词来生成词云。")
        return None


def display_wordcloud(wc, title):
    # ... (rest of your function)
    if wc:
        fig, ax = plt.subplots(figsize=(10, 5)); ax.imshow(wc, interpolation='bilinear'); ax.axis('off'); st.pyplot(fig)
    else: st.info(f"无法为 '{title}' 生成词云图（可能无数据或生成错误）。")


def show_skills_majors_page():
    st.title("🛠️ 职业技能与专业需求洞察")

    df_jobs_raw = load_json_data(JOBS_FILE)
    if df_jobs_raw.empty: st.warning("未能加载职位数据，请检查 `jobs.json` 文件。"); st.stop()

    df_jobs = preprocess_jobs_data(df_jobs_raw)

    if df_jobs.empty: st.warning("数据预处理后为空，无法进行分析。"); st.stop()

    # Critical check for 'job_name_and_major_text'
    if 'job_name_and_major_text' not in df_jobs.columns: # Removed 'and not df_jobs.empty' as df_jobs emptiness is checked above
        st.error("Critical Error: 'job_name_and_major_text' is MISSING from df_jobs before skill extraction!")
        st.info("This likely means `preprocess_jobs_data` from utils.py is not creating this column, or an old cached version is being used.")
        st.stop()


    @st.cache_data
    def add_extracted_skills_column(df, text_col, skill_patterns):
        # ... (rest of your function)
        df_copy = df.copy()
        if text_col not in df_copy.columns:
             st.error(f"FATAL in add_extracted_skills_column: Column '{text_col}' not found!")
             st.write("Columns available in df_copy:", list(df_copy.columns))
             st.stop()
        df_copy['extracted_skills_list'] = extract_skills_from_text_series(
            df_copy[text_col],
            skill_regex_patterns=skill_patterns # Ensure this variable is correctly passed
        )
        return df_copy


    if 'SKILL_REGEX_PATTERNS' not in globals() or SKILL_REGEX_PATTERNS is None: # Check SKILL_REGEX_PATTERNS itself
        st.error("SKILL_REGEX_PATTERNS 未从 utils.py 中正确导入或初始化！")
        st.stop()

    # Call the function to add the skills column
    df_jobs_with_skills = add_extracted_skills_column(df_jobs, 'job_name_and_major_text', SKILL_REGEX_PATTERNS)


    st.sidebar.header("全局筛选器")
    job_catory_col = 'job_catory' if 'job_catory' in df_jobs_with_skills.columns else None
    degree_name_cat_col = 'degree_name_cat' if 'degree_name_cat' in df_jobs_with_skills.columns else None
    company_property_col = 'company_property' if 'company_property' in df_jobs_with_skills.columns else None

    # Sidebar selectbox for job_catory
    if job_catory_col:
        unique_categories_sidebar_raw = df_jobs_with_skills[job_catory_col].astype(str).dropna().unique() # dropna here
        unique_categories_sidebar_cleaned = sorted([val for val in unique_categories_sidebar_raw if val.lower() != 'nan' and val.strip() != '']) # Ensure stripping
        unique_categories_sidebar = ["所有类别"] + unique_categories_sidebar_cleaned
        selected_category_filter = st.sidebar.selectbox("职位类别", unique_categories_sidebar, index=0, key="skills_cat_filter")
    else:
        selected_category_filter = "所有类别"
        st.sidebar.warning("列 'job_catory' 不存在，无法按职位类别筛选。")

    # Sidebar selectbox for degree_name_cat
    if degree_name_cat_col:
        unique_degrees_sidebar_raw = df_jobs_with_skills[degree_name_cat_col].astype(str).dropna().unique() # dropna here
        unique_degrees_sidebar_cleaned = sorted([val for val in unique_degrees_sidebar_raw if val.lower() != 'nan' and val.strip() != ''])
        unique_degrees_sidebar = ["所有学历"] + unique_degrees_sidebar_cleaned
        selected_degree_filter = st.sidebar.selectbox("学历要求", unique_degrees_sidebar, index=0, key="skills_deg_filter")
    else:
        selected_degree_filter = "所有学历"
        st.sidebar.warning("列 'degree_name_cat' 不存在，无法按学历筛选。")

    # Sidebar selectbox for company_property
    if company_property_col:
        unique_properties_sidebar_raw = df_jobs_with_skills[company_property_col].astype(str).dropna().unique() # dropna here
        unique_properties_sidebar_cleaned = sorted([val for val in unique_properties_sidebar_raw if val.lower() != 'nan' and val.strip() != ''])
        unique_properties_sidebar = ["所有性质"] + unique_properties_sidebar_cleaned
        selected_property_filter = st.sidebar.selectbox("公司性质", unique_properties_sidebar, index=0, key="skills_prop_filter")
    else:
        selected_property_filter = "所有性质"
        st.sidebar.warning("列 'company_property' 不存在，无法按公司性质筛选。")


    filtered_df_with_skills = df_jobs_with_skills.copy()
    if job_catory_col and selected_category_filter != "所有类别":
        filtered_df_with_skills = filtered_df_with_skills[filtered_df_with_skills[job_catory_col] == selected_category_filter]
    if degree_name_cat_col and selected_degree_filter != "所有学历":
        filtered_df_with_skills = filtered_df_with_skills[filtered_df_with_skills[degree_name_cat_col] == selected_degree_filter]
    if company_property_col and selected_property_filter != "所有性质":
        filtered_df_with_skills = filtered_df_with_skills[filtered_df_with_skills[company_property_col] == selected_property_filter]

    if filtered_df_with_skills.empty: st.info("根据当前全局筛选条件，没有匹配的职位数据。"); st.stop()
    st.info(f"当前全局筛选条件下，共有 {len(filtered_df_with_skills)} 条职位数据参与分析。")

    tab1, tab2, tab3, tab4 = st.tabs(["🔥 热门技能分析", "🎓 热门专业分析", "🏷️ 公司标签分析", "📊 分类交叉洞察"])

    # ... (rest of your tab content, no changes needed there for this specific error) ...
    # Tab 1: 热门技能分析 (No changes from previous version based on request)
    with tab1:
        st.header("🔥 热门技能分析 (从职位名称与专业需求提取)")
        top_n_skills_display = st.slider("选择热门技能显示数量", 5, 50, 15, key="top_n_skills_display_slider_tab1_v2") # Key updated
        df_extracted_skills_freq = get_skill_frequency(
            filtered_df_with_skills,
            skill_list_column='extracted_skills_list',
            top_n=top_n_skills_display * 2
        )
        if not df_extracted_skills_freq.empty:
            col_skill_bar, col_skill_wc = st.columns([2, 3])
            with col_skill_bar:
                st.subheader(f"Top {top_n_skills_display} 热门技能")
                plot_bar_chart(df_extracted_skills_freq.head(top_n_skills_display), 'skill', 'count', title=f"热门技能词频 (Top {top_n_skills_display})", x_label="技能", y_label="出现次数", orientation='h')
            with col_skill_wc:
                st.subheader("热门技能词云")
                skill_freq_dict = {row['skill']: row['count'] for _, row in df_extracted_skills_freq.iterrows()}
                wc_skills = generate_wordcloud_from_freq_dict(skill_freq_dict, title="热门技能词云", max_words=70)
                display_wordcloud(wc_skills, "热门技能词云")
            st.divider()
            st.subheader("技能共现分析")
            top_n_cooc_pairs_display = st.slider("选择技能共现组合数量", 5, 30, 10, key="top_n_cooc_display_slider_tab1_v2") # Key updated
            min_freq_cooc_input = st.number_input("共现对最小频率", min_value=1, value=3, step=1, key="min_freq_cooc_input_tab1_v2") # Key updated
            min_skills_text_input = st.number_input("单文本最少技能数 (用于共现)", min_value=2, value=2, step=1, key="min_skills_text_input_tab1_v2") # Key updated

            df_cooccurrence = get_skill_cooccurrence_optimized(
                filtered_df_with_skills,
                skill_list_column='extracted_skills_list',
                top_n_cooc_pairs=top_n_cooc_pairs_display,
                min_cooc_frequency=min_freq_cooc_input,
                min_skills_in_one_text=min_skills_text_input
            )
            if not df_cooccurrence.empty:
                plot_bar_chart(df_cooccurrence, 'skill_pair', 'count', title=f"热门技能共现 (Top {top_n_cooc_pairs_display} 组合)", x_label="技能组合", y_label="共现次数", orientation='h')
            else:
                st.info("未能计算出满足条件的技能共现数据。尝试调整上方参数。")
        else:
            st.info("未能提取到技能信息或提取的技能频率过低。")

    # Tab 2: 热门专业分析 (No changes from previous version based on request)
    with tab2:
        st.header("🎓 热门专业分析")
        top_n_majors_display = st.slider("选择热门专业显示数量", 5, 30, 10, key="top_n_majors_slider_tab2_v2") # Key updated

        processed_major_col = 'processed_major' if 'processed_major' in filtered_df_with_skills.columns else None
        if not processed_major_col:
            st.warning("列 'processed_major' 不存在，无法进行标准化专业分析。")
        else:
            # Filter out generic major names before counting
            df_majors_for_count = filtered_df_with_skills[
                ~filtered_df_with_skills[processed_major_col].astype(str).str.lower().isin(['未知', '其他专业', '不限专业', '不限', 'nan', ''])
            ]
            df_std_majors_counts = get_top_n_counts(
                df_majors_for_count,
                processed_major_col,
                top_n=top_n_majors_display * 2
            )

            if not df_std_majors_counts.empty:
                col_major_bar, col_major_wc = st.columns([2, 3])
                with col_major_bar:
                    st.subheader(f"Top {top_n_majors_display} 标准化专业需求")
                    plot_bar_chart(df_std_majors_counts.head(top_n_majors_display),
                                   processed_major_col, 'count',
                                   title=f"热门标准化专业 (Top {top_n_majors_display})",
                                   x_label="专业名称 (标准化)", y_label="职位数量", orientation='h')
                with col_major_wc:
                    st.subheader("标准化专业词云")
                    std_major_freq_dict = {row[processed_major_col]: row['count'] for _, row in df_std_majors_counts.iterrows()}
                    wc_std_majors = generate_wordcloud_from_freq_dict(std_major_freq_dict, title="标准化专业词云", max_words=60)
                    display_wordcloud(wc_std_majors, "标准化专业词云")

                st.divider()
                st.subheader("🎯 专业需求深度洞察")

                if job_catory_col:
                    st.write("**不同职位类别 Top 3 热门专业**")
                    top_categories_for_major_analysis = filtered_df_with_skills[job_catory_col].value_counts().nlargest(5).index.tolist()
                    if top_categories_for_major_analysis:
                        major_by_category_list = []
                        for cat in top_categories_for_major_analysis:
                            df_cat = filtered_df_with_skills[filtered_df_with_skills[job_catory_col] == cat]
                            # Filter generic majors for each category
                            df_cat_majors_filtered = df_cat[
                                ~df_cat[processed_major_col].astype(str).str.lower().isin(['未知', '其他专业', '不限专业', '不限', 'nan', ''])
                            ]
                            if not df_cat_majors_filtered.empty:
                                df_cat_majors = get_top_n_counts(
                                    df_cat_majors_filtered,
                                    processed_major_col,
                                    top_n=3
                                )
                                if not df_cat_majors.empty:
                                    df_cat_majors[job_catory_col] = cat
                                    major_by_category_list.append(df_cat_majors)

                        if major_by_category_list:
                            df_major_by_category_plot = pd.concat(major_by_category_list)
                            if not df_major_by_category_plot.empty:
                                fig_major_cat = px.bar(df_major_by_category_plot,
                                                       x=processed_major_col, y="count", color=job_catory_col,
                                                       barmode="group", title="部分热门职位类别的 Top 3 专业需求",
                                                       labels={processed_major_col: "专业", "count": "职位数", job_catory_col: "职位类别"})
                                fig_major_cat.update_layout(xaxis_tickangle=-45)
                                st.plotly_chart(fig_major_cat, use_container_width=True)
                            else: st.caption("未能生成职位类别与专业对比图。")
                        else: st.caption("未能收集到按职位类别划分的专业数据。")
                    else: st.caption("无足够的职位类别数据进行专业对比分析。")
                else: st.caption(f"列 '{job_catory_col}' 不存在，无法进行职位类别与专业对比分析。")

                if 'avg_month_pay' in filtered_df_with_skills.columns and callable(globals().get('get_average_salary')):
                    st.write("**热门专业的平均月薪**")
                    top_major_names = df_std_majors_counts.head(top_n_majors_display)[processed_major_col].tolist()
                    df_salary_for_top_majors = filtered_df_with_skills[
                        filtered_df_with_skills[processed_major_col].isin(top_major_names) &
                        (filtered_df_with_skills['avg_month_pay'] > 0) # Filter for valid salaries
                    ]

                    if not df_salary_for_top_majors.empty:
                        df_avg_salary_by_major = get_average_salary(df_salary_for_top_majors, processed_major_col) # Assumes get_average_salary handles empty groups
                        if not df_avg_salary_by_major.empty:
                            df_avg_salary_by_major = df_avg_salary_by_major.sort_values(by='average_salary', ascending=False).head(top_n_majors_display)
                            plot_bar_chart(df_avg_salary_by_major, processed_major_col, 'average_salary',
                                           title=f"Top {top_n_majors_display} 专业平均月薪",
                                           x_label="专业名称", y_label="平均月薪 (元)", orientation='h') # Ensure units are consistent
                        else: st.caption("未能计算热门专业的平均薪资 (可能数据不足或全为0)。")
                    else: st.caption("无足够数据 (含有效薪资) 计算热门专业的平均薪资。")
                else: st.caption("缺少薪资数据或 `get_average_salary` 函数无法进行薪资分析。")
            else:
                st.info("未能统计到标准化专业需求。")

    # Tab 3: 公司标签分析
    with tab3:
        st.header("🏷️ 公司福利/标签分析")
        tags_list_col = 'tags_list' if 'tags_list' in filtered_df_with_skills.columns else None
        if not tags_list_col:
            st.warning("列 'tags_list' 不存在，无法进行公司标签分析。")
        else:
            top_n_tags_display = st.slider("选择热门公司标签显示数量", 5, 30, 10, key="top_n_tags_slider_tab3_v2") # Key updated
            df_tags_counts = get_word_counts_from_list_column(
                filtered_df_with_skills, tags_list_col, top_n=top_n_tags_display * 2, exclude_items={'无', 'nan', ''} # Added more excludes
            )

            if not df_tags_counts.empty:
                col_tag_bar, col_tag_wc = st.columns([2, 3])
                with col_tag_bar:
                    st.subheader(f"Top {top_n_tags_display} 公司标签")
                    plot_bar_chart(df_tags_counts.head(top_n_tags_display), 'item', 'count',
                                   title=f"热门公司标签 (Top {top_n_tags_display})",
                                   x_label="公司标签", y_label="出现次数", orientation='h')
                with col_tag_wc:
                    st.subheader("公司标签词云")
                    tag_freq_dict = {row['item']: row['count'] for _, row in df_tags_counts.iterrows()}
                    wc_tags = generate_wordcloud_from_freq_dict(tag_freq_dict, title="公司标签词云", max_words=60)
                    display_wordcloud(wc_tags, "公司标签词云")

                st.divider()
                st.subheader("🏷️ 公司标签深度洞察")

                st.write("**热门公司标签共现** (Top 5 组合)")
                temp_df_for_tag_cooc = filtered_df_with_skills[[tags_list_col]].copy()
                temp_df_for_tag_cooc.rename(columns={tags_list_col: 'cooc_items'}, inplace=True) # Use a generic name for the function
                df_tag_cooccurrence = get_skill_cooccurrence_optimized( # Reusing skill co-occurrence logic here
                    temp_df_for_tag_cooc,
                    skill_list_column='cooc_items', # Changed to generic name
                    top_n_cooc_pairs=5,
                    min_cooc_frequency=2,
                    min_skills_in_one_text=2 # This means min 2 tags for a job to be considered for co-occurrence
                )
                if not df_tag_cooccurrence.empty:
                    plot_bar_chart(df_tag_cooccurrence, 'skill_pair', 'count', # skill_pair is the output column name from the function
                                   title="热门公司标签共现", x_label="标签组合",
                                   y_label="共现次数", orientation='h')
                else: st.caption("未能计算出满足条件的标签共现数据。")

                company_scale_cat_col_tab3 = 'company_scale_cat' if 'company_scale_cat' in filtered_df_with_skills.columns else None
                if company_scale_cat_col_tab3 and not df_tags_counts.empty:
                    st.write("**特定标签下的公司规模分布**")

                    available_tags_for_selection = df_tags_counts['item'].tolist()
                    selected_tag_for_scale_analysis = st.selectbox(
                        "选择一个标签查看其公司规模分布:",
                        options=available_tags_for_selection,
                        index=0 if available_tags_for_selection else -1, # Handle empty options
                        key="tag_scale_dist_selector_tab3_v2"
                    )

                    if selected_tag_for_scale_analysis: # Ensure a tag is selected
                        df_with_selected_tag = filtered_df_with_skills[
                            filtered_df_with_skills[tags_list_col].apply(lambda x: selected_tag_for_scale_analysis in x if isinstance(x, (list, tuple)) else False) # Check type
                        ]
                        if not df_with_selected_tag.empty and df_with_selected_tag[company_scale_cat_col_tab3].notna().any(): # Check for scale data
                            scale_dist = df_with_selected_tag[company_scale_cat_col_tab3].value_counts().reset_index()
                            scale_dist.columns = [company_scale_cat_col_tab3, 'count']
                            fig_scale_dist = px.pie(scale_dist, names=company_scale_cat_col_tab3, values='count',
                                                    title=f"含标签 '{selected_tag_for_scale_analysis}' 的公司规模分布", hole=0.3)
                            st.plotly_chart(fig_scale_dist, use_container_width=True)
                        else: st.caption(f"没有公司同时拥有标签 '{selected_tag_for_scale_analysis}' 和有效的公司规模信息。")
                elif df_tags_counts.empty:
                     st.caption("无热门标签可供分析公司规模。")
                elif not company_scale_cat_col_tab3:
                    st.caption(f"列 'company_scale_cat' 不存在，无法进行公司规模与标签关联分析。")
            else:
                st.info("未能统计到公司标签信息。")

    # Tab 4: 分类交叉洞察
    with tab4:
        st.header("📊 分类交叉洞察")
        st.write("选择一个主要分析维度，然后探索不同指标下的数据洞察。")

        analysis_dimensions = {
            "职位类别": job_catory_col,
            "学历要求": degree_name_cat_col,
            "公司性质": company_property_col,
            "省份": "province_clean" if "province_clean" in filtered_df_with_skills.columns else None,
            "城市": "city_clean" if "city_clean" in filtered_df_with_skills.columns else None,
            "公司规模": 'company_scale_cat' if 'company_scale_cat' in filtered_df_with_skills.columns else None
        }
        valid_analysis_dimensions = {k: v for k, v in analysis_dimensions.items() if v is not None and filtered_df_with_skills[v].notna().any()} # Also check if col has data

        if not valid_analysis_dimensions:
            st.warning("没有可用的主要分析维度（相关列可能缺失或无数据）。")
            st.stop()

        selected_main_dim_label = st.selectbox(
            "选择主要分析维度:",
            options=list(valid_analysis_dimensions.keys()),
            index=0,
            key="main_dim_selector_tab4_v2" # Key updated
        )
        main_dim_col_tab4 = valid_analysis_dimensions[selected_main_dim_label]

        unique_values_raw_tab4 = filtered_df_with_skills[main_dim_col_tab4].astype(str).dropna().unique() # dropna here
        unique_values_in_dim_tab4 = sorted([val for val in unique_values_raw_tab4 if val.lower() != 'nan' and val.strip() != '']) # Clean again


        if len(unique_values_in_dim_tab4) > 25 and main_dim_col_tab4 not in ["province_clean", "city_clean"]:
            # For non-geo dimensions with many values, show top N
            top_n_values_df = get_top_n_counts(filtered_df_with_skills.dropna(subset=[main_dim_col_tab4]), main_dim_col_tab4, top_n=15)
            selectable_values_tab4 = top_n_values_df[main_dim_col_tab4].astype(str).tolist()

            if main_dim_col_tab4 == degree_name_cat_col: # Specific cleaning for degree 'nan'
                selectable_values_tab4 = [val for val in selectable_values_tab4 if val.lower() != 'nan']
            st.info(f"维度 '{selected_main_dim_label}' 的选项过多（{len(unique_values_in_dim_tab4)}个），仅展示最常见的15个。")
        elif not unique_values_in_dim_tab4:
            st.warning(f"维度 '{selected_main_dim_label}' 没有有效值可供选择。")
            selectable_values_tab4 = []
        else:
            selectable_values_tab4 = unique_values_in_dim_tab4

        selected_specific_values = st.multiselect(
            f"选择 '{selected_main_dim_label}' 下的具体分类进行分析/对比 (可多选):",
            options=selectable_values_tab4,
            default=selectable_values_tab4[0] if selectable_values_tab4 else None,
            key="specific_value_selector_tab4_v2" # Key updated
        )

        if not selected_specific_values:
            st.info(f"请至少选择一个 '{selected_main_dim_label}' 下的具体分类。")
        else:
            df_analysis_base_tab4 = filtered_df_with_skills[
                filtered_df_with_skills[main_dim_col_tab4].isin(selected_specific_values)
            ].copy()

            if df_analysis_base_tab4.empty:
                st.warning("根据当前选择，没有可供分析的数据。")
            else:
                analysis_content_options = [
                    "热门技能对比",
                    "热门专业对比",
                    "薪资水平对比",
                    "高薪技能画像"
                ]
                content_tabs = st.tabs(analysis_content_options)

                with content_tabs[0]: # 热门技能对比
                    st.subheader(f"🛠️ '{', '.join(selected_specific_values)}' 的热门技能对比")
                    skill_data_for_plot = []
                    top_n_skills_cat = st.slider("每个分类显示Top N技能", 3, 15, 5, key="top_n_skills_cat_tab4_slider_v2") # Key updated

                    for val in selected_specific_values:
                        df_val_specific = df_analysis_base_tab4[df_analysis_base_tab4[main_dim_col_tab4] == val]
                        if not df_val_specific.empty and 'extracted_skills_list' in df_val_specific.columns:
                            df_skills_freq = get_skill_frequency(df_val_specific, 'extracted_skills_list', top_n=top_n_skills_cat)
                            if not df_skills_freq.empty:
                                df_skills_freq[main_dim_col_tab4] = val
                                skill_data_for_plot.append(df_skills_freq)

                    if skill_data_for_plot:
                        df_plot_skills = pd.concat(skill_data_for_plot)
                        if not df_plot_skills.empty:
                            fig_skills = px.bar(df_plot_skills, x='skill', y='count', color=main_dim_col_tab4,
                                                barmode='group', title=f"热门技能对比 (Top {top_n_skills_cat})",
                                                labels={'skill': '技能', 'count': '职位数', main_dim_col_tab4: selected_main_dim_label})
                            fig_skills.update_layout(xaxis_tickangle=-45)
                            st.plotly_chart(fig_skills, use_container_width=True)

                            if 1 < len(selected_specific_values) <= 5 and top_n_skills_cat <=10:
                                st.write("**技能需求雷达图对比**")
                                all_top_skills_union = df_plot_skills['skill'].unique()
                                radar_df_list = []
                                for val in selected_specific_values:
                                    df_val_skills = df_plot_skills[df_plot_skills[main_dim_col_tab4] == val]
                                    data_row = {main_dim_col_tab4: val}
                                    for skill_item in all_top_skills_union:
                                        count = df_val_skills[df_val_skills['skill'] == skill_item]['count'].sum()
                                        data_row[skill_item] = count
                                    radar_df_list.append(data_row)
                                df_radar_data = pd.DataFrame(radar_df_list)
                                if not df_radar_data.empty and len(all_top_skills_union) >=3 : # Radar needs at least 3 points
                                    df_radar_melted = df_radar_data.melt(id_vars=main_dim_col_tab4, value_vars=all_top_skills_union,
                                                                        var_name='skill', value_name='count')
                                    try:
                                        fig_radar_skills = px.line_polar(df_radar_melted, r='count', theta='skill',
                                                                        color=main_dim_col_tab4, line_close=True,
                                                                        title="技能需求强度雷达图")
                                        st.plotly_chart(fig_radar_skills, use_container_width=True)
                                    except Exception as e_radar: st.caption(f"无法生成技能雷达图: {e_radar} (可能theta值不足)")
                                else: st.caption("无足够数据 (至少3种技能) 生成技能雷达图。")
                        else: st.info("在所选分类下未能提取到足够的技能数据进行对比。")
                    else: st.info("在所选分类下未能提取到技能数据。")

                with content_tabs[1]: # 热门专业对比
                    st.subheader(f"🎓 '{', '.join(selected_specific_values)}' 的热门专业对比")
                    major_data_for_plot = []
                    top_n_majors_cat = st.slider("每个分类显示Top N专业", 3, 15, 5, key="top_n_majors_cat_tab4_slider_v2") # Key updated

                    current_processed_major_col_tab4 = 'processed_major'
                    if current_processed_major_col_tab4 not in df_analysis_base_tab4.columns:
                        st.warning(f"列 '{current_processed_major_col_tab4}' 不存在于分析数据集中。")
                    else:
                        for val in selected_specific_values:
                            df_val_specific = df_analysis_base_tab4[df_analysis_base_tab4[main_dim_col_tab4] == val]
                            # Filter generic majors
                            df_val_specific_filtered = df_val_specific[
                                ~df_val_specific[current_processed_major_col_tab4].astype(str).str.lower().isin(['未知', '其他专业', '不限专业', '不限', 'nan', ''])
                            ]
                            if not df_val_specific_filtered.empty:
                                df_majors_freq = get_top_n_counts(df_val_specific_filtered, current_processed_major_col_tab4, top_n=top_n_majors_cat)
                                if not df_majors_freq.empty:
                                    df_majors_freq[main_dim_col_tab4] = val
                                    major_data_for_plot.append(df_majors_freq)

                        if major_data_for_plot:
                            df_plot_majors = pd.concat(major_data_for_plot)
                            if not df_plot_majors.empty:
                                fig_majors = px.bar(df_plot_majors, x=current_processed_major_col_tab4, y='count', color=main_dim_col_tab4,
                                                    barmode='group', title=f"热门专业对比 (Top {top_n_majors_cat})",
                                                    labels={current_processed_major_col_tab4: '专业 (标准化)', 'count': '职位数', main_dim_col_tab4: selected_main_dim_label})
                                fig_majors.update_layout(xaxis_tickangle=-45)
                                st.plotly_chart(fig_majors, use_container_width=True)
                            else: st.info("在所选分类下未能统计到足够的专业数据进行对比。")
                        else: st.info("在所选分类下未能统计到专业数据。")

                with content_tabs[2]: # 薪资水平对比
                    st.subheader(f"💰 '{', '.join(selected_specific_values)}' 的薪资水平对比")
                    if 'avg_month_pay' not in df_analysis_base_tab4.columns:
                        st.warning("数据中缺少 'avg_month_pay' 列，无法进行薪资分析。")
                    else:
                        df_salary_analysis = df_analysis_base_tab4[df_analysis_base_tab4['avg_month_pay'] > 0].copy()
                        if not df_salary_analysis.empty:
                            avg_salary_data = df_salary_analysis.groupby(main_dim_col_tab4, observed=True)['avg_month_pay'].agg(['mean', 'median', 'count']).reset_index()
                            avg_salary_data.columns = [main_dim_col_tab4, 'average_salary_k', 'median_salary_k', 'job_count_with_salary']
                            # avg_salary_data['average_salary_k'] already in K
                            avg_salary_data = avg_salary_data.sort_values(by='average_salary_k', ascending=False)

                            if not avg_salary_data.empty:
                                fig_avg_salary = px.bar(avg_salary_data, x=main_dim_col_tab4, y='average_salary_k', color=main_dim_col_tab4,
                                                        title="平均月薪对比 (K)",
                                                        labels={main_dim_col_tab4: selected_main_dim_label, 'average_salary_k': '平均月薪 (K/月)'})
                                st.plotly_chart(fig_avg_salary, use_container_width=True)

                            # df_salary_analysis['avg_month_pay_k'] already in K
                            fig_box_salary = px.box(df_salary_analysis, x=main_dim_col_tab4, y='avg_month_pay', color=main_dim_col_tab4, # y='avg_month_pay' which is already in K
                                                    title="月薪分布对比 (K)",
                                                    labels={main_dim_col_tab4: selected_main_dim_label, 'avg_month_pay': '月薪 (K/月)'})
                            st.plotly_chart(fig_box_salary, use_container_width=True)
                        else: st.info("在所选分类下没有有效的薪资数据。")

                with content_tabs[3]: # 高薪技能画像
                    st.subheader(f"💎 高薪技能画像")

                    target_category_value_tab4 = None
                    if not selected_specific_values:
                        st.info("请先在上方选择至少一个具体分类。")
                    elif len(selected_specific_values) == 1:
                        target_category_value_tab4 = selected_specific_values[0]
                        st.markdown(f"### 深入分析: **{target_category_value_tab4}**")
                    else:
                        st.write(f"您已选择了多个 '{selected_main_dim_label}' 分类: {', '.join(selected_specific_values)}")
                        target_category_value_tab4 = st.selectbox(
                            f"请选择其中一个 '{selected_main_dim_label}' 分类进行详细的高薪技能画像分析:",
                            options=selected_specific_values,
                            index=0,
                            key="single_cat_for_high_skill_analysis_tab4_v2" # Key updated
                        )
                        if target_category_value_tab4: # Ensure a selection is made from selectbox
                             st.markdown(f"### 深入分析: **{target_category_value_tab4}**")


                    if target_category_value_tab4:
                        df_target_cat_tab4 = df_analysis_base_tab4[
                            df_analysis_base_tab4[main_dim_col_tab4] == target_category_value_tab4
                        ].copy()

                        if 'avg_month_pay' not in df_target_cat_tab4.columns:
                             st.warning(f"分类 '{target_category_value_tab4}' 的数据中缺少 'avg_month_pay' 列。")
                        elif 'extracted_skills_list' not in df_target_cat_tab4.columns:
                             st.warning(f"分类 '{target_category_value_tab4}' 的数据中缺少 'extracted_skills_list' 列。")
                        else:
                            df_target_cat_filtered_salary = df_target_cat_tab4[df_target_cat_tab4['avg_month_pay'] > 0].copy()

                            if not df_target_cat_filtered_salary.empty:
                                top_skills_in_cat_df = get_skill_frequency(df_target_cat_filtered_salary, 'extracted_skills_list', top_n=20)
                                if not top_skills_in_cat_df.empty:
                                    top_skills_list = top_skills_in_cat_df['skill'].tolist()
                                    skill_salary_comparison = []
                                    overall_avg_salary_in_cat_k = df_target_cat_filtered_salary['avg_month_pay'].mean() # Already in K

                                    for skill_item in top_skills_list:
                                        df_with_skill = df_target_cat_filtered_salary[
                                            df_target_cat_filtered_salary['extracted_skills_list'].apply(lambda x: skill_item in x if isinstance(x, (list, tuple)) else False) # Check type
                                        ]
                                        if not df_with_skill.empty:
                                            avg_salary_with_skill_k = df_with_skill['avg_month_pay'].mean() # Already K
                                            median_salary_with_skill_k = df_with_skill['avg_month_pay'].median() # Already K
                                            job_count_with_skill = len(df_with_skill)
                                            salary_premium_vs_cat_avg = 0
                                            if overall_avg_salary_in_cat_k > 0: # Ensure no division by zero
                                                salary_premium_vs_cat_avg = ((avg_salary_with_skill_k - overall_avg_salary_in_cat_k) / overall_avg_salary_in_cat_k) * 100

                                            skill_salary_comparison.append({
                                                "技能": skill_item,
                                                "平均月薪(K)": avg_salary_with_skill_k,
                                                "中位数月薪(K)": median_salary_with_skill_k,
                                                "职位数": job_count_with_skill,
                                                f"溢价(vs '{target_category_value_tab4}'平均)": salary_premium_vs_cat_avg
                                            })

                                    if skill_salary_comparison:
                                        df_skill_salary = pd.DataFrame(skill_salary_comparison)
                                        df_skill_salary = df_skill_salary.sort_values(by=f"溢价(vs '{target_category_value_tab4}'平均)", ascending=False)
                                        st.write(f"**'{target_category_value_tab4}' 分类下，热门技能对应的薪资表现：**")
                                        format_dict_tab4 = {
                                            "平均月薪(K)": "{:,.1f}", # No need for " K" suffix, it's in the column name
                                            "中位数月薪(K)": "{:,.1f}",
                                            f"溢价(vs '{target_category_value_tab4}'平均)": "{:.1f}%"
                                        }
                                        st.dataframe(df_skill_salary.style.format(format_dict_tab4), use_container_width=True)
                                        df_plot_premium = df_skill_salary.nlargest(10, f"溢价(vs '{target_category_value_tab4}'平均)")
                                        if not df_plot_premium.empty:
                                            fig_premium = px.bar(df_plot_premium, x="技能", y=f"溢价(vs '{target_category_value_tab4}'平均)",
                                                                 color="技能", title=f"'{target_category_value_tab4}' 内薪资溢价最高的 Top 10 技能",
                                                                 labels={"技能":"技能", f"溢价(vs '{target_category_value_tab4}'平均)":"薪资溢价 (%)"})
                                            fig_premium.update_layout(showlegend=False)
                                            st.plotly_chart(fig_premium, use_container_width=True)
                                    else:
                                        st.info(f"未能计算 '{target_category_value_tab4}' 分类下的技能薪资关联数据。")
                                else:
                                    st.info(f"未能提取 '{target_category_value_tab4}' 分类下的热门技能。")
                            else:
                                st.info(f"在 '{target_category_value_tab4}' 分类下没有带有效薪资（大于0）的职位数据。")
                    else:
                        st.info("请从上方选择一个分类进行高薪技能画像分析。")


# --- sys.path modification needs to be at the very top of the script, before any streamlit command.
# --- However, the imports from utils.py are more critical.
# --- The typical way to run a multipage app is `streamlit run Main_App.py` from the project root.
# --- If Main_App.py handles sys.path correctly, pages should not need to modify it.

if __name__ == "__main__":
    # The set_page_config call has been moved to the top of the script.
    # This block is fine for directly running this page, but in a multipage app,
    # Streamlit calls the functions in page files directly.
    show_skills_majors_page()