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
    get_top_n_counts, get_time_series_data, calculate_time_deltas, get_job_freshness_distribution,
    plot_bar_chart, plot_pie_chart, plot_line_chart
)
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, timezone

# Ensure page_config is called only once
if 'page_config_called_demand_analysis' not in st.session_state:
    st.set_page_config(page_title="市场需求分析", layout="wide", page_icon="📈")
    st.session_state.page_config_called_demand_analysis = True

# --- Constants for "Other" labels to exclude/handle ---
EXCLUDE_OTHER_LABELS_LOWER = ['其他类别', '其他相关学历', '未知', '不限', 'nan', 'none', 'null', 'other', 'others', '学历不限','']
DEFAULT_OTHER_GROUP_LABEL = "其它明确类别"
SPECIFIC_DEGREES_TO_TRACK = ["大专", "本科", "硕士", "博士", "博士后"]
DEGREE_BROAD_CATEGORIES = ['本科及以上', '硕士及以上', '学历不限', '不限']
IMPORTANT_DEGREES = SPECIFIC_DEGREES_TO_TRACK + DEGREE_BROAD_CATEGORIES

# --- 加载和预处理数据 ---
@st.cache_data(ttl=3600)
def load_and_prep_demand_data():
    df_jobs_raw = load_json_data(JOBS_FILE)
    df_jobs_interim = preprocess_jobs_data(df_jobs_raw) # Ensures province_clean and city_clean
    df_jobs_final = calculate_time_deltas(df_jobs_interim) if not df_jobs_interim.empty else df_jobs_interim
    
    # Ensure province_clean and city_clean exist, even if empty, to prevent KeyErrors later
    if 'province_clean' not in df_jobs_final.columns:
        df_jobs_final['province_clean'] = pd.Series(dtype=str)
    if 'city_clean' not in df_jobs_final.columns:
        df_jobs_final['city_clean'] = pd.Series(dtype=str)
        
    return df_jobs_final

df_jobs_main = load_and_prep_demand_data()

# --- 页面标题和数据更新时间 ---
st.title("📈 市场需求分析")
if os.path.exists(JOBS_FILE):
    try:
        st.caption(f"数据源: `{os.path.basename(JOBS_FILE)}` (最后修改: {datetime.fromtimestamp(os.path.getmtime(JOBS_FILE)).strftime('%Y-%m-%d %H:%M:%S')})")
    except Exception:
        st.caption(f"数据源: `{os.path.basename(JOBS_FILE)}` (无法获取最后修改时间)")

# --- 侧边栏过滤器 ---
st.sidebar.header("需求分析过滤器")
demand_display_df = pd.DataFrame()
default_start_date, min_date_obj_sidebar, max_date_obj_sidebar = None, None, None


