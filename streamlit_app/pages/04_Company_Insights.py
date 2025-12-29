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
from streamlit_app.utils import (
    load_json_data, preprocess_jobs_data, JOBS_FILE,
    get_top_n_counts, get_average_salary,
    plot_bar_chart, plot_pie_chart,
    get_word_counts_from_list_column
)
from datetime import datetime
import plotly.express as px # Ensure plotly express is imported
import numpy as np # For np.nan

# Ensure page_config is called only once at the top of the script
if 'page_config_called_company_insight' not in st.session_state:
    st.set_page_config(page_title="公司招聘洞察", layout="wide", page_icon="🏢")
    st.session_state.page_config_called_company_insight = True

# --- 加载和预处理数据 ---
@st.cache_data(ttl=3600)
def load_and_prep_company_data():
    df_jobs_raw = load_json_data(JOBS_FILE)
    df_jobs = preprocess_jobs_data(df_jobs_raw) # IMPORTANT: Ensure this handles invalid company names and populates province_clean

    if 'company_name' in df_jobs.columns:
        df_jobs['company_name'] = df_jobs['company_name'].replace(r'^\s*$', np.nan, regex=True)
    else:
        df_jobs['company_name'] = pd.Series(dtype=str)

    # Ensure province_clean exists (critical for this fix)
    if 'province_clean' not in df_jobs.columns:
        df_jobs['province_clean'] = pd.Series(dtype=str)


    for col in ['company_property', 'company_scale_cat', 'company_scale_cleaned', 'city_clean', 'job_catory', 'degree_name_cat', 'tags_list', 'avg_month_pay', 'publish_date_dt']:
        if col not in df_jobs.columns:
            if 'cat' in col or 'degree' in col :
                 df_jobs[col] = pd.Series(dtype='category')
            elif 'pay' in col:
                 df_jobs[col] = pd.Series(dtype=float)
            elif 'date' in col:
                 df_jobs[col] = pd.Series(dtype='datetime64[ns, UTC]') # Added UTC for consistency
            else:
                 df_jobs[col] = pd.Series(dtype=str)
    return df_jobs

df_jobs_main = load_and_prep_company_data()

# --- 页面标题和数据更新时间 ---
st.title("🏢 公司招聘洞察")
if os.path.exists(JOBS_FILE):
    st.caption(f"数据源: `{os.path.basename(JOBS_FILE)}` (最后修改: {datetime.fromtimestamp(os.path.getmtime(JOBS_FILE)).strftime('%Y-%m-%d %H:%M:%S')})")

# --- 侧边栏过滤器 ---
st.sidebar.header("公司洞察过滤器")
selected_company_for_profile = "输入或选择公司..." # Initialize

