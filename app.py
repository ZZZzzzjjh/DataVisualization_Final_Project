from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from ai_insights import build_local_insights, generate_ai_insight, has_ai_config  # noqa: E402
from charts import (  # noqa: E402
    category_bar,
    category_price_scatter,
    category_region_heatmap,
    category_share_doughnut,
    category_waterfall,
    daily_sales_line,
    monthly_category_area,
    monthly_sales_line,
    payment_doughnut,
    price_band_bar,
    price_band_doughnut,
    product_bar,
    product_treemap,
    region_bar,
    region_payment_bar,
    region_payment_sunburst,
    region_price_heatmap,
    weekday_bar,
)
from data_loader import (  # noqa: E402
    PRICE_BAND_ORDER,
    RAW_CSV,
    category_region_summary,
    category_summary,
    daily_summary,
    filter_sales,
    kpi_metrics,
    load_field_dictionary,
    load_sales_data,
    load_summary,
    monthly_category_summary,
    monthly_summary,
    payment_summary,
    price_band_summary,
    product_summary,
    product_tree_summary,
    region_price_summary,
    region_payment_summary,
    region_summary,
    weekday_summary,
)
from styles import apply_style  # noqa: E402


st.set_page_config(page_title="2024年电商平台在线销售可视化分析", page_icon="📊", layout="wide")
apply_style()


@st.cache_data(show_spinner="正在读取 2024 年在线销售数据...")
def cached_sales() -> pd.DataFrame:
    return load_sales_data()


@st.cache_data(show_spinner=False)
def cached_summary() -> pd.DataFrame:
    return load_summary()


@st.cache_data(show_spinner=False)
def cached_dictionary() -> pd.DataFrame:
    return load_field_dictionary()


sales_df = cached_sales()

st.title("2024年电商平台在线销售可视化分析")
st.caption("数据源：Kaggle Online Sales Dataset - Popular Marketplace Data；当前样本覆盖 2024-01-01 至 2024-08-27。")