if not df_jobs_main.empty:
    # --- Province/City Dependent Filter for Demand Page ---
    unique_provinces_demand = ["全国"]
    if 'province_clean' in df_jobs_main.columns and df_jobs_main['province_clean'].notna().any():
        prov_options_demand = sorted([
            p for p in df_jobs_main['province_clean'].dropna().unique()
            if p.lower().strip() not in EXCLUDE_OTHER_LABELS_LOWER and p.strip() != ''
        ])
        unique_provinces_demand.extend(prov_options_demand)

    selected_province_demand = st.sidebar.selectbox(
        "选择省份:", unique_provinces_demand, index=0, key="demand_province_filter_v1"
    )

    temp_df_for_city_filter_demand = df_jobs_main.copy()
    if selected_province_demand != "全国":
        if 'province_clean' in temp_df_for_city_filter_demand.columns:
            temp_df_for_city_filter_demand = temp_df_for_city_filter_demand[
                temp_df_for_city_filter_demand['province_clean'] == selected_province_demand
            ]

    default_city_option_text_demand = "全国" if selected_province_demand == "全国" else selected_province_demand
    city_filter_label_all_cities_demand = f"所有城市 ({default_city_option_text_demand})"
    unique_cities_in_province_options_demand = [city_filter_label_all_cities_demand]

    if 'city_clean' in temp_df_for_city_filter_demand.columns and temp_df_for_city_filter_demand['city_clean'].notna().any():
        city_names_from_data_demand = sorted([
            c for c in temp_df_for_city_filter_demand['city_clean'].dropna().unique()
            if c.lower().strip() not in EXCLUDE_OTHER_LABELS_LOWER and c.strip() != ''
        ])
        for city_name in city_names_from_data_demand:
            if city_name != city_filter_label_all_cities_demand and city_name not in unique_cities_in_province_options_demand:
                unique_cities_in_province_options_demand.append(city_name)
    
    selected_city_demand = st.sidebar.selectbox(
        "选择城市 (该省内):", unique_cities_in_province_options_demand, index=0, key="demand_city_in_province_filter_v1"
    )
    # --- End Province/City Dependent Filter ---

    # Category Filter (remains largely the same, uses a helper for options)
    def get_meaningful_filter_options(df, column, default_prefix="所有"):
        options = [default_prefix]
        if column in df.columns and df[column].notna().any():
            unique_vals = df[column].dropna().astype(str).unique()
            meaningful_vals = sorted([
                val for val in unique_vals if val.lower().strip() not in EXCLUDE_OTHER_LABELS_LOWER and val.strip() != ''
            ])
            options.extend(meaningful_vals)
        return options
        
    category_options_demand = get_meaningful_filter_options(df_jobs_main, 'job_catory', "所有类别")
    selected_category_demand_filter = st.sidebar.selectbox( # Renamed to avoid conflict if selected_category_demand is used elsewhere
        "选择职位类别:", category_options_demand, index=0, key="demand_cat_filter_v7"
    )
    
    # Date Filter
    if 'publish_date_dt' in df_jobs_main.columns and not df_jobs_main['publish_date_dt'].dropna().empty:
        min_date_ts = df_jobs_main['publish_date_dt'].min()
        max_date_ts = df_jobs_main['publish_date_dt'].max()
        if pd.notna(min_date_ts) and pd.notna(max_date_ts):
             min_date_obj_sidebar = min_date_ts.date()
             max_date_obj_sidebar = max_date_ts.date()

    if min_date_obj_sidebar and max_date_obj_sidebar and min_date_obj_sidebar <= max_date_obj_sidebar:
        default_start_date = max(min_date_obj_sidebar, max_date_obj_sidebar - timedelta(days=365)) if max_date_obj_sidebar else min_date_obj_sidebar
        selected_date_range_demand = st.sidebar.date_input(
            "选择岗位发布日期范围:", 
            value=(default_start_date, max_date_obj_sidebar),
            min_value=min_date_obj_sidebar,
            max_value=max_date_obj_sidebar,
            key="demand_date_range_filter_v7"
        )
    else:
        selected_date_range_demand = None
        st.sidebar.text("日期数据不足以进行范围筛选。")

    # Apply Filters
    demand_display_df = df_jobs_main.copy()

    if selected_province_demand != "全国":
        if 'province_clean' in demand_display_df.columns:
            demand_display_df = demand_display_df[demand_display_df['province_clean'] == selected_province_demand]

    if not selected_city_demand.startswith("所有城市"): # e.g. "所有城市 (北京)" vs "北京"
        actual_city_name = selected_city_demand # This is the direct city name
        if 'city_clean' in demand_display_df.columns:
            demand_display_df = demand_display_df[demand_display_df['city_clean'] == actual_city_name]
    
    if selected_category_demand_filter != category_options_demand[0] and 'job_catory' in demand_display_df.columns:
        demand_display_df = demand_display_df[demand_display_df['job_catory'] == selected_category_demand_filter]
    
    if selected_date_range_demand and len(selected_date_range_demand) == 2 and 'publish_date_dt' in demand_display_df.columns:
        try:
            start_date_input = pd.to_datetime(selected_date_range_demand[0])
            end_date_input = pd.to_datetime(selected_date_range_demand[1])
            
            # Ensure correct timezone handling if publish_date_dt is timezone-aware
            if demand_display_df['publish_date_dt'].dt.tz is not None:
                tz_info = demand_display_df['publish_date_dt'].dt.tz
                start_date_aware = start_date_input.tz_localize(tz_info) if start_date_input.tzinfo is None else start_date_input.tz_convert(tz_info)
                end_date_aware = (end_date_input + pd.Timedelta(days=1)).tz_localize(tz_info) if end_date_input.tzinfo is None else (end_date_input + pd.Timedelta(days=1)).tz_convert(tz_info)
            else: # If publish_date_dt is naive, compare with naive
                start_date_aware = start_date_input
                end_date_aware = end_date_input + pd.Timedelta(days=1) # End date is exclusive

            demand_display_df = demand_display_df[
                (demand_display_df['publish_date_dt'] >= start_date_aware) &
                (demand_display_df['publish_date_dt'] < end_date_aware)
            ]
        except Exception as e_date_filter:
            st.sidebar.error(f"日期筛选错误: {e_date_filter}")
else:
    st.sidebar.warning("岗位数据未加载，无法应用过滤器。")
    demand_display_df = pd.DataFrame(columns=df_jobs_main.columns if not df_jobs_main.empty else None)
    if demand_display_df is None: demand_display_df = pd.DataFrame()


# --- 主内容区 ---
# Determine filter status for the warning message
filters_applied = False
if 'selected_province_demand' in locals(): # Check if filters have been initialized
    is_province_default = (selected_province_demand == "全国")
    is_city_default = (selected_city_demand.startswith("所有城市") if 'selected_city_demand' in locals() else True)
    is_category_default = (selected_category_demand_filter == (category_options_demand[0] if 'category_options_demand' in locals() and category_options_demand else "所有类别"))
    
    is_date_default = True
    if selected_date_range_demand and min_date_obj_sidebar and max_date_obj_sidebar and default_start_date:
        is_date_default = (selected_date_range_demand[0] == default_start_date and selected_date_range_demand[1] == max_date_obj_sidebar)
    
    if not (is_province_default and is_city_default and is_category_default and is_date_default):
        filters_applied = True


if df_jobs_main.empty:
    st.error("未能加载岗位数据。")
elif demand_display_df.empty and filters_applied:
    st.warning("当前筛选条件下没有匹配的岗位数据。请尝试调整过滤器。")
elif demand_display_df.empty and not filters_applied and not df_jobs_main.empty:
    st.info("数据已加载，但总体数据量可能较少或所有数据均不含有效信息。")

