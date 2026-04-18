from datetime import datetime

import pandas as pd
import streamlit as st
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


st.set_page_config(page_title="AOG 零件维修资源规划", page_icon="✈️", layout="wide")


def load_data():
    aog_path = "aog_with_exchange_match.csv"
    zsht_path = "ZSHT_202604141503.csv"
    new_aog_path = "求援数据_with_pnr_id.csv"

    aog_df = pd.read_csv(BASE_DIR, aog_path)
    zsht_df = pd.read_csv(BASE_DIR, zsht_path)
    new_aog_df = pd.read_csv(BASE_DIR, new_aog_path)

    aog_df["BEDAT"] = pd.to_datetime(
        aog_df["BEDAT"].astype(str), format="%Y%m%d", errors="coerce"
    )
    aog_df["ZZJRRQ"] = pd.to_datetime(
        aog_df["ZZJRRQ"].astype(str), format="%Y%m%d", errors="coerce"
    )
    aog_df["ZZGHRQ"] = pd.to_datetime(
        aog_df["ZZGHRQ"].astype(str).str.replace(".0", "", regex=False),
        format="%Y%m%d",
        errors="coerce",
    )
    aog_df["ZCHDAT"] = pd.to_datetime(
        aog_df["ZCHDAT"].astype(str).str.replace(".0", "", regex=False),
        format="%Y%m%d",
        errors="coerce",
    )

    zsht_df["BEDAT"] = pd.to_datetime(
        zsht_df["BEDAT"].astype(str), format="%Y%m%d", errors="coerce"
    )

    new_aog_df["create_time"] = pd.to_datetime(
        new_aog_df["create_time"], errors="coerce"
    )

    return aog_df, zsht_df, new_aog_df


def get_monthly_data(df, year, date_col="ZZJRRQ"):
    monthly_counts = []
    for month in range(1, 13):
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1)
        else:
            month_end = datetime(year, month + 1, 1)

        count = len(df[(df[date_col] >= month_start) & (df[date_col] < month_end)])
        monthly_counts.append(count)
    return monthly_counts


def get_yearly_data(df, date_col="ZZJRRQ", start_year=2011, end_year=2026):
    yearly_counts = {y: 0 for y in range(start_year, end_year + 1)}
    for _, row in df.iterrows():
        date_val = row[date_col]
        if pd.notna(date_val):
            if hasattr(date_val, "year"):
                year = date_val.year
            else:
                year = int(str(int(date_val))[:4])
            if start_year <= year <= end_year:
                yearly_counts[year] += 1
    return yearly_counts


def get_monthly_data_by_year(df, date_col="ZZJRRQ", start_year=2011, end_year=2023):
    monthly_counts = {}
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            monthly_counts[(year, month)] = 0

    for _, row in df.iterrows():
        date_val = row[date_col]
        if pd.notna(date_val):
            if hasattr(date_val, "year"):
                year = date_val.year
                month = date_val.month
            else:
                date_str = str(int(date_val))
                year = int(date_str[:4])
                month = int(date_str[4:6])
            if start_year <= year <= end_year and 1 <= month <= 12:
                monthly_counts[(year, month)] += 1
    return monthly_counts


def calculate_cv(values):
    if len(values) == 0:
        return 0
    mean_val = sum(values) / len(values)
    if mean_val == 0:
        return 0
    variance = sum((x - mean_val) ** 2 for x in values) / len(values)
    std_val = variance**0.5
    return std_val / mean_val


def calculate_trend(yearly_counts, start_year=2011, end_year=2023):
    years = list(range(start_year, end_year + 1))
    values = [yearly_counts.get(y, 0) for y in years]

    if sum(values) == 0:
        return 0, 0, 0

    n = len(years)
    sum_x = sum(years)
    sum_y = sum(values)
    sum_xy = sum(x * y for x, y in zip(years, values))
    sum_x2 = sum(x * x for x in years)

    slope = (
        (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        if (n * sum_x2 - sum_x * sum_x) != 0
        else 0
    )

    weighted_avg_year = (
        sum(y * w for y, w in zip(years, values)) / sum(values)
        if sum(values) > 0
        else 0
    )

    recent_years = years[-3:]
    recent_demand = sum(yearly_counts.get(y, 0) for y in recent_years)
    total_demand = sum(values)
    recent_ratio = recent_demand / total_demand if total_demand > 0 else 0

    return slope, weighted_avg_year, recent_ratio


st.title("✈️ AOG 零件维修资源规划系统")
st.markdown("---")

if "data_loaded" not in st.session_state:
    aog_df, zsht_df, new_aog_df = load_data()
    st.session_state.aog_df = aog_df
    st.session_state.zsht_df = zsht_df
    st.session_state.new_aog_df = new_aog_df
    st.session_state.get_monthly_data = get_monthly_data
    st.session_state.get_yearly_data = get_yearly_data
    st.session_state.get_monthly_data_by_year = get_monthly_data_by_year
    st.session_state.calculate_cv = calculate_cv
    st.session_state.calculate_trend = calculate_trend
    st.session_state.data_loaded = True

st.info("请使用左侧导航栏选择查看 **按零件号** 或 **按功能ID** 分析页面")