with st.sidebar:
    st.header("筛选条件")
    min_date = sales_df["DateOnly"].min().date()
    max_date = sales_df["DateOnly"].max().date()
    selected_dates = st.date_input("交易日期", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        date_range = (pd.Timestamp(selected_dates[0]), pd.Timestamp(selected_dates[1]))
    else:
        date_range = (pd.Timestamp(min_date), pd.Timestamp(max_date))

    category_options = sorted(sales_df["Product Category"].dropna().unique())
    price_options = [label for label in PRICE_BAND_ORDER if label in set(sales_df["PriceBand"].dropna())]
    region_options = sorted(sales_df["Region"].dropna().unique())
    payment_options = sorted(sales_df["Payment Method"].dropna().unique())

    categories = st.multiselect("商品类别", category_options)
    price_bands = st.multiselect("价格带", price_options)
    regions = st.multiselect("销售地区", region_options)
    payments = st.multiselect("支付方式", payment_options)
    top_n = st.slider("商品排行数量", min_value=5, max_value=30, value=15)

filtered = filter_sales(sales_df, date_range, categories, price_bands, regions, payments)
if filtered.empty:
    st.warning("当前筛选条件下没有可用数据，已回退为全量样本。")
    filtered = sales_df

metric_cols = st.columns(5)
for col, (label, value) in zip(metric_cols, kpi_metrics(filtered).items()):
    col.metric(label, value)

tab_overview, tab_time, tab_category, tab_price, tab_region, tab_ai, tab_data = st.tabs(
    ["总览看板", "时间趋势", "品类偏好", "价格带分析", "地区与支付方式", "AI洞察", "数据管理"]
)

with tab_overview:
    category_df = category_summary(filtered)
    price_df = price_band_summary(filtered)
    region_df = region_summary(filtered)
    payment_df = payment_summary(filtered)

    st.plotly_chart(monthly_sales_line(monthly_summary(filtered)), use_container_width=True, key="overview_monthly")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(category_share_doughnut(category_df), use_container_width=True, key="overview_category_share")
    with c2:
        st.plotly_chart(category_waterfall(category_df), use_container_width=True, key="overview_category_waterfall")

    c3, c4, c5 = st.columns([1, 1, 1])
    with c3:
        st.plotly_chart(price_band_doughnut(price_df), use_container_width=True, key="overview_price_share")
    with c4:
        st.plotly_chart(region_bar(region_df), use_container_width=True, key="overview_region")
    with c5:
        st.plotly_chart(payment_doughnut(payment_df), use_container_width=True, key="overview_payment")

with tab_time:
    c1, c2 = st.columns([1.25, 0.9])
    with c1:
        st.plotly_chart(monthly_sales_line(monthly_summary(filtered)), use_container_width=True, key="time_monthly")
    with c2:
        st.plotly_chart(weekday_bar(weekday_summary(filtered)), use_container_width=True, key="time_weekday")
    st.plotly_chart(daily_sales_line(daily_summary(filtered)), use_container_width=True, key="time_daily")
    st.plotly_chart(monthly_category_area(monthly_category_summary(filtered)), use_container_width=True, key="time_monthly_category")

with tab_category:
    category_df = category_summary(filtered)
    c1, c2 = st.columns([1.05, 0.95])
    with c1:
        st.plotly_chart(category_bar(category_df), use_container_width=True, key="category_bar")
    with c2:
        st.plotly_chart(category_price_scatter(category_df), use_container_width=True, key="category_scatter")
    st.plotly_chart(category_region_heatmap(category_region_summary(filtered)), use_container_width=True, key="category_region_heatmap")
    st.plotly_chart(product_treemap(product_tree_summary(filtered)), use_container_width=True, key="product_tree")
    st.plotly_chart(product_bar(product_summary(filtered, top_n)), use_container_width=True, key="product_bar")
    category_table = category_df.assign(销售额占比=lambda d: d["销售额占比"].map("{:.2%}".format))
    st.dataframe(category_table, use_container_width=True, hide_index=True)

with tab_price:
    price_df = price_band_summary(filtered)
    c1, c2 = st.columns([1.15, 0.85])
    with c1:
        st.plotly_chart(price_band_bar(price_df), use_container_width=True, key="price_bar")
    with c2:
        st.plotly_chart(price_band_doughnut(price_df), use_container_width=True, key="price_share")
    st.plotly_chart(region_price_heatmap(region_price_summary(filtered)), use_container_width=True, key="price_region_heatmap")
    price_table = price_df.assign(销售额占比=lambda d: d["销售额占比"].map("{:.2%}".format))
    st.dataframe(price_table, use_container_width=True, hide_index=True)

with tab_region:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(region_bar(region_summary(filtered)), use_container_width=True, key="region_bar")
    with c2:
        st.plotly_chart(payment_doughnut(payment_summary(filtered)), use_container_width=True, key="payment_pie")
    st.plotly_chart(region_payment_sunburst(region_payment_summary(filtered)), use_container_width=True, key="region_payment_sunburst")
    st.plotly_chart(region_payment_bar(region_payment_summary(filtered)), use_container_width=True, key="region_payment")
    st.dataframe(region_payment_summary(filtered), use_container_width=True, hide_index=True)

with tab_ai:
    insights = build_local_insights(filtered)
    insight_cols = st.columns(4)
    for col, insight in zip(insight_cols, insights):
        accent = insight.get("accent", "muted")
        col.markdown(
            f"""
            <div class="ai-card ai-{accent}">
                <h3>{insight["title"]}</h3>
                <p>{insight["body"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    focus = st.text_area("AI分析关注点", value="请关注销售增长机会、品类结构、地区差异和支付方式风险。", height=90)
    c1, c2 = st.columns([0.22, 0.78])
    with c1:
        run_ai = st.button("生成AI洞察", type="primary", use_container_width=True)
    with c2:
        if not has_ai_config():
            st.warning("未检测到 AI API Key，请在 Code/streamlit_app/.env 中配置 DEEPSEEK_API_KEY。")
        else:
            st.caption("AI接口已就绪，生成内容会基于当前筛选后的聚合数据。")

    if run_ai:
        with st.spinner("正在生成AI洞察..."):
            try:
                st.session_state["ai_response"] = generate_ai_insight(filtered, focus)
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))

    if st.session_state.get("ai_response"):
        st.markdown(st.session_state["ai_response"])

with tab_data:
    st.caption(f"当前读取文件：{RAW_CSV.name}")
    c1, c2 = st.columns([0.9, 1.1])
    with c1:
        st.dataframe(cached_summary(), use_container_width=True, hide_index=True)
    with c2:
        st.dataframe(cached_dictionary(), use_container_width=True, hide_index=True)

    show_cols = [
        "Transaction ID",
        "Date",
        "Product Category",
        "Product Name",
        "Units Sold",
        "Unit Price",
        "Total Revenue",
        "Region",
        "Payment Method",
        "PriceBand",
    ]
    preview = filtered[show_cols].head(1000).rename(
        columns={
            "Transaction ID": "交易编号",
            "Date": "交易日期",
            "Product Category": "商品类别",
            "Product Name": "商品名称",
            "Units Sold": "销售数量",
            "Unit Price": "商品单价",
            "Total Revenue": "销售额",
            "Region": "销售地区",
            "Payment Method": "支付方式",
            "PriceBand": "价格带",
        }
    )
    st.dataframe(preview, use_container_width=True, hide_index=True)
