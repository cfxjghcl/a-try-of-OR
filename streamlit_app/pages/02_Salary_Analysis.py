import sys
import os

# --- sys.path modification ---
# Use __file__ to get the path of the current script
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
)
import plotly.express as px
from datetime import datetime
import numpy as np

if 'page_config_called_salary_analysis' not in st.session_state:
    st.set_page_config(page_title="薪资深度分析", layout="wide", page_icon="💰")
    st.session_state.page_config_called_salary_analysis = True

# --- 加载和预处理数据 ---
@st.cache_data(ttl=3600)
def load_and_prep_salary_page_data():
    df_jobs_raw = load_json_data(JOBS_FILE)
    df_jobs = preprocess_jobs_data(df_jobs_raw) # Assumes preprocess_jobs_data populates 'province_clean' and 'city_clean'

    # Ensure work_year_cat is created and ordered (copied from your provided code)
    if 'work_year' in df_jobs.columns and 'work_year_cat' not in df_jobs.columns:
        df_jobs['work_year_numeric'] = pd.to_numeric(df_jobs['work_year'], errors='coerce')
        bins = [-np.inf, 0, 1, 3, 5, 10, np.inf] 
        labels = ['经验不限', '1年以内', '1-3年', '3-5年', '5-10年', '10年以上']
        if df_jobs['work_year_numeric'].notna().any():
            df_jobs['work_year_cat'] = pd.cut(df_jobs['work_year_numeric'], bins=bins, labels=labels, right=False, include_lowest=True)
            if not df_jobs['work_year_cat'].empty and df_jobs['work_year_cat'].notna().any():
                actual_categories = df_jobs['work_year_cat'].cat.categories.tolist()
                ordered_categories = [l for l in labels if l in actual_categories]
                if ordered_categories:
                    df_jobs['work_year_cat'] = df_jobs['work_year_cat'].cat.reorder_categories(ordered_categories, ordered=True)
            df_jobs['work_year_cat'] = df_jobs['work_year_cat'].fillna('经验不限') 
        else: 
            df_jobs['work_year_cat'] = pd.Series(['经验不限'] * len(df_jobs), dtype=pd.CategoricalDtype(categories=labels, ordered=True))

    elif 'work_year_cat' in df_jobs.columns and not (pd.api.types.is_categorical_dtype(df_jobs['work_year_cat']) and df_jobs['work_year_cat'].cat.ordered):
        labels = ['经验不限', '1年以内', '1-3年', '3-5年', '5-10年', '10年以上']
        present_categories = [l for l in labels if l in df_jobs['work_year_cat'].unique()]
        if present_categories: df_jobs['work_year_cat'] = pd.Categorical(df_jobs['work_year_cat'], categories=present_categories, ordered=True)
        else: df_jobs['work_year_cat'] = pd.Series(['经验不限'] * len(df_jobs), dtype=pd.CategoricalDtype(categories=labels, ordered=True))
    elif 'work_year_cat' not in df_jobs.columns : 
        labels = ['经验不限', '1年以内', '1-3年', '3-5年', '5-10年', '10年以上']
        df_jobs['work_year_cat'] = pd.Series(['经验不限'] * len(df_jobs), dtype=pd.CategoricalDtype(categories=labels, ordered=True))

    # Ensure other categorical columns are ordered and exist
    for col, order in [
        ('degree_name_cat', ['学历不限', '其他', '初中及以下', '中专', '中技', '中专/中技', '高中', '大专', '本科', '硕士', '博士', '博士后']),
        ('company_scale_cat', ["1-49人", "50-99人", "100-499人", "500-999人", "1000-9999人", "10000+人", "未知"])
    ]:
        if col in df_jobs.columns and df_jobs[col].notna().any():
            present_categories_in_data = df_jobs[col].unique()
            final_order_for_categorical = [cat for cat in order if cat in present_categories_in_data]
            if not final_order_for_categorical: 
                final_order_for_categorical = order 
                
            if not (pd.api.types.is_categorical_dtype(df_jobs[col]) and df_jobs[col].cat.ordered and list(df_jobs[col].cat.categories) == final_order_for_categorical):
                 df_jobs[col] = pd.Categorical(df_jobs[col], categories=final_order_for_categorical, ordered=True)
        elif col in df_jobs.columns and (df_jobs[col].empty or df_jobs[col].isnull().all()):
             df_jobs[col] = pd.Categorical(pd.Series([order[0]]*len(df_jobs) if order else ["未知"]*len(df_jobs)), categories=order, ordered=True)
        elif col not in df_jobs.columns:
            df_jobs[col] = pd.Categorical(pd.Series([order[0]]*len(df_jobs) if order else ["未知"]*len(df_jobs)), categories=order, ordered=True)

    if 'avg_month_pay' in df_jobs.columns:
        df_jobs['avg_month_pay'] = pd.to_numeric(df_jobs['avg_month_pay'], errors='coerce')
    else: df_jobs['avg_month_pay'] = pd.Series(dtype=float)

    if 'head_count' in df_jobs.columns:
        df_jobs['head_count'] = pd.to_numeric(df_jobs['head_count'], errors='coerce')
    else: df_jobs['head_count'] = pd.Series(dtype=float)

    for col_name in ['province_clean', 'city_clean', 'job_catory', 'company_property', 'degree_name', 'company_scale_cleaned', 'job_name', 'company_name']:
        if col_name not in df_jobs.columns:
            df_jobs[col_name] = pd.Series(dtype=str)
    return df_jobs