if not df_jobs_main.empty:
    df_for_filters = df_jobs_main.dropna(subset=['company_name'])
    df_for_filters = df_for_filters[df_for_filters['company_name'].str.strip() != '']

    unique_company_properties = ["所有性质"]
    if not df_for_filters.empty and 'company_property' in df_for_filters.columns and df_for_filters['company_property'].notna().any():
        unique_company_properties.extend(sorted(df_for_filters['company_property'].dropna().unique().tolist()))
    selected_property = st.sidebar.selectbox(
        "筛选公司性质:", unique_company_properties, index=0, key="company_property_filter_adv_v2" # Key updated
    )

    unique_company_scales = ["所有规模"]
    if not df_for_filters.empty and 'company_scale_cat' in df_for_filters.columns and df_for_filters['company_scale_cat'].notna().any():
        # Check if it's categorical and has categories
        if isinstance(df_for_filters['company_scale_cat'].dtype, pd.CategoricalDtype) and not df_for_filters['company_scale_cat'].cat.categories.empty:
            unique_company_scales.extend(df_for_filters['company_scale_cat'].cat.categories.tolist())
        # Fallback if not categorical or empty categories, but column exists with data
        elif df_for_filters['company_scale_cat'].dropna().nunique() > 0 :
             unique_company_scales.extend(sorted(df_for_filters['company_scale_cat'].dropna().unique().tolist()))
        # Further fallback to _cleaned if _cat is problematic
        elif 'company_scale_cleaned' in df_for_filters.columns and df_for_filters['company_scale_cleaned'].notna().any():
             unique_company_scales.extend(sorted(df_for_filters['company_scale_cleaned'].dropna().unique().tolist()))
    selected_scale = st.sidebar.selectbox(
        "筛选公司规模:", unique_company_scales, index=0, key="company_scale_filter_adv_v2" # Key updated
    )
    
    # --- MODIFIED PROVINCE FILTER ---
    unique_provinces_company = ["所有省份"]
    if not df_for_filters.empty and 'province_clean' in df_for_filters.columns and df_for_filters['province_clean'].notna().any():
        # Get unique, sorted, non-empty, non-NaN province names
        prov_options = sorted([
            p for p in df_for_filters['province_clean'].dropna().unique() 
            if str(p).strip() != '' and pd.notna(p)
        ])
        unique_provinces_company.extend(prov_options)
    selected_province_company_filter = st.sidebar.selectbox( # Renamed to avoid confusion
        "筛选省份:", unique_provinces_company, index=0, key="company_province_filter_adv_v2" # Key updated
    )
    # --- END MODIFIED PROVINCE FILTER ---


    st.sidebar.markdown("---")
    st.sidebar.subheader("特定公司画像")
    
    # temp_filtered_df_for_companies is used to populate the company selectbox for profile view
    temp_filtered_df_for_companies = df_for_filters.copy()
    if selected_property != "所有性质": temp_filtered_df_for_companies = temp_filtered_df_for_companies[temp_filtered_df_for_companies['company_property'] == selected_property]
    
    scale_col_to_filter_on = None # Determine which scale column to use
    if 'company_scale_cat' in temp_filtered_df_for_companies.columns and temp_filtered_df_for_companies['company_scale_cat'].notna().any():
        scale_col_to_filter_on = 'company_scale_cat'
    elif 'company_scale_cleaned' in temp_filtered_df_for_companies.columns and temp_filtered_df_for_companies['company_scale_cleaned'].notna().any():
        scale_col_to_filter_on = 'company_scale_cleaned'

    if selected_scale != "所有规模" and scale_col_to_filter_on:
         temp_filtered_df_for_companies = temp_filtered_df_for_companies[temp_filtered_df_for_companies[scale_col_to_filter_on] == selected_scale]

    # Use the new province filter for populating company list for profile
    if selected_province_company_filter != "所有省份" and 'province_clean' in temp_filtered_df_for_companies.columns:
        temp_filtered_df_for_companies = temp_filtered_df_for_companies[temp_filtered_df_for_companies['province_clean'] == selected_province_company_filter]
    
    top_companies_for_select = ["输入或选择公司..."]
    if not temp_filtered_df_for_companies.empty:
         # Ensure company_name column exists and has data before calling get_top_n_counts
         if 'company_name' in temp_filtered_df_for_companies and temp_filtered_df_for_companies['company_name'].notna().any():
            top_companies_list = get_top_n_counts(temp_filtered_df_for_companies, 'company_name', top_n=50)['company_name'].tolist()
            top_companies_for_select.extend(top_companies_list)
    
    selected_company_for_profile_sb = st.sidebar.selectbox(
        "选择公司查看画像:", top_companies_for_select, index=0, key="company_profile_select_adv_sb_v2" # Key Updated
    )
    company_search_term = st.sidebar.text_input("或按名称搜索公司:", key="company_search_profile_sb_v2") # Key Updated

    # Logic to determine selected_company_for_profile
    if company_search_term:
        search_results_df = df_for_filters[df_for_filters['company_name'].str.contains(company_search_term, case=False, na=False)]
        search_results_unique = search_results_df['company_name'].unique()
        if len(search_results_unique) > 0:
            if len(search_results_unique) == 1:
                selected_company_for_profile = search_results_unique[0]
                st.sidebar.success(f"已选择: {selected_company_for_profile}")
            else:
                 selected_company_for_profile_radio = st.sidebar.radio("从搜索结果中选择:", ["选择一个公司查看画像..."] + search_results_unique.tolist(), index=0, key="company_radio_select_profile_v2") # Key Updated
                 if selected_company_for_profile_radio != "选择一个公司查看画像...":
                     selected_company_for_profile = selected_company_for_profile_radio
                 elif selected_company_for_profile_sb != "输入或选择公司...": # Fallback to selectbox if radio not chosen
                     selected_company_for_profile = selected_company_for_profile_sb
        else:
            st.sidebar.warning(f"未找到包含 '{company_search_term}' 的公司。")
            if selected_company_for_profile_sb != "输入或选择公司...":
                selected_company_for_profile = selected_company_for_profile_sb
    elif selected_company_for_profile_sb != "输入或选择公司...":
        selected_company_for_profile = selected_company_for_profile_sb


    # Apply global筛选逻辑 to company_display_df
    company_display_df = df_for_filters.copy() # Start fresh from df_for_filters
    if selected_property != "所有性质":
        company_display_df = company_display_df[company_display_df['company_property'] == selected_property]
    
    if selected_scale != "所有规模" and scale_col_to_filter_on: # Use the determined scale column
        company_display_df = company_display_df[company_display_df[scale_col_to_filter_on] == selected_scale]
    
    # --- APPLY MODIFIED PROVINCE FILTER to company_display_df ---
    if selected_province_company_filter != "所有省份" and 'province_clean' in company_display_df.columns:
        company_display_df = company_display_df[company_display_df['province_clean'] == selected_province_company_filter]
