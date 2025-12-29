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
import plotly.express as px
from streamlit_app.utils import (
    load_json_data, preprocess_jobs_data, JOBS_FILE,
    calculate_time_deltas, get_job_freshness_distribution,
    plot_bar_chart, plot_pie_chart, get_average_salary, get_top_n_counts
)
from datetime import datetime

st.set_page_config(page_title="岗位时效性深度分析", layout="wide", page_icon="⏱️")

# --- 加载和预处理数据 ---
@st.cache_data(ttl=3600)
def load_and_prep_timedelta_data():
    df_jobs_raw = load_json_data(JOBS_FILE)
    if df_jobs_raw.empty:
        st.error(f"无法从 {JOBS_FILE} 加载原始数据。")
        return pd.DataFrame()
    df_jobs = preprocess_jobs_data(df_jobs_raw)
    if df_jobs.empty:
        st.error("预处理数据后DataFrame为空。")
        return pd.DataFrame()
    df_jobs_with_deltas = calculate_time_deltas(df_jobs)
    return df_jobs_with_deltas

df_jobs_timed_main = load_and_prep_timedelta_data()

# --- 页面标题和数据更新时间 ---
st.title("⏱️ 岗位时效性深度分析")
if os.path.exists(JOBS_FILE):
    st.caption(f"数据源: `{os.path.basename(JOBS_FILE)}` (最后修改: {datetime.fromtimestamp(os.path.getmtime(JOBS_FILE)).strftime('%Y-%m-%d %H:%M:%S')})")
else:
    st.caption(f"数据源文件 `{os.path.basename(JOBS_FILE)}` 未找到。")


# --- 侧边栏过滤器 ---
st.sidebar.header("时效性分析过滤器")
if not df_jobs_timed_main.empty:
    # 1. 省份选择
    unique_provinces_time = ["所有省份"] + sorted(df_jobs_timed_main['province_clean'].dropna().unique().tolist())
    selected_province_time = st.sidebar.selectbox(
        "选择省份:", unique_provinces_time, index=0, key="timedelta_province_filter"
    )

    # 2. 城市选择 (动态根据省份)
    if selected_province_time == "所有省份":
        available_cities_time = ["所有城市"] + sorted(df_jobs_timed_main['city_clean'].dropna().unique().tolist())
    else:
        # 筛选出选定省份下的城市
        cities_in_province = df_jobs_timed_main[df_jobs_timed_main['province_clean'] == selected_province_time]['city_clean'].dropna().unique().tolist()
        available_cities_time = ["所有城市"] + sorted(cities_in_province)
    
    selected_city_time = st.sidebar.selectbox(
        "选择城市:", available_cities_time, index=0, key="timedelta_city_filter_adv" # 保持 key 不变或更新
    )

    # 3. 职位类别选择
    unique_categories_time = ["所有类别"] + sorted(df_jobs_timed_main['job_catory'].dropna().unique().tolist())
    selected_category_time = st.sidebar.selectbox(
        "选择职位类别:", unique_categories_time, index=0, key="timedelta_cat_filter_adv"
    )
    
    # 4. 公司规模选择
    # 检查 company_scale_cat 是否存在且是 Categorical 类型
    if 'company_scale_cat' in df_jobs_timed_main.columns and pd.api.types.is_categorical_dtype(df_jobs_timed_main['company_scale_cat']):
        # 从 category 获取有序列表，并确保 "所有规模" 在最前面
        scale_categories = df_jobs_timed_main['company_scale_cat'].cat.categories.tolist()
        unique_scales_time = ["所有规模"] + [cat for cat in scale_categories if cat != "所有规模"] # 避免重复
    elif 'company_scale_cleaned_mapped' in df_jobs_timed_main.columns: # Fallback
         unique_scales_time = ["所有规模"] + sorted(df_jobs_timed_main['company_scale_cleaned_mapped'].dropna().unique().tolist())
    elif 'company_scale_cleaned' in df_jobs_timed_main.columns: # Further Fallback
        unique_scales_time = ["所有规模"] + sorted(df_jobs_timed_main['company_scale_cleaned'].dropna().unique().tolist())
    else:
        unique_scales_time = ["所有规模"]
        st.sidebar.warning("无法找到合适的公司规模列。")

    selected_scale_time = st.sidebar.selectbox(
        "选择公司规模:", unique_scales_time, index=0, key="timedelta_scale_filter"
    )

    # 5. 公司性质选择
    unique_properties_time = ["所有性质"] + sorted(df_jobs_timed_main['company_property'].dropna().unique().tolist())
    selected_property_time = st.sidebar.selectbox(
        "选择公司性质:", unique_properties_time, index=0, key="timedelta_property_filter"
    )
    
    # 应用筛选逻辑
    timedelta_display_df = df_jobs_timed_main.copy()
    if selected_province_time != "所有省份":
        timedelta_display_df = timedelta_display_df[timedelta_display_df['province_clean'] == selected_province_time]
        # 如果省份被选中，城市筛选也应该在已筛选的省份数据基础上进行
        if selected_city_time != "所有城市": # 确保不是选“所有城市”的情况
            timedelta_display_df = timedelta_display_df[timedelta_display_df['city_clean'] == selected_city_time]
    elif selected_city_time != "所有城市": # 如果省份是"所有省份"，但城市不是"所有城市"
         timedelta_display_df = timedelta_display_df[timedelta_display_df['city_clean'] == selected_city_time]


    if selected_category_time != "所有类别":
        timedelta_display_df = timedelta_display_df[timedelta_display_df['job_catory'] == selected_category_time]
    
    # 公司规模筛选，使用正确的列名
    scale_column_to_filter = None
    if 'company_scale_cat' in timedelta_display_df.columns and pd.api.types.is_categorical_dtype(timedelta_display_df['company_scale_cat']):
        scale_column_to_filter = 'company_scale_cat'
    elif 'company_scale_cleaned_mapped' in timedelta_display_df.columns:
        scale_column_to_filter = 'company_scale_cleaned_mapped'
    elif 'company_scale_cleaned' in timedelta_display_df.columns:
        scale_column_to_filter = 'company_scale_cleaned'

    if selected_scale_time != "所有规模" and scale_column_to_filter:
        timedelta_display_df = timedelta_display_df[timedelta_display_df[scale_column_to_filter] == selected_scale_time]
    
    if selected_property_time != "所有性质":
        timedelta_display_df = timedelta_display_df[timedelta_display_df['company_property'] == selected_property_time]