df_jobs_main = load_and_prep_salary_page_data()

# --- 页面标题和数据更新时间 ---
st.title("💰 薪资深度分析")
if os.path.exists(JOBS_FILE):
    try:
        st.caption(f"数据基于: {os.path.basename(JOBS_FILE)} (最后修改: {datetime.fromtimestamp(os.path.getmtime(JOBS_FILE)).strftime('%Y-%m-%d %H:%M:%S')})")
    except Exception:
        st.caption(f"数据基于: {os.path.basename(JOBS_FILE)} (无法获取最后修改时间)")

# --- 侧边栏过滤器 ---
st.sidebar.header("薪资分析过滤器")
salary_display_df = df_jobs_main.copy()

if not df_jobs_main.empty:
    # --- New Province/City Dependent Filter (Refined) ---
    unique_provinces = ["全国"]
    if 'province_clean' in df_jobs_main.columns and df_jobs_main['province_clean'].notna().any():
        prov_options = sorted([
            p for p in df_jobs_main['province_clean'].dropna().unique() 
            if p not in ['未知省份', '未知地区'] # Filter out unwanted placeholders
        ])
        unique_provinces.extend(prov_options)

    selected_province_salary = st.sidebar.selectbox(
        "选择省份:", unique_provinces, index=0, key="salary_province_filter_v3"
    )

    # Filter DataFrame based on selected_province_salary before populating city options
    temp_df_for_city_filter = df_jobs_main.copy()
    if selected_province_salary != "全国":
        if 'province_clean' in temp_df_for_city_filter.columns:
            temp_df_for_city_filter = temp_df_for_city_filter[temp_df_for_city_filter['province_clean'] == selected_province_salary]

    # City options - Refined to ensure "所有城市 (...)" is first and handles duplicates correctly
    default_city_option_text = "全国" if selected_province_salary == "全国" else selected_province_salary
    city_filter_label_all_cities = f"所有城市 ({default_city_option_text})"
    unique_cities_in_province_options = [city_filter_label_all_cities] # Start with this as the first option

    if 'city_clean' in temp_df_for_city_filter.columns and temp_df_for_city_filter['city_clean'].notna().any():
        city_names_from_data = sorted([
            c for c in temp_df_for_city_filter['city_clean'].dropna().unique()
            if c not in ['未知城市', '未知地区'] # Filter out unwanted placeholders from raw data
        ])
        
        for city_name in city_names_from_data:
            # Add city name if it's not the same as the "all cities" label and not already added
            if city_name != city_filter_label_all_cities and city_name not in unique_cities_in_province_options:
                unique_cities_in_province_options.append(city_name)
    
    selected_city_within_province = st.sidebar.selectbox(
        "选择城市 (该省内):", unique_cities_in_province_options, index=0, key="salary_city_in_province_filter_v3"
    )
    # --- End New Province/City Dependent Filter ---

    unique_categories_salary = ["所有类别"]
    if 'job_catory' in df_jobs_main.columns and df_jobs_main['job_catory'].notna().any():
        cat_options = sorted([jc for jc in df_jobs_main['job_catory'].dropna().unique() if jc and '未知' not in jc])
        unique_categories_salary.extend(cat_options)
    selected_category_salary = st.sidebar.selectbox(
        "选择职位类别:", unique_categories_salary, index=0, key="salary_cat_filter_adv_v3"
    )

    degree_col_for_filter = 'degree_name_cat'
    unique_degrees_salary = ["所有学历"]
    if degree_col_for_filter in df_jobs_main.columns and pd.api.types.is_categorical_dtype(df_jobs_main[degree_col_for_filter]) and not df_jobs_main[degree_col_for_filter].cat.categories.empty:
        unique_degrees_salary.extend(df_jobs_main[degree_col_for_filter].cat.categories.tolist())
    selected_degree_salary = st.sidebar.selectbox(
        "选择学历要求:", unique_degrees_salary, index=0, key="salary_degree_filter_adv_v3"
    )

    scale_col_for_filter = 'company_scale_cat'
    unique_scales_salary = ["所有规模"]
    if scale_col_for_filter in df_jobs_main.columns and pd.api.types.is_categorical_dtype(df_jobs_main[scale_col_for_filter]) and not df_jobs_main[scale_col_for_filter].cat.categories.empty:
        unique_scales_salary.extend(df_jobs_main[scale_col_for_filter].cat.categories.tolist())
    selected_scale_salary = st.sidebar.selectbox(
        "选择公司规模:", unique_scales_salary, index=0, key="salary_scale_filter_adv_v3"
    )

    unique_properties_salary = ["所有性质"]
    if 'company_property' in df_jobs_main.columns and df_jobs_main['company_property'].notna().any():
        prop_options = sorted([cp for cp in df_jobs_main['company_property'].dropna().unique() if cp and '未知' not in cp])
        unique_properties_salary.extend(prop_options)
    selected_property_salary = st.sidebar.selectbox(
        "选择公司性质:", unique_properties_salary, index=0, key="salary_property_filter_adv_v3"
    )

    unique_experience_salary = ["所有经验"]
    if 'work_year_cat' in df_jobs_main.columns and pd.api.types.is_categorical_dtype(df_jobs_main['work_year_cat']) and not df_jobs_main['work_year_cat'].cat.categories.empty:
        unique_experience_salary.extend(df_jobs_main['work_year_cat'].cat.categories.tolist())
    selected_experience_salary = st.sidebar.selectbox(
        "选择经验要求:", unique_experience_salary, index=0, key="salary_exp_filter_adv_v3"
    )

    min_pay_slider, max_pay_slider = 0.0, 100.0 
    valid_salaries_for_slider = pd.Series(dtype=float)
    if 'avg_month_pay' in df_jobs_main.columns and df_jobs_main['avg_month_pay'].notna().any():
        positive_salaries = df_jobs_main[df_jobs_main['avg_month_pay'] > 0]['avg_month_pay']
        if not positive_salaries.empty:
            valid_salaries_for_slider = positive_salaries
            min_pay_slider = float(valid_salaries_for_slider.min())
            max_pay_slider = float(valid_salaries_for_slider.max())
            if min_pay_slider >= max_pay_slider : min_pay_slider = max_pay_slider - 0.1 if max_pay_slider > 0.1 else 0.0

    selected_salary_range = st.sidebar.slider(
        "筛选平均月薪范围 (K):", min_value=min_pay_slider, max_value=max_pay_slider,
        value=(min_pay_slider, max_pay_slider), step=0.5, key="salary_range_filter_adv_v3",
        disabled=(min_pay_slider >= max_pay_slider -0.01 or valid_salaries_for_slider.empty) 
    )

    # --- Apply Filters ---
    if selected_province_salary != "全国":
        if 'province_clean' in salary_display_df.columns:
            salary_display_df = salary_display_df[salary_display_df['province_clean'] == selected_province_salary]

    if not selected_city_within_province.startswith("所有城市"):
        if 'city_clean' in salary_display_df.columns:
            salary_display_df = salary_display_df[salary_display_df['city_clean'] == selected_city_within_province]

    if selected_category_salary != "所有类别" and 'job_catory' in salary_display_df.columns:
        salary_display_df = salary_display_df[salary_display_df['job_catory'] == selected_category_salary]

    if selected_degree_salary != "所有学历" and degree_col_for_filter in salary_display_df.columns:
        salary_display_df = salary_display_df[salary_display_df[degree_col_for_filter] == selected_degree_salary]

    if selected_scale_salary != "所有规模" and scale_col_for_filter in salary_display_df.columns:
        salary_display_df = salary_display_df[salary_display_df[scale_col_for_filter] == selected_scale_salary]

    if selected_property_salary != "所有性质" and 'company_property' in salary_display_df.columns:
        salary_display_df = salary_display_df[salary_display_df['company_property'] == selected_property_salary]

    if selected_experience_salary != "所有经验" and 'work_year_cat' in salary_display_df.columns:
         if pd.api.types.is_categorical_dtype(salary_display_df['work_year_cat']) and \
            not salary_display_df['work_year_cat'].cat.categories.empty and \
            selected_experience_salary in salary_display_df['work_year_cat'].cat.categories:
            salary_display_df = salary_display_df[salary_display_df['work_year_cat'] == selected_experience_salary]

    if 'avg_month_pay' in salary_display_df.columns and salary_display_df['avg_month_pay'].notna().any():
        if not (min_pay_slider >= max_pay_slider -0.01 or valid_salaries_for_slider.empty): 
            salary_display_df = salary_display_df[
                (salary_display_df['avg_month_pay'] >= selected_salary_range[0]) &
                (salary_display_df['avg_month_pay'] <= selected_salary_range[1])
            ]
        salary_display_df = salary_display_df[
            (salary_display_df['avg_month_pay'] > 0) & (salary_display_df['avg_month_pay'].notna())
        ].copy()
    else: 
        salary_display_df = pd.DataFrame(columns=df_jobs_main.columns)