else:
    st.sidebar.warning("岗位数据未加载或公司名称信息缺失，无法应用过滤器。")
    company_display_df = pd.DataFrame()

# --- 主内容区 ---
# Check if df_jobs_main itself is empty first
if df_jobs_main.empty:
    st.error("未能加载岗位数据。")
# Then check if filters were applied and resulted in an empty df
elif company_display_df.empty and \
     ( (selected_property != "所有性质" if 'selected_property' in locals() else False) or \
       (selected_scale != "所有规模" if 'selected_scale' in locals() else False) or \
       (selected_province_company_filter != "所有省份" if 'selected_province_company_filter' in locals() else False) ) and \
     (selected_company_for_profile == "输入或选择公司..." or not selected_company_for_profile): # Check if profile not selected
    st.warning("当前全局筛选条件下没有匹配的岗位数据。")
# If company_display_df is empty but no significant filters applied (and profile not selected), it might be due to initial lack of valid company names
elif company_display_df.empty and not (selected_company_for_profile != "输入或选择公司..." and selected_company_for_profile):
    st.warning("数据已加载，但符合初步条件的公司数据为空或筛选后为空。")

else:
    # --- 特定公司画像 Tab ---
    if selected_company_for_profile != "输入或选择公司..." and selected_company_for_profile:
        st.header(f"🏢 {selected_company_for_profile} - 招聘画像")
        profile_df_all_jobs = df_jobs_main[df_jobs_main['company_name'] == selected_company_for_profile]
        
        if not profile_df_all_jobs.empty:
            st.metric("该公司发布岗位总数 (全量数据)", f"{len(profile_df_all_jobs):,}")
            
            profile_avg_salary_df = profile_df_all_jobs[profile_df_all_jobs['avg_month_pay'] > 0]
            profile_avg_salary = profile_avg_salary_df['avg_month_pay'].mean() if not profile_avg_salary_df.empty else 0
            profile_median_salary = profile_avg_salary_df['avg_month_pay'].median() if not profile_avg_salary_df.empty else 0
            
            prof_col1, prof_col2 = st.columns(2)
            prof_col1.metric("平均月薪 (K)", f"{profile_avg_salary:,.1f}" if profile_avg_salary > 0 else "N/A")
            prof_col2.metric("中位数月薪 (K)", f"{profile_median_salary:,.1f}" if profile_median_salary > 0 else "N/A")

            st.markdown("---")
            prof_chart_col1, prof_chart_col2 = st.columns(2)
            with prof_chart_col1:
                st.subheader("主要招聘职位类别")
                # Ensure 'job_catory' exists and has non-NA values
                if 'job_catory' in profile_df_all_jobs.columns and profile_df_all_jobs['job_catory'].notna().any():
                    cats_in_company = get_top_n_counts(profile_df_all_jobs.dropna(subset=['job_catory']), 'job_catory', 5)
                    if not cats_in_company.empty: plot_pie_chart(cats_in_company, 'job_catory', 'count', "职位类别分布", hole=0.3)
                    else: st.caption("职位类别数据不足")
                else: st.caption("无职位类别数据")

                st.subheader("主要招聘地区")
                 # Ensure 'city_clean' exists and has non-NA values (this should be province_clean for company profile's top regions)
                # For company profile, it might make more sense to show its top cities if province_clean is just one.
                # If a company operates in multiple provinces, then province_clean is fine.
                # If usually one province, then city_clean within that province.
                # Let's assume for profile, we show its top city_clean values if available and diverse.
                region_col_for_profile = 'city_clean' # Default to city_clean for company profile's regions
                if 'province_clean' in profile_df_all_jobs.columns and profile_df_all_jobs['province_clean'].nunique() > 1:
                    region_col_for_profile = 'province_clean' # If company spans multiple provinces, show provinces
                
                if region_col_for_profile in profile_df_all_jobs.columns and profile_df_all_jobs[region_col_for_profile].notna().any():
                    regions_in_company = get_top_n_counts(profile_df_all_jobs.dropna(subset=[region_col_for_profile]), region_col_for_profile, 5)
                    if not regions_in_company.empty: plot_bar_chart(regions_in_company, region_col_for_profile, 'count', "地区分布", "地区", "岗位数")
                    else: st.caption("地区数据不足")
                else: st.caption("无地区数据")


            with prof_chart_col2:
                st.subheader("学历要求分布")
                degree_col_profile = 'degree_name_cat' if 'degree_name_cat' in profile_df_all_jobs.columns and profile_df_all_jobs['degree_name_cat'].notna().any() else 'degree_name'
                if degree_col_profile in profile_df_all_jobs.columns and profile_df_all_jobs[degree_col_profile].notna().any():
                    degrees_in_company = get_top_n_counts(profile_df_all_jobs.dropna(subset=[degree_col_profile]), degree_col_profile, 5)
                    if not degrees_in_company.empty: plot_pie_chart(degrees_in_company, degree_col_profile, 'count', "学历要求", hole=0.3)
                    else: st.caption("学历数据不足")
                else: st.caption("无学历数据")


                st.subheader("热门福利标签")
                if 'tags_list' in profile_df_all_jobs.columns and profile_df_all_jobs['tags_list'].apply(lambda x: isinstance(x, (list, tuple)) and len(x) > 0).any():
                    tags_in_company = get_word_counts_from_list_column(profile_df_all_jobs, 'tags_list', 5)
                    if not tags_in_company.empty: plot_bar_chart(tags_in_company, 'item', 'count', "福利标签Top5", "福利", "提及次数", orientation='h')
                    else: st.caption("福利标签数据不足")
                else: st.caption("无福利标签数据")
            
            with st.expander("查看该公司所有岗位 (部分列)"):
                cols_to_show = ['job_name', 'city_clean', 'province_clean', 'job_catory', 'avg_month_pay', 'degree_name', 'publish_date_dt']
                existing_cols_to_show = [col for col in cols_to_show if col in profile_df_all_jobs.columns]
                if existing_cols_to_show:
                    st.dataframe(profile_df_all_jobs[existing_cols_to_show])
                else:
                    st.caption("没有可供显示的列。")
        else:
            st.warning(f"未找到公司 '{selected_company_for_profile}' 的详细数据。")
        st.divider()

    # --- 全局洞察 (基于侧边栏筛选器) ---
    st.header("全局公司洞察 (基于侧边栏筛选)")
    if company_display_df.empty:
        st.info("当前全局筛选条件下没有匹配的岗位数据可供分析。") # More informative than warning if it's due to filters
    else:
        st.metric("符合全局筛选的公司数量 (去重)", company_display_df['company_name'].nunique())
        st.metric("这些公司发布的岗位总数 (筛选后)", f"{len(company_display_df):,}")
        st.divider()

        st.subheader("公司性质与规模分布 (筛选后)")
        col_prop, col_sca = st.columns(2)
        
        # Determine the scale column to use for plotting (consistent with filter population)
        scale_col_for_plots = None
        if 'company_scale_cat' in company_display_df.columns and company_display_df['company_scale_cat'].notna().any():
            scale_col_for_plots = 'company_scale_cat'
        elif 'company_scale_cleaned' in company_display_df.columns and company_display_df['company_scale_cleaned'].notna().any():
            scale_col_for_plots = 'company_scale_cleaned'
            
        with col_prop:
            if selected_property == "所有性质":
                if 'company_property' in company_display_df.columns and company_display_df['company_property'].notna().any():
                    prop_counts = get_top_n_counts(company_display_df.dropna(subset=['company_property']), 'company_property', top_n=10)
                    if not prop_counts.empty: plot_pie_chart(prop_counts, 'company_property', 'count', "公司性质分布 (Top 10)")
                    else: st.caption("无公司性质数据")
                else: st.caption("无公司性质数据")
            else:
                st.info(f"当前已筛选公司性质: {selected_property}")
                if scale_col_for_plots and company_display_df[scale_col_for_plots].notna().any():
                    scale_in_prop_df = get_top_n_counts(company_display_df.dropna(subset=[scale_col_for_plots]), scale_col_for_plots, top_n=7)
                    if not scale_in_prop_df.empty:
                        if isinstance(company_display_df[scale_col_for_plots].dtype, pd.CategoricalDtype) and not company_display_df[scale_col_for_plots].cat.categories.empty:
                             # Use the original categories for ordering if present and valid
                            cat_order = [cat for cat in company_display_df[scale_col_for_plots].cat.categories if cat in scale_in_prop_df[scale_col_for_plots].unique()]
                            if cat_order:
                                scale_in_prop_df[scale_col_for_plots] = pd.Categorical(scale_in_prop_df[scale_col_for_plots], categories=cat_order, ordered=True)
                                scale_in_prop_df = scale_in_prop_df.sort_values(scale_col_for_plots)
                        plot_bar_chart(scale_in_prop_df, scale_col_for_plots, 'count', f"{selected_property}下的公司规模分布", "公司规模", "岗位数量")
                    else: st.caption("无公司规模数据")
                else: st.caption("无公司规模数据")
        with col_sca:
            if selected_scale == "所有规模":
                if scale_col_for_plots and company_display_df[scale_col_for_plots].notna().any():
                    scale_counts = get_top_n_counts(company_display_df.dropna(subset=[scale_col_for_plots]), scale_col_for_plots, top_n=7)
                    if not scale_counts.empty:
                        if isinstance(company_display_df[scale_col_for_plots].dtype, pd.CategoricalDtype) and not company_display_df[scale_col_for_plots].cat.categories.empty:
                            cat_order_scale = [cat for cat in company_display_df[scale_col_for_plots].cat.categories if cat in scale_counts[scale_col_for_plots].unique()]
                            if cat_order_scale:
                                scale_counts[scale_col_for_plots] = pd.Categorical(scale_counts[scale_col_for_plots], categories=cat_order_scale, ordered=True)
                                scale_counts = scale_counts.sort_values(scale_col_for_plots)
                        plot_bar_chart(scale_counts, scale_col_for_plots, 'count', "公司规模岗位数量分布", "公司规模", "岗位数量")
                    else: st.caption("无公司规模数据")
                else: st.caption("无公司规模数据")
            else:
                st.info(f"当前已筛选公司规模: {selected_scale}")
                if 'company_property' in company_display_df.columns and company_display_df['company_property'].notna().any():
                    prop_in_scale_df = get_top_n_counts(company_display_df.dropna(subset=['company_property']), 'company_property', top_n=7)
                    if not prop_in_scale_df.empty: plot_pie_chart(prop_in_scale_df, 'company_property', 'count', f"{selected_scale}规模下的公司性质分布")
                    else: st.caption("无公司性质数据")
                else: st.caption("无公司性质数据")


        st.divider()
        st.subheader("招聘活跃公司排行 (Top 20, 基于当前筛选)")
        if 'company_name' in company_display_df.columns and company_display_df['company_name'].notna().any():
            active_companies_df = get_top_n_counts(company_display_df, 'company_name', top_n=20)
            if not active_companies_df.empty: plot_bar_chart(active_companies_df, 'company_name', 'count', "发布岗位最多的公司", "公司名称", "岗位数量", orientation='h')
            else: st.caption("当前筛选下无公司招聘数据")
        else: st.caption("缺少公司名称数据")
        
        if 'company_name' in company_display_df.columns and company_display_df['company_name'].nunique() >= 2 and \
           'avg_month_pay' in company_display_df.columns and not company_display_df[company_display_df['avg_month_pay']>0].empty :
            st.subheader("部分公司平均薪资概览 (Top 15发布岗位公司, 基于当前筛选)")
            company_avg_salary_df = get_average_salary(company_display_df.dropna(subset=['company_name', 'avg_month_pay']), 'company_name')
            if not company_avg_salary_df.empty:
                company_avg_salary_df_sorted = company_avg_salary_df.sort_values('job_count', ascending=False).head(15)
                if not company_avg_salary_df_sorted.empty and company_avg_salary_df_sorted['average_salary'].notna().any(): # Check if there's any valid salary to plot
                    plot_bar_chart(company_avg_salary_df_sorted.sort_values('average_salary', ascending=False), 'company_name', 'average_salary',
                                   "部分公司平均月薪 (K)", "公司名称", "平均月薪 (K)", orientation='h', color='job_count')
                    st.caption("注：公司平均薪资受该公司发布的职位类型和数量影响较大，仅供参考。")
                else: st.caption("薪资数据不足或公司数量不足以进行此图表展示。")
            else: st.caption("未能计算公司平均薪资。")
        
        st.divider()
        st.subheader("不同类型公司的热门招聘职位类别 (Top 5)")
        # Make sure job_catory column exists and has data before proceeding
        if 'job_catory' not in company_display_df.columns or not company_display_df['job_catory'].notna().any():
            st.caption("职位类别数据不足，无法进行此分析。")
        elif selected_property != "所有性质" or selected_scale != "所有规模":
            if selected_property != "所有性质":
                st.markdown(f"#### {selected_property} 类公司热门职位类别")
                prop_job_cats = get_top_n_counts(company_display_df.dropna(subset=['job_catory']), 'job_catory', 5)
                if not prop_job_cats.empty: plot_bar_chart(prop_job_cats, 'job_catory', 'count', f"{selected_property}热门类别", "职位类别", "岗位数", orientation='h')
                else: st.caption("该性质公司无职位类别数据")

            if selected_scale != "所有规模" and scale_col_for_plots: # Check if scale_col_for_plots is determined
                st.markdown(f"#### {selected_scale} 规模公司热门职位类别")
                scale_job_cats = get_top_n_counts(company_display_df.dropna(subset=['job_catory']), 'job_catory', 5)
                if not scale_job_cats.empty: plot_bar_chart(scale_job_cats, 'job_catory', 'count', f"{selected_scale}热门类别", "职位类别", "岗位数", orientation='h')
                else: st.caption("该规模公司无职位类别数据")
        else: 
            if 'company_property' in company_display_df.columns and company_display_df['company_property'].notna().any():
                prop_groups = company_display_df.dropna(subset=['company_property', 'job_catory']).groupby('company_property')['job_catory'].apply(
                    lambda x: x.value_counts().nlargest(3).index.tolist() if not x.empty else []
                ).reset_index()
                if not prop_groups.empty:
                    st.markdown("#### 不同性质公司的Top3热门职位类别 (示例)")
                    st.dataframe(prop_groups.rename(columns={'company_property':'公司性质', 'job_catory':'热门职位类别Top3'}))
                else: st.caption("数据不足以按公司性质对比热门职位。")
            else: st.caption("公司性质数据不足。")


        st.divider()
        if 'tags_list' in company_display_df.columns and company_display_df['tags_list'].apply(lambda x: isinstance(x, (list, tuple)) and len(x) > 0).any():
            st.subheader("公司福利标签分析 (基于当前筛选)")
            tags_df_overall = get_word_counts_from_list_column(company_display_df, 'tags_list', top_n=10)
            if not tags_df_overall.empty:
                plot_bar_chart(tags_df_overall, 'item', 'count', "常见公司福利标签 (筛选后整体)", "福利标签", "提及次数", orientation='h')

            if selected_property == "所有性质" and \
               'company_property' in company_display_df.columns and \
               company_display_df['company_property'].nunique() > 1 and \
               company_display_df['company_property'].nunique() <= 5: # Limit to a few properties for comparison
                st.markdown("##### 不同性质公司的Top5福利标签")
                props_to_compare = company_display_df['company_property'].value_counts().nlargest(3).index # Compare top 3
                for prop_val in props_to_compare:
                    prop_specific_tags_df = company_display_df[company_display_df['company_property'] == prop_val]
                    if not prop_specific_tags_df.empty and prop_specific_tags_df['tags_list'].apply(lambda x: isinstance(x, (list, tuple)) and len(x) > 0).any():
                        tags_for_prop = get_word_counts_from_list_column(prop_specific_tags_df, 'tags_list', top_n=5)
                        if not tags_for_prop.empty:
                            plot_bar_chart(tags_for_prop, 'item', 'count', f"{prop_val} - Top 5 福利", "福利", "提及次数", orientation='h')
                        else: st.caption(f"{prop_val}类公司无热门福利标签。")
                    else: st.caption(f"{prop_val}类公司无福利标签数据。")
            elif selected_property != "所有性质":
                 st.info(f"已筛选公司性质: {selected_property} (上方已显示其整体福利标签)")
        else:
            st.info("当前筛选条件下，未能统计出有效的公司福利标签。")