else:
    st.header("需求概览 (基于当前筛选)")
    if not demand_display_df.empty:
        st.metric("符合条件的岗位数量", f"{len(demand_display_df):,}")
    st.divider()

    lookback_options = {"近3个月": 90, "近6个月": 180, "近1年": 365, "近2年": 730, "所有时间": None}

    # --- Helper Function for Refining Degree Counts (remains unchanged) ---
    def get_refined_degree_counts(degree_series,
                                  top_n_specific=4,
                                  important_degrees_to_show=IMPORTANT_DEGREES,
                                  other_label="其它具体学历",
                                  exclude_generic_lower=EXCLUDE_OTHER_LABELS_LOWER,
                                  min_count_threshold=1):
        if degree_series.empty:
            return pd.DataFrame(columns=['degree_name_cat', 'count'])

        temp_degree_series_str = degree_series.astype(str).fillna("未知").str.strip()
        temp_degree_series_str.replace('nan', '未知', inplace=True)
        counts = temp_degree_series_str.value_counts()
        
        broad_counts_dict = {}
        specific_counts_dict = {}

        for degree, count_val in counts.items():
            degree_s = str(degree).strip()
            degree_lower = degree_s.lower()
            is_broad = False
            for broad_cat_orig in DEGREE_BROAD_CATEGORIES:
                if broad_cat_orig.lower() == degree_lower:
                    broad_counts_dict[broad_cat_orig] = broad_counts_dict.get(broad_cat_orig, 0) + int(count_val)
                    is_broad = True
                    break
            if not is_broad and degree_lower not in exclude_generic_lower and degree_s:
                is_specific_tracked = False
                for specific_tracked_orig in SPECIFIC_DEGREES_TO_TRACK:
                    if specific_tracked_orig.lower() == degree_lower:
                        specific_counts_dict[specific_tracked_orig] = specific_counts_dict.get(specific_tracked_orig, 0) + int(count_val)
                        is_specific_tracked = True
                        break
                if not is_specific_tracked:
                     specific_counts_dict[degree_s] = specific_counts_dict.get(degree_s, 0) + int(count_val)
        if not specific_counts_dict: specific_counts_series = pd.Series(dtype='int64')
        else: specific_counts_series = pd.Series(specific_counts_dict, dtype='int64').sort_values(ascending=False)
        explicitly_tracked_specific_counts = pd.Series({k: v for k, v in specific_counts_series.items() if k in SPECIFIC_DEGREES_TO_TRACK}, dtype='int64')
        other_specific_for_nlargest = specific_counts_series[~specific_counts_series.index.isin(SPECIFIC_DEGREES_TO_TRACK)]
        top_other_specific = other_specific_for_nlargest.nlargest(top_n_specific - len(explicitly_tracked_specific_counts))
        top_specific_combined = pd.concat([explicitly_tracked_specific_counts, top_other_specific]).drop_duplicates()
        other_specific_sum = specific_counts_series[~specific_counts_series.index.isin(top_specific_combined.index)].sum()
        final_counts_list = []
        for degree, count_val in top_specific_combined.items():
            if count_val >= min_count_threshold: final_counts_list.append({'degree_name_cat': degree, 'count': int(count_val)})
        for degree, count_val in broad_counts_dict.items():
            if count_val > 0 and count_val >= min_count_threshold: final_counts_list.append({'degree_name_cat': degree, 'count': int(count_val)})
        if other_specific_sum > 0 and other_label.lower() not in exclude_generic_lower:
            final_counts_list.append({'degree_name_cat': other_label, 'count': int(other_specific_sum)})
        result_df = pd.DataFrame(final_counts_list)
        if not result_df.empty:
            result_df['count'] = pd.to_numeric(result_df['count'], errors='coerce').fillna(0)
            result_df = result_df[result_df['count'] > 0]
            if 'degree_name_cat' in df_jobs_main.columns and isinstance(df_jobs_main['degree_name_cat'].dtype, pd.CategoricalDtype) and not result_df.empty and 'degree_name_cat' in result_df.columns:
                all_original_cats = df_jobs_main['degree_name_cat'].cat.categories.tolist()
                if other_specific_sum > 0 and other_label not in all_original_cats and other_label.lower() not in exclude_generic_lower: all_original_cats.append(other_label)
                present_cats_for_ordering = [cat for cat in all_original_cats if cat in result_df['degree_name_cat'].unique()]
                if present_cats_for_ordering:
                    try:
                        result_df['degree_name_cat'] = pd.Categorical(result_df['degree_name_cat'], categories=present_cats_for_ordering, ordered=True)
                        result_df = result_df.sort_values('degree_name_cat')
                    except Exception as e_cat_sort: result_df = result_df.sort_values('count', ascending=False)
                else: result_df = result_df.sort_values('count', ascending=False)
            else: result_df = result_df.sort_values('count', ascending=False)
            return result_df
        return pd.DataFrame(columns=['degree_name_cat', 'count'])
    # --- End Helper ---

    tab_dist, tab_trends, tab_edu_trends = st.tabs(["📊 各维度需求分布", "🚀 市场动态与职位热度", "🎓 学历需求变化"])

    with tab_dist:
        st.subheader("各维度需求分布")
        col_dist1, col_dist2 = st.columns(2)
        
        # prep_dist_data remains the same
        def prep_dist_data(df, column_name, top_n=10, other_label=DEFAULT_OTHER_GROUP_LABEL, min_threshold_pct=0.005, min_threshold_abs=5):
            if column_name not in df.columns or df[column_name].dropna().empty:
                return pd.DataFrame(columns=[column_name, 'count'])
            temp_series = df[column_name].astype(str).fillna("未知").str.strip()
            temp_series.replace('nan', '未知', inplace=True)
            counts = temp_series.value_counts()
            meaningful_counts = counts[~counts.index.astype(str).str.lower().isin(EXCLUDE_OTHER_LABELS_LOWER)]
            if meaningful_counts.empty: return pd.DataFrame(columns=[column_name, 'count'])
            threshold = max(min_threshold_abs, len(df) * min_threshold_pct) if not df.empty else min_threshold_abs
            top_items = meaningful_counts[meaningful_counts.astype(float) >= threshold]
            other_sum = meaningful_counts[meaningful_counts.astype(float) < threshold].sum()
            df_list = [{'item': idx, 'count': val} for idx, val in top_items.items()]
            if other_sum > 0 and other_label.lower() not in EXCLUDE_OTHER_LABELS_LOWER:
                df_list.append({'item': other_label, 'count': other_sum})
            result_df = pd.DataFrame(df_list)
            if not result_df.empty:
                 result_df.rename(columns={'item': column_name}, inplace=True)
                 result_df['count'] = pd.to_numeric(result_df['count'])
                 result_df = result_df.sort_values('count', ascending=False)
            return result_df.head(top_n + (1 if other_sum > 0 and other_label.lower() not in EXCLUDE_OTHER_LABELS_LOWER else 0))

        with col_dist1:
            # Determine if we should show province ranking or city ranking (or info message)
            show_province_ranking = (selected_province_demand == "全国" and selected_city_demand.startswith("所有城市"))
            show_city_ranking_within_province = (selected_province_demand != "全国" and selected_city_demand.startswith("所有城市"))

            if show_province_ranking:
                if 'province_clean' in demand_display_df.columns and demand_display_df['province_clean'].notna().any():
                    province_series = demand_display_df['province_clean'].astype(str).fillna("未知").str.strip()
                    valid_province_series = province_series[~province_series.str.lower().isin(EXCLUDE_OTHER_LABELS_LOWER)]
                    
                    if not valid_province_series.empty:
                        province_counts_df = valid_province_series.value_counts().reset_index()
                        province_counts_df.columns = ['province_name', 'count']
                        province_counts_df = province_counts_df[province_counts_df['count'] > 0].sort_values('count', ascending=False)
                        
                        num_provinces_to_show = 15
                        province_demand_df_for_plot = province_counts_df.head(num_provinces_to_show)

                        if not province_demand_df_for_plot.empty:
                            plot_bar_chart(province_demand_df_for_plot, 'province_name', 'count',
                                           "热门招聘省份排行", "省份", "岗位数量")
                        else: st.info("处理后无省份数据可供展示 (已排除通用标签)。")
                    else: st.info("数据中无有效省份信息 (已排除通用标签)。")
                else: st.warning("缺少 'province_clean' 数据列，无法生成省份排行。")
            
            elif show_city_ranking_within_province:
                # Plot cities within the selected province
                if 'city_clean' in demand_display_df.columns and demand_display_df['city_clean'].notna().any():
                    city_series = demand_display_df['city_clean'].astype(str).fillna("未知").str.strip()
                    valid_city_series = city_series[~city_series.str.lower().isin(EXCLUDE_OTHER_LABELS_LOWER)]

                    if not valid_city_series.empty:
                        city_counts_df = valid_city_series.value_counts().reset_index()
                        city_counts_df.columns = ['city_name', 'count']
                        city_counts_df = city_counts_df[city_counts_df['count'] > 0].sort_values('count', ascending=False)

                        num_cities_to_show = 15
                        city_demand_df_for_plot = city_counts_df.head(num_cities_to_show)
                        
                        if not city_demand_df_for_plot.empty:
                             plot_bar_chart(city_demand_df_for_plot, 'city_name', 'count',
                                           f"{selected_province_demand}内热门招聘城市排行", "城市", "岗位数量")
                        else: st.info(f"在 {selected_province_demand} 内，处理后无城市数据可供展示 (已排除通用标签)。")
                    else: st.info(f"在 {selected_province_demand} 内，数据中无有效城市信息 (已排除通用标签)。")
                else: st.warning(f"缺少 'city_clean' 数据列，无法生成 {selected_province_demand} 内城市排行。")
            
            elif not selected_city_demand.startswith("所有城市"): # Specific city selected
                st.info(f"当前已按城市筛选: {selected_city_demand}。地区排行仅在选择“全国”或“所有城市”时显示。")
            
            st.markdown("---")
            if 'degree_name_cat' in demand_display_df.columns and demand_display_df['degree_name_cat'].notna().any():
                degree_demand_df_refined = get_refined_degree_counts(
                    demand_display_df['degree_name_cat'],
                    top_n_specific=5, 
                    other_label="其它具体学历",
                    min_count_threshold=max(1, int(len(demand_display_df) * 0.001)) if not demand_display_df.empty else 1
                )
                if not degree_demand_df_refined.empty:
                    plot_pie_chart(degree_demand_df_refined.head(8), 'degree_name_cat', 'count', "主要学历要求分布 (Top 8)", hole=0.3)
                else: st.info("学历数据不足或筛选后为空 (已排除通用标签)。")
            else: st.warning("缺少 'degree_name_cat' 数据列。")

        with col_dist2:
            # Show category plot if no specific category is filtered OR if it's a national/provincial overview
            show_category_plot = (selected_category_demand_filter == (category_options_demand[0] if category_options_demand else "所有类别")) or \
                                 (selected_province_demand == "全国" and selected_city_demand.startswith("所有城市")) or \
                                 (selected_province_demand != "全国" and selected_city_demand.startswith("所有城市"))

            if show_category_plot:
                if 'job_catory' in demand_display_df.columns and demand_display_df['job_catory'].notna().any():
                    category_demand_df_processed = prep_dist_data(demand_display_df, 'job_catory', top_n=10, other_label="其它职位类别")
                    if not category_demand_df_processed.empty:
                        plot_bar_chart(category_demand_df_processed, 'job_catory', 'count', "热门职位类别排行", "职位类别", "岗位数量", orientation='h')
                    else: st.info("职位类别数据不足或筛选后为空 (已排除通用标签)。")
                else: st.warning("缺少 'job_catory' 数据列。")
            elif selected_category_demand_filter != (category_options_demand[0] if category_options_demand else "所有类别"):
                 st.info(f"当前已筛选职位类别: {selected_category_demand_filter}。")


            st.markdown("---")
            if 'company_scale_cat' in demand_display_df.columns and demand_display_df['company_scale_cat'].notna().any():
                scale_counts = demand_display_df['company_scale_cat'].astype(str).str.strip().value_counts()
                scale_demand_df_filtered = scale_counts[~scale_counts.index.str.lower().isin(EXCLUDE_OTHER_LABELS_LOWER)].reset_index()
                if not scale_demand_df_filtered.empty:
                    scale_demand_df_filtered.columns = ['company_scale_cat', 'count']
                    if 'company_scale_cat' in df_jobs_main.columns and isinstance(df_jobs_main['company_scale_cat'].dtype, pd.CategoricalDtype): # Check original df for cat type
                        original_categories = df_jobs_main['company_scale_cat'].cat.categories
                        present_categories = [cat for cat in original_categories if cat in scale_demand_df_filtered['company_scale_cat'].unique()]
                        if present_categories:
                            scale_demand_df_filtered['company_scale_cat'] = pd.Categorical(scale_demand_df_filtered['company_scale_cat'],categories=present_categories,ordered=True)
                            scale_demand_df_filtered = scale_demand_df_filtered.sort_values('company_scale_cat')
                        else: scale_demand_df_filtered = scale_demand_df_filtered.sort_values('count', ascending=False)
                    else: scale_demand_df_filtered = scale_demand_df_filtered.sort_values('count', ascending=False)
                    plot_bar_chart(scale_demand_df_filtered, 'company_scale_cat', 'count', "公司规模需求分布", "公司规模", "岗位数量")
                else: st.info("公司规模数据不足或筛选后为空 (已排除通用标签)。")
            else: st.warning("缺少 'company_scale_cat' 数据列。")


    with tab_trends: # Market Dynamics
        st.subheader("市场动态与职位热度")
        if 'publish_date_dt' not in demand_display_df.columns or demand_display_df['publish_date_dt'].dropna().empty:
            st.info("缺少有效的发布日期信息，无法进行此部分分析。")
        else:
            st.markdown("#### 1. 主要职位类别市场份额演变")
            selected_lookback_market_share_key = st.selectbox(
                "选择市场份额图显示范围:", options=list(lookback_options.keys()), index=2, key="market_share_lookback_v9" # Incremented key
            )
            days_market_share = lookback_options.get(selected_lookback_market_share_key)

            if 'job_catory' in demand_display_df.columns and demand_display_df['job_catory'].notna().any():
                df_for_market_share = demand_display_df[['publish_date_dt', 'job_catory']].copy()
                df_for_market_share['job_catory'] = df_for_market_share['job_catory'].fillna('未知').astype(str).str.strip()
                df_for_market_share['publish_date_dt'] = pd.to_datetime(df_for_market_share['publish_date_dt'])

                category_over_time_full = df_for_market_share.groupby(
                    [pd.Grouper(key='publish_date_dt', freq='ME'), 'job_catory'], observed=False
                ).size().unstack(fill_value=0)

                cols_to_keep_cats_market = [
                    col for col in category_over_time_full.columns if str(col).lower().strip() not in EXCLUDE_OTHER_LABELS_LOWER
                ]
                category_over_time_full = category_over_time_full[cols_to_keep_cats_market]
                category_over_time_display = category_over_time_full.copy()

                if days_market_share and not category_over_time_display.empty:
                    max_date_cats = category_over_time_display.index.max()
                    if pd.notna(max_date_cats):
                        cutoff_cats = max_date_cats - pd.Timedelta(days=days_market_share)
                        min_date_cats = category_over_time_display.index.min()
                        if pd.notna(min_date_cats) and cutoff_cats < min_date_cats: cutoff_cats = min_date_cats
                        category_over_time_display = category_over_time_display[category_over_time_display.index >= cutoff_cats]
                
                if not category_over_time_display.empty:
                    num_top_cats_plot = 7
                    total_cat_counts = category_over_time_display.sum().sort_values(ascending=False)
                    final_cat_plot_data = pd.DataFrame()

                    if len(total_cat_counts) > 0:
                        meaningful_total_cat_counts_market = total_cat_counts[~total_cat_counts.index.to_series().astype(str).str.lower().isin(EXCLUDE_OTHER_LABELS_LOWER)]
                        if len(meaningful_total_cat_counts_market) > num_top_cats_plot:
                            top_n_cats_list = meaningful_total_cat_counts_market.nlargest(num_top_cats_plot).index.tolist()
                            other_cats_cols = [col for col in meaningful_total_cat_counts_market.index if col not in top_n_cats_list]
                            final_cat_plot_data = category_over_time_display[top_n_cats_list].copy()
                            if other_cats_cols and category_over_time_display[other_cats_cols].sum().sum() > 0 :
                                current_other_label = DEFAULT_OTHER_GROUP_LABEL if DEFAULT_OTHER_GROUP_LABEL.lower() not in EXCLUDE_OTHER_LABELS_LOWER else "其它汇总类别"
                                if current_other_label not in final_cat_plot_data.columns:
                                     final_cat_plot_data[current_other_label] = category_over_time_display[other_cats_cols].sum(axis=1)
                                else:
                                     final_cat_plot_data[current_other_label] += category_over_time_display[other_cats_cols].sum(axis=1)
                        elif not meaningful_total_cat_counts_market.empty:
                            final_cat_plot_data = category_over_time_display[meaningful_total_cat_counts_market.index].copy()

                    if not final_cat_plot_data.empty:
                        market_share_pct = final_cat_plot_data.apply(
                            lambda x: (x / x.sum() * 100) if x.sum() > 0 else 0, axis=1
                        ).fillna(0)
                        if not market_share_pct.empty:
                            market_share_pct = market_share_pct[final_cat_plot_data.sum().sort_values(ascending=False).index.intersection(market_share_pct.columns)]
                            fig_market_share = px.area(market_share_pct, title=f"主要职位类别市场份额演变 ({selected_lookback_market_share_key})")
                            fig_market_share.update_xaxes(title_text='月份', rangeslider_visible=True)
                            fig_market_share.update_yaxes(title_text='市场份额 (%)', ticksuffix="%")
                            fig_market_share.update_layout(legend_title_text='职位类别')
                            st.plotly_chart(fig_market_share, use_container_width=True)
                        else: st.info("市场份额数据计算后为空。")
                    else: st.info("处理后的职位类别数据为空 (已排除通用标签)。")
                else: st.info(f"在选定的时间范围 '{selected_lookback_market_share_key}' 内，无足够数据分析职位类别市场份额。")
            else: st.warning("缺少 'job_catory' 列，无法分析市场份额。")
            st.markdown("---")

            st.markdown("#### 2. 岗位时效性与需求动态")
            if 'job_age_days' in demand_display_df.columns and demand_display_df['job_age_days'].notna().any():
                freshness_df = get_job_freshness_distribution(demand_display_df)
                freshness_df_display = freshness_df[
                    ~freshness_df['freshness_range'].astype(str).str.lower().isin(EXCLUDE_OTHER_LABELS_LOWER)
                ].copy()
                if not freshness_df_display.empty:
                    plot_bar_chart(freshness_df_display, 'freshness_range', 'count',
                                   "当前筛选岗位的新鲜度分布", "发布时长范围", "岗位数量", orientation='v')
                else:
                    st.info("岗位新鲜度数据不足 (已排除通用标签)。")
            else:
                st.warning("缺少 'job_age_days' 列，无法分析岗位新鲜度。")

            st.markdown("##### 新增岗位数量趋势")
            freq_options_trend = {"每日": "D", "周度": "W-MON",  "月度": "ME"}
            selected_freq_label_new_jobs = st.selectbox(
                "选择时间聚合频率:", list(freq_options_trend.keys()), index=0, key="new_jobs_freq_v9" # Incremented key
            )
            freq_code_new_jobs = freq_options_trend[selected_freq_label_new_jobs]

            new_jobs_trend_series = get_time_series_data(
                demand_display_df,
                time_col='publish_date_dt',
                freq=freq_code_new_jobs,
                value_col=None
            )
            if not new_jobs_trend_series.empty:
                plot_line_chart(new_jobs_trend_series,
                                title=f"新增岗位数量趋势 ({selected_freq_label_new_jobs})",
                                y_label="新增岗位数量",
                                default_lookback_days=days_market_share)
            else:
                st.info("无法生成新增岗位数量趋势图 (数据不足或筛选后为空)。")

            st.markdown("##### 岗位更新时效性趋势")
            if 'publish_date_dt' in demand_display_df.columns and \
               'update_date_dt' in demand_display_df.columns and \
               'publish_to_update_hours' in demand_display_df.columns and \
               demand_display_df['publish_to_update_hours'].notna().any():

                short_term_threshold_days = st.slider("“速招”定义 (发布到首次更新 <= X 天):", 1, 30, 7, key="short_term_days_v9") # Incremented
                long_term_threshold_days = st.slider("“长招”定义 (发布后 > Y 天仍低频更新):", 30, 180, 60, key="long_term_days_v9") # Incremented

                df_temp_timeliness = demand_display_df[
                    demand_display_df['publish_date_dt'].notna() &
                    demand_display_df['update_date_dt'].notna() &
                    demand_display_df['publish_to_update_hours'].notna()
                ].copy()
                df_temp_timeliness['publish_date_dt'] = pd.to_datetime(df_temp_timeliness['publish_date_dt'])

                if not df_temp_timeliness.empty:
                    df_temp_timeliness['time_to_update_days'] = df_temp_timeliness['publish_to_update_hours'] / 24
                    df_temp_timeliness['is_short_term_updated'] = (df_temp_timeliness['time_to_update_days'] >= 0) & \
                                                                  (df_temp_timeliness['time_to_update_days'] <= short_term_threshold_days)
                    
                    job_id_col = 'job_id' if 'job_id' in df_temp_timeliness.columns else df_temp_timeliness.columns[0]

                    monthly_timeliness_stats = df_temp_timeliness.groupby(
                        pd.Grouper(key='publish_date_dt', freq='ME')
                    ).agg(
                        total_new_jobs=(job_id_col, 'count'),
                        short_term_updated_jobs=('is_short_term_updated', 'sum')
                    ).reset_index()

                    if not monthly_timeliness_stats.empty and monthly_timeliness_stats['total_new_jobs'].sum() >0:
                        monthly_timeliness_stats['short_term_updated_pct'] = \
                            (monthly_timeliness_stats['short_term_updated_jobs'] / monthly_timeliness_stats['total_new_jobs'] * 100).fillna(0)

                        fig_timeliness = make_subplots(specs=[[{"secondary_y": True}]])
                        fig_timeliness.add_trace(
                            go.Bar(x=monthly_timeliness_stats['publish_date_dt'],
                                   y=monthly_timeliness_stats['total_new_jobs'],
                                   name='当月新增岗位总数'),
                            secondary_y=False,
                        )
                        fig_timeliness.add_trace(
                            go.Scatter(x=monthly_timeliness_stats['publish_date_dt'],
                                       y=monthly_timeliness_stats['short_term_updated_pct'],
                                       name=f'速招岗位占比 (≤{short_term_threshold_days}天内更新)', mode='lines+markers'),
                            secondary_y=True,
                        )
                        fig_timeliness.update_layout(
                            title_text=f'岗位更新时效性趋势 (速招占比)',
                            xaxis_title='发布月份',
                            legend_title_text='指标'
                        )
                        fig_timeliness.update_yaxes(title_text="岗位数量", secondary_y=False)
                        fig_timeliness.update_yaxes(title_text="速招占比 (%)", secondary_y=True, ticksuffix="%")
                        st.plotly_chart(fig_timeliness, use_container_width=True)

                    df_temp_timeliness['is_late_updated'] = (df_temp_timeliness['time_to_update_days'] > long_term_threshold_days)
                    monthly_late_update_stats = df_temp_timeliness.groupby(
                         pd.Grouper(key='publish_date_dt', freq='ME')
                    ).agg(
                        total_new_jobs=(job_id_col, 'count'),
                        late_updated_jobs=('is_late_updated', 'sum')
                    ).reset_index()

                    if not monthly_late_update_stats.empty and monthly_late_update_stats['total_new_jobs'].sum() > 0:
                        monthly_late_update_stats['late_updated_pct'] = \
                            (monthly_late_update_stats['late_updated_jobs'] / monthly_late_update_stats['total_new_jobs'] * 100).fillna(0)

                        fig_late_update = px.line(monthly_late_update_stats, x='publish_date_dt', y='late_updated_pct',
                                                  title=f'低频/晚更新岗位占比趋势 (首次更新 > {long_term_threshold_days} 天)',
                                                  labels={'publish_date_dt': '发布月份', 'late_updated_pct': '占比 (%)'})
                        fig_late_update.update_yaxes(ticksuffix="%")
                        st.plotly_chart(fig_late_update, use_container_width=True)
                        st.caption(f"低频/晚更新指岗位发布后，首次记录的更新发生在 {long_term_threshold_days} 天之后。这可能暗示招聘周期较长或岗位需求不紧急。")
                    elif not monthly_timeliness_stats.empty :
                        st.info("速招趋势已显示。低频/晚更新趋势数据不足。")
                else:
                    st.info("用于时效性趋势分析的数据不足（缺少有效的发布/更新日期或更新间隔）。")
            else:
                st.caption("缺少 'update_date_dt' 或 'publish_to_update_hours' 数据，无法进行详细的岗位更新时效性趋势分析。")


    with tab_edu_trends:
        st.subheader("学历要求随时间变化趋势")
        if 'publish_date_dt' in demand_display_df.columns and 'degree_name_cat' in demand_display_df.columns and \
            demand_display_df['publish_date_dt'].notna().any() and demand_display_df['degree_name_cat'].notna().any():

            meaningful_job_categories_edu = get_meaningful_filter_options(demand_display_df, 'job_catory', "总体趋势 (所有类别汇总)")
            selected_cat_for_edu = st.selectbox(
                "选择职位类别以查看其学历需求变化:", meaningful_job_categories_edu, index=0, key="edu_trend_cat_select_v5" # Incremented
            )
            selected_lookback_edu_key = st.selectbox(
                "选择学历趋势图显示范围:", options=list(lookback_options.keys()), index=1, key="edu_trend_lookback_v5" # Incremented
            )
            lookback_days_edu_val = lookback_options[selected_lookback_edu_key]

            df_for_edu_trend_analysis = demand_display_df.copy()
            if selected_cat_for_edu != "总体趋势 (所有类别汇总)":
                df_for_edu_trend_analysis = df_for_edu_trend_analysis[df_for_edu_trend_analysis['job_catory'] == selected_cat_for_edu]
            
            df_for_edu_trend_analysis['publish_date_dt'] = pd.to_datetime(df_for_edu_trend_analysis['publish_date_dt'])

            if not df_for_edu_trend_analysis.empty:
                def apply_refined_degree_counts_for_trend(df_period):
                    if df_period.empty or 'degree_name_cat' not in df_period.columns:
                         return pd.Series(dtype='int64')
                    refined_counts_df = get_refined_degree_counts(
                        df_period['degree_name_cat'],
                        top_n_specific=3,
                        other_label="其它特定学历",
                        min_count_threshold=1
                        )
                    if not refined_counts_df.empty:
                        return refined_counts_df.set_index('degree_name_cat')['count']
                    return pd.Series(dtype='int64')

                degree_over_time_refined = df_for_edu_trend_analysis.groupby(
                    pd.Grouper(key='publish_date_dt', freq='ME')
                ).apply(apply_refined_degree_counts_for_trend)

                if isinstance(degree_over_time_refined, pd.Series) and isinstance(degree_over_time_refined.index, pd.MultiIndex):
                    degree_over_time_refined = degree_over_time_refined.unstack(level=-1, fill_value=0)
                elif not isinstance(degree_over_time_refined, pd.DataFrame) :
                    degree_over_time_refined = pd.DataFrame()

                if not degree_over_time_refined.empty:
                    degree_over_time_refined.columns = degree_over_time_refined.columns.astype(str)
                    degree_over_time_refined = degree_over_time_refined.loc[:, (degree_over_time_refined != 0).any(axis=0)]

                final_degree_plot_data_abs = degree_over_time_refined.copy()
                if lookback_days_edu_val and not final_degree_plot_data_abs.empty:
                    max_date_edu = final_degree_plot_data_abs.index.max()
                    if pd.notna(max_date_edu):
                        cutoff_date_edu = max_date_edu - pd.Timedelta(days=lookback_days_edu_val)
                        min_date_edu = final_degree_plot_data_abs.index.min()
                        if pd.notna(min_date_edu) and cutoff_date_edu < min_date_edu:
                            cutoff_date_edu = min_date_edu
                        final_degree_plot_data_abs = final_degree_plot_data_abs[final_degree_plot_data_abs.index >= cutoff_date_edu]

                if not final_degree_plot_data_abs.empty:
                    final_degree_plot_data_abs = final_degree_plot_data_abs.loc[:, (final_degree_plot_data_abs != 0).any(axis=0)]

                if not final_degree_plot_data_abs.empty:
                    sorted_cols_for_legend_edu = final_degree_plot_data_abs.sum().sort_values(ascending=False).index
                    valid_cols_for_plot = [col for col in sorted_cols_for_legend_edu if col in final_degree_plot_data_abs.columns]
                    final_degree_plot_data_abs_sorted = final_degree_plot_data_abs[valid_cols_for_plot]

                    if not final_degree_plot_data_abs_sorted.empty:
                        fig_degree_time_abs = px.area(final_degree_plot_data_abs_sorted, title=f"{selected_cat_for_edu} - 主要学历要求数量 ({selected_lookback_edu_key})")
                        fig_degree_time_abs.update_xaxes(title_text='月份', rangeslider_visible=True)
                        fig_degree_time_abs.update_yaxes(title_text='岗位数量')
                        fig_degree_time_abs.update_layout(legend_title_text='学历要求')
                        st.plotly_chart(fig_degree_time_abs, use_container_width=True)

                        final_degree_plot_data_pct = final_degree_plot_data_abs_sorted.apply(lambda x: (x / x.sum() * 100) if x.sum() > 0 else 0, axis=1).fillna(0)
                        if not final_degree_plot_data_pct.empty:
                            fig_degree_time_pct = px.area(final_degree_plot_data_pct, title=f"{selected_cat_for_edu} - 主要学历要求占比 (%) ({selected_lookback_edu_key})")
                            fig_degree_time_pct.update_xaxes(title_text='月份', rangeslider_visible=True)
                            fig_degree_time_pct.update_yaxes(title_text='占比 (%)', ticksuffix="%")
                            fig_degree_time_pct.update_layout(legend_title_text='学历要求')
                            st.plotly_chart(fig_degree_time_pct, use_container_width=True)

                        if len(final_degree_plot_data_pct) >= 2:
                            start_period_data = final_degree_plot_data_pct.iloc[[0, -1]].copy(); start_period_data.index = ['期初占比', '期末占比']
                            start_period_data_melted = start_period_data.reset_index().melt(id_vars='index', var_name='学历要求', value_name='占比 (%)')

                            fig_stacked_bar_edu = px.bar(start_period_data_melted, x='index', y='占比 (%)', color='学历要求',
                                                            title=f'{selected_cat_for_edu} - 学历要求占比: 期初 vs 期末 ({selected_lookback_edu_key})',
                                                            text_auto='.1f')
                            fig_stacked_bar_edu.update_xaxes(title_text='时期')
                            fig_stacked_bar_edu.update_yaxes(title_text='占比 (%)')
                            fig_stacked_bar_edu.update_layout(legend_title_text='学历构成')
                            st.plotly_chart(fig_stacked_bar_edu, use_container_width=True)
                        elif not final_degree_plot_data_pct.empty :
                             st.info("数据量不足以展示期初与期末对比图。")

                    else: st.info(f"在选定的时间范围和类别下，经过滤后主要学历要求数据不足。")
                else: st.info(f"在选定的时间范围和类别下，学历要求数据不足(已排除通用标签)。")
            else: st.info("当前筛选条件下无数据分析学历需求变化。")
        else: st.info("缺少必要列(`publish_date_dt`, `degree_name_cat`)或数据不足以进行学历趋势分析。")