else:
    st.sidebar.warning("岗位数据未加载，无法应用过滤器。")
    salary_display_df = pd.DataFrame(columns=df_jobs_main.columns if not df_jobs_main.empty else None)
    if salary_display_df is None: salary_display_df = pd.DataFrame()

# --- 主内容区 ---
if df_jobs_main.empty:
    st.error("未能加载岗位数据。请运行爬虫以生成数据文件 jobs.json。")
elif salary_display_df.empty:
    st.warning("当前筛选条件下没有匹配的、包含有效薪资信息的岗位数据。请尝试调整过滤器或检查数据源。")
else:
    st.header("薪资洞察 (基于当前筛选)")

    dynamic_region_col_for_dim_option = 'city_clean' 
    if selected_province_salary == "全国" and selected_city_within_province.startswith("所有城市"):
        dynamic_region_col_for_dim_option = 'province_clean'

    dim_options = {
        "地区": dynamic_region_col_for_dim_option,
        "职位类别": "job_catory", "学历": "degree_name_cat",
        "公司规模": "company_scale_cat", "公司性质": "company_property", "经验": "work_year_cat"
    }
    valid_dim_options = {
        k: v for k, v in dim_options.items()
        if v in salary_display_df.columns and salary_display_df[v].notna().any()
    }

    # --- 高阶洞察速览 ---
    st.subheader("🚀 高阶洞察速览")
    insights_cols = st.columns(3)

    job_catory_col_exec = valid_dim_options.get("职位类别")
    if job_catory_col_exec:
        avg_salary_by_cat = salary_display_df.groupby(job_catory_col_exec, observed=True)['avg_month_pay'].agg(['mean', 'count'])
        avg_salary_by_cat_filtered = avg_salary_by_cat[avg_salary_by_cat['count'] >= 10].sort_values(by='mean', ascending=False)
        
        location_context_for_metric = "全国"
        if selected_province_salary != "全国":
            location_context_for_metric = selected_province_salary
            if not selected_city_within_province.startswith("所有城市"):
                location_context_for_metric = selected_city_within_province

        if not avg_salary_by_cat_filtered.empty:
            top_cat = avg_salary_by_cat_filtered.index[0]
            top_cat_sal = avg_salary_by_cat_filtered['mean'].iloc[0]
            insights_cols[0].metric(
                f"最高薪职位类别 ({location_context_for_metric})",
                f"{str(top_cat)[:20]}{'...' if len(str(top_cat))>20 else ''}",
                f"{top_cat_sal:,.1f} K 平均"
            )
        else: insights_cols[0].info(f"在 {location_context_for_metric}，各职位类别样本不足10。")
    else: insights_cols[0].info("职位类别数据不可用。")

    if 'avg_month_pay' in salary_display_df.columns and len(salary_display_df['avg_month_pay']) >= 20:
        p25 = salary_display_df['avg_month_pay'].quantile(0.25)
        p75 = salary_display_df['avg_month_pay'].quantile(0.75)
        insights_cols[1].metric("主流薪资范围 (25%-75%)", f"{p25:,.1f} K - {p75:,.1f} K")
    else: insights_cols[1].info("样本不足20，无法计算主流薪资范围。")

    city_col_for_combo = 'city_clean' 
    if city_col_for_combo in salary_display_df.columns and job_catory_col_exec:
        combo_salary_df = salary_display_df.dropna(subset=[city_col_for_combo, job_catory_col_exec, 'avg_month_pay'])
        if not combo_salary_df.empty:
            top_combos = combo_salary_df.groupby([city_col_for_combo, job_catory_col_exec], observed=True)['avg_month_pay'].agg(['median', 'count'])
            top_combos_filtered = top_combos[top_combos['count'] >= 5].sort_values(by='median', ascending=False).head(1)
            if not top_combos_filtered.empty:
                top_combo_city, top_combo_cat = top_combos_filtered.index[0]
                top_combo_median_sal = top_combos_filtered['median'].iloc[0]
                insights_cols[2].metric(f"高薪组合: {str(top_combo_city)[:10]}-{str(top_combo_cat)[:10]}",
                                        f"{top_combo_median_sal:,.1f} K 中位数", help="基于当前筛选, 组合至少5个样本")
            else: insights_cols[2].info("当前筛选下，无城市/类别组合满足分析条件 (各需至少5样本)。")
        else: insights_cols[2].info("数据不足以分析城市/类别组合薪资。")
    else: insights_cols[2].info("地区或职位类别数据不足 (无法进行高薪组合分析)。")

    st.divider()

    tab_dist_relation, tab_compare, tab_top_combos = st.tabs([
        "📊 薪酬分布与关系", "🆚 多维薪酬对比", "🏆 高薪领域组合"
    ])

    with tab_dist_relation:
        st.subheader("整体平均月薪分布与百分位数")
        dist_col1, dist_col2 = st.columns([2,1])
        with dist_col1:
            if 'avg_month_pay' in salary_display_df.columns and not salary_display_df['avg_month_pay'].empty :
                dynamic_nbins = max(10, min(50, len(salary_display_df['avg_month_pay'])//50 if len(salary_display_df['avg_month_pay']) > 50 else 10))
                fig_hist = px.histogram(salary_display_df, x="avg_month_pay", nbins=dynamic_nbins,
                                        title="平均月薪分布 (K/月)", labels={'avg_month_pay': '平均月薪 (K)'},
                                        marginal="box", opacity=0.8)
                st.plotly_chart(fig_hist, use_container_width=True)
            else: st.info("无足够薪资数据显示整体薪资分布。")
        with dist_col2:
            st.markdown("##### 薪资百分位数")
            if 'avg_month_pay' in salary_display_df.columns and len(salary_display_df['avg_month_pay']) >= 20: 
                percentiles = salary_display_df['avg_month_pay'].quantile([0.1, 0.25, 0.5, 0.75, 0.9, 0.95]).round(1)
                percentile_df = percentiles.reset_index()
                percentile_df.columns = ['百分位点', '月薪 (K)']
                percentile_df['百分位点'] = (percentile_df['百分位点'] * 100).astype(int).astype(str) + '%'
                st.dataframe(percentile_df, hide_index=True)
            else: st.info("数据不足 (少于20条有效薪资)。")

        st.divider()
        st.subheader("薪资与其他因素关系")
        relation_col1, relation_col2 = st.columns(2)
        with relation_col1:
            st.markdown("##### 平均月薪 vs. 招聘人数")
            if 'head_count' in salary_display_df.columns and salary_display_df['head_count'].notna().any() and \
               'avg_month_pay' in salary_display_df.columns and salary_display_df['avg_month_pay'].notna().any():
                scatter_df_hc = salary_display_df.dropna(subset=['head_count', 'avg_month_pay']).copy()
                if not scatter_df_hc.empty:
                    hc_color_display_names = ["无"] + [k for k, v_col in valid_dim_options.items() if v_col in ['city_clean', 'job_catory', 'degree_name_cat', 'province_clean']]
                    selected_hc_color_key = st.selectbox("颜色区分(招聘图):", hc_color_display_names, key="scatter_hc_color_v4_salary")
                    color_scatter_hc = valid_dim_options.get(selected_hc_color_key) if selected_hc_color_key != "无" else None

                    hover_data_scatter = {'avg_month_pay':':.1f K', 'head_count': True}
                    if "job_name" in scatter_df_hc.columns: hover_data_scatter['job_name'] = True
                    if "company_name" in scatter_df_hc.columns: hover_data_scatter['company_name'] = True
                    if dynamic_region_col_for_dim_option in scatter_df_hc.columns: hover_data_scatter[dynamic_region_col_for_dim_option] = True
                    
                    fig_scatter_hc = px.scatter(
                        scatter_df_hc, x="avg_month_pay", y="head_count",
                        color=color_scatter_hc if color_scatter_hc and color_scatter_hc in scatter_df_hc.columns else None,
                        size="avg_month_pay", size_max=15,
                        hover_name="job_name" if "job_name" in scatter_df_hc else None,
                        hover_data=hover_data_scatter,
                        title="平均月薪 vs. 招聘人数",
                        labels={'avg_month_pay': '平均月薪 (K)', 'head_count': '招聘人数 (对数轴)'},
                        log_y=True, opacity=0.7
                    )
                    st.plotly_chart(fig_scatter_hc, use_container_width=True)
                else: st.info("筛选后无足够数据绘制招聘人数散点图。")
            else: st.info("缺少招聘人数 (`head_count`)或薪资数据。")
        
        with relation_col2:
            st.markdown("##### 平均月薪 vs. 公司规模")
            scale_col = valid_dim_options.get("公司规模") 
            if scale_col and scale_col in salary_display_df.columns and pd.api.types.is_categorical_dtype(salary_display_df[scale_col]) and salary_display_df[scale_col].cat.ordered:
                plot_df_scale = salary_display_df.dropna(subset=[scale_col, 'avg_month_pay'])
                if not plot_df_scale.empty and not plot_df_scale[scale_col].cat.categories.empty:
                    scale_cat_order = salary_display_df[scale_col].cat.categories.tolist() 
                    plot_df_scale = plot_df_scale[plot_df_scale[scale_col].isin(scale_cat_order)]

                    if not plot_df_scale.empty :
                        fig_scale = px.box(plot_df_scale, x=scale_col, y="avg_month_pay", color=scale_col,
                                        title="不同公司规模的薪资分布",
                                        labels={scale_col: "公司规模", 'avg_month_pay': '平均月薪 (K)'},
                                        category_orders={scale_col: scale_cat_order})
                        fig_scale.update_layout(showlegend=False)
                        st.plotly_chart(fig_scale, use_container_width=True)
                    else:
                        st.info("公司规模数据在有效类别内为空。")
                else:
                    st.info("公司规模数据不足或类别为空。")
            else:
                st.info("公司规模数据 (company_scale_cat, 有序分类) 不可用或格式不正确。")

    with tab_compare:
        st.subheader("单维度与交叉维度薪资对比")
        
        valid_dim_keys_for_compare = list(valid_dim_options.keys())

        if not valid_dim_keys_for_compare:
            st.info("无足够维度数据进行对比分析。")
        else:
            st.markdown("#### 单维度薪资分布")
            selected_dim_key_single = st.selectbox("选择分析维度:", valid_dim_keys_for_compare, key="compare_single_dim_v5_salary")
            selected_dim_col_single = valid_dim_options[selected_dim_key_single]

            plot_type_single = st.radio("图表类型:", ["箱线图", "小提琴图"], key="compare_single_plot_type_v5_salary", horizontal=True)
            min_samples_single = st.slider("每类最小样本(单维度):", 1, 30, 5, key="compare_single_min_samples_v5_salary")

            temp_df_single = salary_display_df.dropna(subset=[selected_dim_col_single, 'avg_month_pay'])
            if not temp_df_single.empty:
                category_counts_single = temp_df_single[selected_dim_col_single].value_counts()
                valid_cats_single = category_counts_single[category_counts_single >= min_samples_single].index
                plot_df_single = temp_df_single[temp_df_single[selected_dim_col_single].isin(valid_cats_single)]
            else:
                plot_df_single = pd.DataFrame()

            final_cat_order_single = None
            if not plot_df_single.empty and pd.api.types.is_categorical_dtype(plot_df_single[selected_dim_col_single]) and plot_df_single[selected_dim_col_single].cat.ordered:
                ordered_valid_cats = [cat for cat in plot_df_single[selected_dim_col_single].cat.categories if cat in valid_cats_single]
                if ordered_valid_cats:
                    plot_df_single = plot_df_single[plot_df_single[selected_dim_col_single].isin(ordered_valid_cats)] # Ensure correct filtering
                    final_cat_order_single = {selected_dim_col_single: ordered_valid_cats} # Use these for ordering
            elif not plot_df_single.empty: 
                top_n_display_limit = 15 
                cats_to_display = valid_cats_single[:top_n_display_limit]
                plot_df_single = plot_df_single[plot_df_single[selected_dim_col_single].isin(cats_to_display)]

            if not plot_df_single.empty:
                fig_args_single = {
                    "data_frame": plot_df_single, "x": selected_dim_col_single, "y": "avg_month_pay",
                    "color": selected_dim_col_single, "title": f"{selected_dim_key_single}维度薪资",
                    "labels": {selected_dim_col_single: selected_dim_key_single, 'avg_month_pay': '平均月薪(K)'}
                }
                if final_cat_order_single: 
                    fig_args_single["category_orders"] = final_cat_order_single
                elif selected_dim_key_single == "地区" and selected_dim_col_single in plot_df_single.columns: # Sort non-ordered regions by median salary
                    median_sal_order = plot_df_single.groupby(selected_dim_col_single, observed=True)['avg_month_pay'].median().sort_values().index.tolist()
                    fig_args_single["category_orders"] = {selected_dim_col_single: median_sal_order}

                fig_single = px.box(**fig_args_single) if plot_type_single == "箱线图" else px.violin(**fig_args_single, box=True, points=False)
                fig_single.update_layout(showlegend=False)
                st.plotly_chart(fig_single, use_container_width=True)
            else: st.info(f"数据不足以按 {selected_dim_key_single} 分析 (最小样本: {min_samples_single})。")

            st.markdown("---")
            st.markdown("#### 交叉维度薪资热力图 (中位数薪资)")
            heatmap_cols = st.columns([1,1,1,1])
            dim1_key = heatmap_cols[0].selectbox("行维度:", valid_dim_keys_for_compare, key="compare_cross_dim1_v5_salary", index = 0)
            dim1_top_n = heatmap_cols[1].slider("行Top N:", 3, 20, 7, key="heatmap_dim1_top_n_v5_salary")

            available_for_dim2 = [k for k in valid_dim_keys_for_compare if k != dim1_key]
            if not available_for_dim2: 
                st.info("交叉分析需要至少两个不同的可用维度。")
                dim2_key = None
            else:
                dim2_key = heatmap_cols[2].selectbox("列维度:", available_for_dim2, key="compare_cross_dim2_v5_salary", index=0)
                dim2_top_n = heatmap_cols[3].slider("列Top N:", 3, 15, 5, key="heatmap_dim2_top_n_v5_salary")

            if dim1_key and dim2_key and dim1_key != dim2_key:
                dim1_col = valid_dim_options[dim1_key] 
                dim2_col = valid_dim_options[dim2_key]

                heatmap_df_base = salary_display_df.dropna(subset=[dim1_col, dim2_col, 'avg_month_pay'])
                if not heatmap_df_base.empty:
                    top_dim1_cats_series = heatmap_df_base[dim1_col].value_counts().nlargest(dim1_top_n)
                    top_dim1_cats_list = top_dim1_cats_series.index.tolist()
                    top_dim2_cats_series = heatmap_df_base[dim2_col].value_counts().nlargest(dim2_top_n)
                    top_dim2_cats_list = top_dim2_cats_series.index.tolist()

                    heatmap_df_filtered = heatmap_df_base[
                        heatmap_df_base[dim1_col].isin(top_dim1_cats_list) &
                        heatmap_df_base[dim2_col].isin(top_dim2_cats_list)
                    ]
                    min_samples_heatmap_cell = st.slider("热力图每单元格最小样本:", 1, 10, 3, key="heatmap_min_samples_cell_detail_v5_salary")

                    if not heatmap_df_filtered.empty:
                        grouped_for_heatmap = heatmap_df_filtered.groupby([dim1_col, dim2_col], observed=True)['avg_month_pay']
                        cell_counts = grouped_for_heatmap.count()
                        median_salaries = grouped_for_heatmap.median()
                        median_salaries_final = median_salaries[cell_counts >= min_samples_heatmap_cell]

                        if not median_salaries_final.empty:
                            pivot_table = median_salaries_final.unstack(level=dim2_col)
                            
                            final_dim1_order_heatmap = top_dim1_cats_list
                            if pd.api.types.is_categorical_dtype(heatmap_df_base[dim1_col]) and heatmap_df_base[dim1_col].cat.ordered:
                                final_dim1_order_heatmap = [cat for cat in heatmap_df_base[dim1_col].cat.categories if cat in top_dim1_cats_list and cat in pivot_table.index]
                            final_dim2_order_heatmap = top_dim2_cats_list
                            if pd.api.types.is_categorical_dtype(heatmap_df_base[dim2_col]) and heatmap_df_base[dim2_col].cat.ordered:
                                 final_dim2_order_heatmap = [cat for cat in heatmap_df_base[dim2_col].cat.categories if cat in top_dim2_cats_list and cat in pivot_table.columns]
                            
                            if final_dim1_order_heatmap and any(item in pivot_table.index for item in final_dim1_order_heatmap):
                                pivot_table = pivot_table.reindex(index=[idx for idx in final_dim1_order_heatmap if idx in pivot_table.index])
                            if final_dim2_order_heatmap and any(item in pivot_table.columns for item in final_dim2_order_heatmap):
                                pivot_table = pivot_table.reindex(columns=[col for col in final_dim2_order_heatmap if col in pivot_table.columns])
                            
                            pivot_table.dropna(axis=0, how='all', inplace=True)
                            pivot_table.dropna(axis=1, how='all', inplace=True)

                            if not pivot_table.empty:
                                fig_heatmap = px.imshow(pivot_table, text_auto=".1f", aspect="auto", color_continuous_scale="viridis",
                                                        labels=dict(x=dim2_key, y=dim1_key, color="中位数月薪(K)"),
                                                        title=f"Top {len(pivot_table.index)} {dim1_key} vs Top {len(pivot_table.columns)} {dim2_key} (中位数薪资)")
                                st.plotly_chart(fig_heatmap, use_container_width=True)
                            else: st.info("交叉维度聚合后无足够数据或所有单元格值为空。")
                        else: st.info(f"无交叉维度数据满足单元格最小样本数 ({min_samples_heatmap_cell})。")
                    else: st.info("选择的Top N类别组合后数据为空。")
                else: st.info("用于热力图的基础数据为空。")
            elif dim1_key and dim2_key and dim1_key == dim2_key:
                 st.warning("请为交叉分析选择两个不同的维度。")

    with tab_top_combos:
        st.subheader("高薪领域组合分析 (Top N)")
        st.write("探索不同维度组合下的高薪领域。下图展示了基于所选维度组合的Top N平均/中位数薪资最高的具体类别。")

        combo_dim_keys = []
        for k, v_col_name in dim_options.items(): 
            if v_col_name in ['city_clean', 'province_clean', 'job_catory', 'degree_name_cat', 'company_scale_cat', 'work_year_cat'] and \
               v_col_name in salary_display_df.columns and salary_display_df[v_col_name].notna().any():
                combo_dim_keys.append(k)

        if len(combo_dim_keys) >= 2:
            tc_col1, tc_col2, tc_col3, tc_col4 = st.columns(4)
            combo_dim1_key = tc_col1.selectbox("选择组合维度1:", combo_dim_keys, index=0, key="top_combo_dim1_v3_salary")

            remaining_dims_for_tc2 = [k for k in combo_dim_keys if k != combo_dim1_key]
            if not remaining_dims_for_tc2:
                st.info("高薪组合分析至少需要两个不同维度。") # Should not happen if len(combo_dim_keys) >=2 initially
                combo_dim2_key = None
            else:
                combo_dim2_key = tc_col2.selectbox("选择组合维度2:", remaining_dims_for_tc2, index=0, key="top_combo_dim2_v3_salary")

            if combo_dim1_key and combo_dim2_key : 
                combo_metric = tc_col3.selectbox("排序指标:", ["中位数薪资", "平均薪资"], key="top_combo_metric_v3_salary")
                top_n_combos = tc_col4.slider("显示Top N组合:", 5, 25, 10, key="top_n_combos_slider_v3_salary")
                min_jobs_per_combo = st.slider("每个组合的最小岗位数:", 1, 20, 5, key="top_combo_min_jobs_v3_salary")

                combo_dim1_col = valid_dim_options[combo_dim1_key] 
                combo_dim2_col = valid_dim_options[combo_dim2_key]

                combos_df = salary_display_df.dropna(subset=[combo_dim1_col, combo_dim2_col, 'avg_month_pay'])
                if not combos_df.empty:
                    grouped_combos = combos_df.groupby([combo_dim1_col, combo_dim2_col], observed=True)['avg_month_pay'].agg(['median', 'mean', 'count'])
                    grouped_combos.columns = ['median_salary', 'average_salary', 'job_count']
                    grouped_combos = grouped_combos[grouped_combos['job_count'] >= min_jobs_per_combo].reset_index()

                    sort_col = 'median_salary' if combo_metric == "中位数薪资" else 'average_salary'
                    top_paying_combos = grouped_combos.sort_values(by=sort_col, ascending=False).head(top_n_combos)

                    if not top_paying_combos.empty:
                        top_paying_combos['combination_label'] = top_paying_combos[combo_dim1_col].astype(str) + " - " + \
                                                                 top_paying_combos[combo_dim2_col].astype(str)
                        max_label_len = 45 
                        top_paying_combos['combination_label'] = top_paying_combos['combination_label'].apply(
                            lambda x: x[:max_label_len] + '...' if len(x) > max_label_len else x
                        )

                        fig_top_combos = px.bar(
                            top_paying_combos, x=sort_col, y='combination_label', color='job_count',
                            color_continuous_scale=px.colors.sequential.Viridis, orientation='h',
                            title=f"Top {len(top_paying_combos)} 高薪组合 ({combo_dim1_key} & {combo_dim2_key})",
                            labels={sort_col: f"{combo_metric} (K)", 'combination_label': "维度组合", 'job_count': "岗位数"},
                            text=sort_col
                        )
                        fig_top_combos.update_traces(texttemplate='%{text:,.1f} K', textposition='outside')
                        fig_top_combos.update_layout(yaxis={'categoryorder':'total ascending'})
                        st.plotly_chart(fig_top_combos, use_container_width=True)

                        with st.expander("查看Top N组合数据表"):
                            display_cols_table = ['combination_label', 'median_salary', 'average_salary', 'job_count']
                            st.dataframe(top_paying_combos[display_cols_table].style.format({
                                'median_salary': '{:,.1f}', 'average_salary': '{:,.1f}', 'job_count': '{:,}'
                            }), hide_index=True, use_container_width=True)
                    else:
                        st.info(f"当前筛选及设置下，没有足够的组合数据 (每个组合至少 {min_jobs_per_combo} 岗位) 来生成Top N高薪组合图。")
                else:
                    st.info("数据不足以分析高薪组合。")
        else:
            st.info("高薪组合分析至少需要两个可用的维度。")