else:
    st.sidebar.warning("岗位数据未加载或预处理失败，无法应用过滤器。")
    timedelta_display_df = pd.DataFrame() # Ensure it's a DataFrame

# --- 主内容区 ---
if df_jobs_timed_main.empty:
    st.error("未能加载岗位数据或计算时间差失败。") # 错误已在加载时显示，这里可以简化
elif timedelta_display_df.empty and \
     (selected_province_time != "所有省份" or selected_city_time != "所有城市" or \
      selected_category_time != "所有类别" or selected_scale_time != "所有规模" or \
      selected_property_time != "所有性质"):
    st.warning("当前筛选条件下没有匹配的岗位数据。")
else:
    st.header("岗位新鲜度与更新行为洞察 (基于当前筛选)")
    
    # 只有在 timedelta_display_df 非空时才显示 metric
    if not timedelta_display_df.empty:
        st.metric("符合分析条件的岗位数量", f"{len(timedelta_display_df):,}")
    else: # 如果是因为筛选后为空，但原始数据存在
        if not df_jobs_timed_main.empty: # 确保不是因为原始数据就空
             st.info("当前筛选条件下没有匹配的岗位数据。")
        # else: # 如果原始数据就空，错误已在上面显示
    
    st.divider()

    tab_freshness, tab_update_freq, tab_cross_time = st.tabs(["🌟 岗位新鲜度", "🔄 更新频率分析", "🔗 时效性交叉分析"])

    with tab_freshness:
        st.subheader("岗位新鲜度 (发布至今时长)")
        if timedelta_display_df.empty or 'job_age_days' not in timedelta_display_df.columns or timedelta_display_df['job_age_days'].dropna().empty:
            st.info("缺少有效的岗位年龄数据 (job_age_days) 或当前筛选无数据。")
        else:
            freshness_df = get_job_freshness_distribution(timedelta_display_df)
            if not freshness_df.empty:
                plot_bar_chart(freshness_df, 'freshness_range', 'count', "岗位新鲜度分布", "发布时长区间", "岗位数量")
            else:
                st.info("无法生成岗位新鲜度分布图 (数据不足)。")
            
            avg_job_age = timedelta_display_df['job_age_days'].mean()
            median_job_age = timedelta_display_df['job_age_days'].median()
            col_age1, col_age2 = st.columns(2)
            col_age1.metric("平均岗位年龄 (天)", f"{avg_job_age:.1f}" if pd.notna(avg_job_age) else "N/A")
            col_age2.metric("岗位年龄中位数 (天)", f"{median_job_age:.1f}" if pd.notna(median_job_age) else "N/A")

            st.markdown("---")
            st.subheader("不同维度的岗位平均年龄对比")
            compare_dim_age = st.selectbox(
                "选择对比维度查看平均岗位年龄:",
                ["职位类别", "城市", "公司规模", "公司性质", "省份"], # 添加省份
                key="age_compare_dim_select"
            )
            dim_col_map_age = {
                "职位类别": "job_catory", "城市": "city_clean", "省份": "province_clean",
                "公司规模": scale_column_to_filter if scale_column_to_filter else 'company_scale_cat', # 使用上面确定的规模列
                "公司性质": "company_property"
            }
            selected_dim_col_age = dim_col_map_age.get(compare_dim_age)

            if selected_dim_col_age and selected_dim_col_age in timedelta_display_df.columns:
                avg_age_by_dim_df = timedelta_display_df.groupby(selected_dim_col_age, observed=False)['job_age_days'].mean().reset_index()
                avg_age_by_dim_df.rename(columns={'job_age_days': 'avg_job_age_days'}, inplace=True)
                
                dim_counts = timedelta_display_df[selected_dim_col_age].value_counts()
                valid_dims_for_age = dim_counts[dim_counts >= 10].index # 至少有10个岗位
                avg_age_by_dim_df = avg_age_by_dim_df[avg_age_by_dim_df[selected_dim_col_age].isin(valid_dims_for_age)]
                avg_age_by_dim_df = avg_age_by_dim_df.sort_values('avg_job_age_days', ascending=False).head(15)

                if not avg_age_by_dim_df.empty:
                    plot_bar_chart(avg_age_by_dim_df, selected_dim_col_age, 'avg_job_age_days',
                                   f"不同{compare_dim_age}的平均岗位年龄 (天)", compare_dim_age, "平均岗位年龄 (天)", orientation='h')
                else:
                    st.info(f"当前筛选下，按'{compare_dim_age}'分组的有效数据不足 (需要至少10个样本)。")
            elif not selected_dim_col_age:
                 st.warning(f"选择的对比维度 '{compare_dim_age}' 没有有效的列名映射。")


    with tab_update_freq:
        st.subheader("岗位信息更新频率 (发布到最后更新的小时数)")
        if timedelta_display_df.empty or'publish_to_update_hours' not in timedelta_display_df.columns or timedelta_display_df['publish_to_update_hours'].dropna().empty:
            st.info("缺少有效的岗位更新时间差数据 (publish_to_update_hours) 或当前筛选无数据。")
        else:
            valid_update_df = timedelta_display_df[timedelta_display_df['publish_to_update_hours'] >= 0].copy()
            if not valid_update_df.empty:
                fig_update_hist = px.histogram(valid_update_df, x="publish_to_update_hours", nbins=30,
                                               title="岗位更新时间差分布 (小时)",
                                               labels={'publish_to_update_hours': '发布到更新的小时数'}, marginal="box")
                st.plotly_chart(fig_update_hist, use_container_width=True)

                avg_update_hours = valid_update_df['publish_to_update_hours'].mean()
                median_update_hours = valid_update_df['publish_to_update_hours'].median()
                col_update1, col_update2 = st.columns(2)
                col_update1.metric("平均更新耗时 (小时)", f"{avg_update_hours:.1f}" if pd.notna(avg_update_hours) else "N/A")
                col_update2.metric("更新耗时中位数 (小时)", f"{median_update_hours:.1f}" if pd.notna(median_update_hours) else "N/A")

                st.markdown("---")
                st.subheader("不同维度的平均更新耗时对比")
                compare_dim_update = st.selectbox(
                    "选择对比维度查看平均更新耗时:",
                    ["职位类别", "城市", "公司规模", "公司性质", "省份"], # 添加省份
                    key="update_compare_dim_select"
                )
                dim_col_map_update = {
                    "职位类别": "job_catory", "城市": "city_clean", "省份": "province_clean",
                    "公司规模": scale_column_to_filter if scale_column_to_filter else 'company_scale_cat',
                    "公司性质": "company_property"
                }
                selected_dim_col_update = dim_col_map_update.get(compare_dim_update)

                if selected_dim_col_update and selected_dim_col_update in valid_update_df.columns:
                    avg_update_by_dim_df = valid_update_df.groupby(selected_dim_col_update, observed=False)['publish_to_update_hours'].mean().reset_index()
                    avg_update_by_dim_df.rename(columns={'publish_to_update_hours': 'avg_update_hours'}, inplace=True)
                    
                    dim_counts_update = valid_update_df[selected_dim_col_update].value_counts()
                    valid_dims_for_update = dim_counts_update[dim_counts_update >= 10].index
                    avg_update_by_dim_df = avg_update_by_dim_df[avg_update_by_dim_df[selected_dim_col_update].isin(valid_dims_for_update)]
                    avg_update_by_dim_df = avg_update_by_dim_df.sort_values('avg_update_hours', ascending=True).head(15)

                    if not avg_update_by_dim_df.empty:
                        plot_bar_chart(avg_update_by_dim_df, selected_dim_col_update, 'avg_update_hours',
                                       f"不同{compare_dim_update}的平均更新耗时 (小时)", compare_dim_update, "平均更新耗时 (小时)", orientation='h')
                    else:
                        st.info(f"当前筛选下，按'{compare_dim_update}'分组的有效数据不足 (需要至少10个样本)。")
                elif not selected_dim_col_update:
                    st.warning(f"选择的对比维度 '{compare_dim_update}' 没有有效的列名映射。")
            else:
                st.info("当前筛选条件下，无有效的岗位更新时间差数据。")

    with tab_cross_time:
        st.subheader("时效性与薪资的关联分析") # 简化标题，主要关注薪资
        if timedelta_display_df.empty or 'job_age_days' not in timedelta_display_df.columns or 'avg_month_pay' not in timedelta_display_df.columns:
            st.info("缺少岗位年龄或平均薪资数据进行交叉分析，或当前筛选无数据。")
        else:
            st.markdown("##### 岗位年龄与平均薪资")
            df_age_salary = timedelta_display_df[['job_age_days', 'avg_month_pay']].copy()
            df_age_salary.dropna(inplace=True)
            df_age_salary = df_age_salary[(df_age_salary['job_age_days'] >= 0) & (df_age_salary['avg_month_pay'] > 0)]

            if not df_age_salary.empty:
                age_bins = [0, 7, 30, 90, 180, 365, float('inf')]
                age_labels = ['1周内', '1周-1月', '1-3月', '3-6月', '半年-1年', '1年以上']
                df_age_salary['job_age_group'] = pd.cut(df_age_salary['job_age_days'], bins=age_bins, labels=age_labels, right=False)
                
                # 按年龄组计算平均/中位数薪资
                avg_salary_by_age_group = df_age_salary.groupby('job_age_group', observed=False).agg(
                    average_salary=('avg_month_pay', 'mean'),
                    median_salary=('avg_month_pay', 'median'),
                    count=('avg_month_pay', 'count')
                ).reset_index()
                # 确保job_age_group是categorical且有序，以便绘图
                avg_salary_by_age_group['job_age_group'] = pd.Categorical(avg_salary_by_age_group['job_age_group'], categories=age_labels, ordered=True)
                avg_salary_by_age_group.sort_values('job_age_group', inplace=True)

                avg_salary_by_age_group = avg_salary_by_age_group[avg_salary_by_age_group['count'] >= 5] 

                if not avg_salary_by_age_group.empty:
                    fig_age_salary_bar = px.bar(avg_salary_by_age_group, x='job_age_group', y='average_salary',
                                                color='median_salary', title='不同年龄段岗位的平均/中位数薪资',
                                                labels={'job_age_group':'岗位年龄段', 'average_salary':'平均月薪(K)', 'median_salary':'中位数月薪(K)'},
                                                color_continuous_scale=px.colors.sequential.Viridis, # 添加颜色标度
                                                text_auto='.1f')
                    st.plotly_chart(fig_age_salary_bar, use_container_width=True)

                    fig_age_salary_box = px.box(df_age_salary, x='job_age_group', y='avg_month_pay',
                                                title='不同年龄段岗位的薪资分布 (箱线图)',
                                                labels={'job_age_group':'岗位年龄段', 'avg_month_pay':'平均月薪(K)'},
                                                category_orders={"job_age_group": age_labels})
                    st.plotly_chart(fig_age_salary_box, use_container_width=True)
                else:
                    st.info("按岗位年龄段分组后数据不足 (需要至少5个样本)。")
            else:
                st.info("岗位年龄与薪资数据不足。")
            
    st.caption("注：岗位时效性分析依赖于数据中的 `publish_date` 和 `update_date` 字段的准确性。")