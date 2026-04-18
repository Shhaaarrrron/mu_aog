import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

st.set_page_config(page_title="按零件号分析", page_icon="✈️")

if "data_loaded" not in st.session_state:
    st.switch_page("app.py")

aog_df = st.session_state.aog_df
zsht_df = st.session_state.zsht_df
new_aog_df = st.session_state.new_aog_df

get_monthly_data = st.session_state.get_monthly_data
get_yearly_data = st.session_state.get_yearly_data
get_monthly_data_by_year = st.session_state.get_monthly_data_by_year
calculate_cv = st.session_state.calculate_cv
calculate_trend = st.session_state.calculate_trend

st.title("📊 按零件号分析")

overview_tab, detail_tab = st.tabs(["📊 概览", "📋 详细"])

with overview_tab:
    st.header("零件号统计概览")

    summary_data = []
    for matnr in sorted(aog_df["MATNR"].dropna().unique()):
        matnr_aog = aog_df[aog_df["MATNR"] == matnr]
        matnr_zsht = zsht_df[zsht_df["MATNR"] == matnr]
        matched = matnr_aog[matnr_aog["CHID"].notna() & (matnr_aog["CHID"] != "")]

        min_date = matnr_aog["ZZJRRQ"].min()
        max_date = matnr_aog["ZZJRRQ"].max()

        summary_data.append(
            {
                "零件号": matnr,
                "AOG记录数": len(matnr_aog),
                "已匹配拆换": len(matched),
                "未匹配": len(matnr_aog) - len(matched),
                "匹配率": f"{len(matched) / len(matnr_aog) * 100:.1f}%"
                if len(matnr_aog) > 0
                else "0%",
                "最早求援": min_date.strftime("%Y-%m-%d")
                if pd.notna(min_date)
                else "",
                "最晚求援": max_date.strftime("%Y-%m-%d")
                if pd.notna(max_date)
                else "",
                "采购记录数": len(matnr_zsht),
            }
        )

    summary_df = pd.DataFrame(summary_data)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("零件种类", len(summary_df))
    col2.metric("AOG总记录", len(aog_df))
    col3.metric("已匹配拆换", int(summary_df["已匹配拆换"].sum()))
    col4.metric("采购总记录", len(zsht_df))

    st.markdown("---")

    stability_data = []
    for matnr in sorted(aog_df["MATNR"].dropna().unique()):
        matnr_aog = aog_df[aog_df["MATNR"] == matnr]
        yearly_counts = list(get_yearly_data(matnr_aog, "ZZJRRQ").values())
        yearly_cv = calculate_cv(yearly_counts)
        monthly_counts_list = list(
            get_monthly_data_by_year(matnr_aog, "ZZJRRQ").values()
        )
        monthly_cv = calculate_cv(monthly_counts_list)
        total_demand = len(matnr_aog)
        stability_data.append(
            {
                "零件号": matnr,
                "年度Cv": round(yearly_cv, 2),
                "月度Cv": round(monthly_cv, 2),
                "总需求量": total_demand,
            }
        )

    stability_df = pd.DataFrame(stability_data)

    avg_demand = stability_df["总需求量"].mean()

    stability_combined_chart = {
        "tooltip": {"trigger": "axis"},
        "legend": {
            "data": ["年度Cv", "月度Cv", "总需求量", "平均需求量"],
            "top": 30,
        },
        "grid": {"left": "3%", "right": "8%", "bottom": "3%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": stability_df["零件号"].tolist(),
            "axisLabel": {"rotate": 45, "interval": 0},
        },
        "yAxis": [
            {"type": "value", "name": "Cv值", "position": "left"},
            {"type": "value", "name": "需求量", "position": "right"},
        ],
        "series": [
            {
                "name": "年度Cv",
                "type": "bar",
                "data": stability_df["年度Cv"].tolist(),
                "itemStyle": {"color": "#EE6666"},
            },
            {
                "name": "月度Cv",
                "type": "bar",
                "data": stability_df["月度Cv"].tolist(),
                "itemStyle": {"color": "#5470C6"},
            },
            {
                "name": "总需求量",
                "type": "line",
                "data": stability_df["总需求量"].tolist(),
                "itemStyle": {"color": "#91CC75"},
                "yAxisIndex": 1,
            },
            {
                "name": "平均需求量",
                "type": "line",
                "data": [round(avg_demand, 1)] * len(stability_df),
                "itemStyle": {"color": "#FAC858"},
                "lineStyle": {"type": "dashed"},
                "yAxisIndex": 1,
                "symbol": "none",
            },
        ],
    }
    st.subheader("需求稳定度分析（Cv越小越稳定）")
    st_echarts(options=stability_combined_chart, height="400px")

    st.markdown("---")
    st.subheader("需求趋势分析（斜率>0表示上升趋势）")

    trend_data = []
    for matnr in sorted(aog_df["MATNR"].dropna().unique()):
        matnr_aog = aog_df[aog_df["MATNR"] == matnr]
        yearly_counts = get_yearly_data(matnr_aog, "ZZJRRQ")
        slope, weighted_avg_year, recent_ratio = calculate_trend(yearly_counts)
        total_demand = len(matnr_aog)
        trend_data.append(
            {
                "零件号": matnr,
                "趋势斜率": round(slope, 3),
                "加权平均年份": round(weighted_avg_year, 1),
                "近期需求占比": round(recent_ratio, 2),
                "总需求量": total_demand,
            }
        )

    trend_df = pd.DataFrame(trend_data)

    avg_slope = trend_df["趋势斜率"].mean()

    trend_combined_chart = {
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["趋势斜率", "近期需求占比", "平均斜率"], "top": 30},
        "grid": {"left": "3%", "right": "8%", "bottom": "3%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": trend_df["零件号"].tolist(),
            "axisLabel": {"rotate": 45, "interval": 0},
        },
        "yAxis": [
            {"type": "value", "name": "斜率", "position": "left"},
            {"type": "value", "name": "占比", "position": "right", "max": 1},
        ],
        "series": [
            {
                "name": "趋势斜率",
                "type": "bar",
                "data": trend_df["趋势斜率"].tolist(),
                "itemStyle": {"color": "#5470C6"},
            },
            {
                "name": "近期需求占比",
                "type": "line",
                "data": trend_df["近期需求占比"].tolist(),
                "itemStyle": {"color": "#91CC75"},
                "yAxisIndex": 1,
            },
            {
                "name": "平均斜率",
                "type": "line",
                "data": [round(avg_slope, 3)] * len(trend_df),
                "itemStyle": {"color": "#FAC858"},
                "lineStyle": {"type": "dashed"},
                "yAxisIndex": 0,
                "symbol": "none",
            },
        ],
    }
    st_echarts(options=trend_combined_chart, height="400px")

    st.markdown("---")

    search_matnr = st.text_input("搜索零件号")
    if search_matnr:
        filtered_summary = summary_df[
            summary_df["零件号"].str.contains(search_matnr, case=False)
        ]
    else:
        filtered_summary = summary_df

    st.dataframe(filtered_summary, use_container_width=True)

    st.markdown("---")
    st.subheader("年度趋势分析")
    overview_matnr_list = ["全部"] + sorted(
        aog_df["MATNR"].dropna().unique().tolist()
    )
    overview_selected_matnr = st.selectbox("选择零件号", overview_matnr_list)

    if overview_selected_matnr == "全部":
        overview_aog = aog_df
        overview_zsht = zsht_df
        overview_new_aog = new_aog_df
    else:
        overview_aog = aog_df[aog_df["MATNR"] == overview_selected_matnr]
        overview_zsht = zsht_df[zsht_df["MATNR"] == overview_selected_matnr]
        overview_new_aog = new_aog_df[new_aog_df["pn"] == overview_selected_matnr]

    aog_yearly = get_yearly_data(overview_aog, "ZZJRRQ")
    zsht_yearly = get_yearly_data(overview_zsht, "BEDAT")
    new_aog_yearly = get_yearly_data(overview_new_aog, "create_time")

    years = [str(y) for y in range(2011, 2024)]

    aog_year_values = [aog_yearly.get(int(y), 0) for y in years]
    zsht_year_values = [zsht_yearly.get(int(y), 0) for y in years]
    new_aog_year_values = [new_aog_yearly.get(int(y), 0) for y in years]

    year_chart_options = {
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["AOG求援", "采购订单", "新求援数据"], "top": 30},
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {"type": "category", "data": years},
        "yAxis": {"type": "value", "name": "数量"},
        "series": [
            {
                "name": "AOG求援",
                "type": "bar",
                "data": aog_year_values,
                "itemStyle": {"color": "#5470C6"},
            },
            {
                "name": "采购订单",
                "type": "line",
                "data": zsht_year_values,
                "itemStyle": {"color": "#91CC75"},
            },
            {
                "name": "新求援数据",
                "type": "line",
                "data": new_aog_year_values,
                "itemStyle": {"color": "#EE6666"},
                "lineStyle": {"width": 3},
            },
        ],
    }

    st_echarts(options=year_chart_options, height="400px")

with detail_tab:
    st.header("按零件号详情")

    matnr_list = sorted(aog_df["MATNR"].dropna().unique().tolist())
    selected_matnr = st.selectbox("选择零件号", matnr_list)

    filtered_aog = aog_df[aog_df["MATNR"] == selected_matnr]
    filtered_zsht = zsht_df[zsht_df["MATNR"] == selected_matnr]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AOG记录数", len(filtered_aog))
    matched = filtered_aog[
        filtered_aog["CHID"].notna() & (filtered_aog["CHID"] != "")
    ]
    col2.metric("已匹配拆换", len(matched))
    col3.metric("未匹配", len(filtered_aog) - len(matched))
    col4.metric(
        "匹配率",
        f"{len(matched) / len(filtered_aog) * 100:.1f}%"
        if len(filtered_aog) > 0
        else "0%",
    )

    st.markdown("---")

    min_date = filtered_aog["ZZJRRQ"].min()
    max_date = filtered_aog["ZZJRRQ"].max()

    if pd.isna(min_date) or pd.isna(max_date):
        st.warning("数据中没有有效的日期信息")
        st.stop()

    zsht_min_date = filtered_zsht["BEDAT"].min()
    zsht_max_date = filtered_zsht["BEDAT"].max()

    if pd.isna(zsht_min_date):
        min_year = min_date.year
    else:
        min_year = min(int(zsht_min_date.year), min_date.year)

    if pd.isna(zsht_max_date):
        max_year = max_date.year
    else:
        max_year = max(int(zsht_max_date.year), max_date.year)

    years = list(range(min_year, max_year + 1))
    selected_year = st.selectbox("选择年份", years, index=len(years) - 1)

    months = [f"{i}月" for i in range(1, 13)]

    aog_monthly = get_monthly_data(filtered_aog, selected_year, "ZZJRRQ")
    purchase_monthly = get_monthly_data(filtered_zsht, selected_year, "BEDAT")

    next_year = selected_year + 1
    purchase_next_year_same_month = get_monthly_data(
        filtered_zsht, next_year, "BEDAT"
    )

    last_year = selected_year - 1
    purchase_last_year_same_month = get_monthly_data(
        filtered_zsht, last_year, "BEDAT"
    )

    chart_options = {
        "tooltip": {"trigger": "axis"},
        "legend": {
            "data": ["当月AOG", "当年采购", "前年采购", "明年采购"],
            "top": 30,
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {"type": "category", "data": months},
        "yAxis": {"type": "value", "name": "数量"},
        "series": [
            {
                "name": "当月AOG",
                "type": "bar",
                "data": aog_monthly,
                "itemStyle": {"color": "#5470C6"},
            },
            {
                "name": "当年采购",
                "type": "line",
                "data": purchase_monthly,
                "itemStyle": {"color": "#91CC75"},
            },
            {
                "name": "前年采购",
                "type": "line",
                "data": purchase_last_year_same_month,
                "itemStyle": {"color": "#FAC858"},
            },
            {
                "name": "明年采购",
                "type": "line",
                "data": purchase_next_year_same_month,
                "itemStyle": {"color": "#EE6666"},
            },
        ],
    }

    st.subheader("详细数据")
    st.dataframe(
        filtered_aog[
            ["EBELN", "MATNR", "ADPRI", "ZZJRRQ", "ZZGHRQ", "ZCHDAT", "ZZCHYY"]
        ].sort_values("ZZJRRQ", ascending=False),
        use_container_width=True,
    )

    st.markdown("---")
    st.subheader(f"{selected_year}年月度趋势分析")
    st_echarts(options=chart_options, height="400px")
