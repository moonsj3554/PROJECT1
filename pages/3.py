import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="국가별 CO₂ 배출량 시각화", layout="wide")
st.title("🌍 국가별 이산화탄소 배출량 시각화 (1960-2018)")

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("CO2_Emissions_1960-2018.csv")
    return df

df = load_data()
country_col = "Country Name"
year_cols = [col for col in df.columns if col.isdigit()]
year_ints = list(map(int, year_cols))

# 국가 선택 및 연도 범위 슬라이더
selected_countries = st.multiselect("국가 선택", df[country_col].unique(), default=["Korea, Rep.", "United States"])
start_year, end_year = st.slider("연도 범위 선택", min_value=min(year_ints), max_value=max(year_ints),
                                 value=(1990, 2018), step=1)

selected_years = [str(y) for y in range(start_year, end_year + 1)]
filtered_df = df[df[country_col].isin(selected_countries)][[country_col] + selected_years]

# melt로 long-form 변환
melted_df = filtered_df.melt(id_vars=country_col, var_name="Year", value_name="CO2 Emissions")
melted_df.dropna(subset=["CO2 Emissions"], inplace=True)
melted_df["Year"] = melted_df["Year"].astype(int)

# 📊 국가별 CO₂ 배출량 시각화
st.subheader("📈 선택한 국가의 연도별 CO₂ 배출량")
fig = px.bar(
    melted_df,
    x="Year",
    y="CO2 Emissions",
    color=country_col,
    barmode="group",
    title="선택한 국가들의 연도별 이산화탄소 배출량",
    labels={"CO2 Emissions": "이산화탄소 배출량 (톤)"},
    height=600
)
st.plotly_chart(fig, use_container_width=True)

# 📌 연도별 CO₂ 배출량 최고 국가 표시
st.subheader("🏆 연도별 CO₂ 배출량 최고 국가")

# 전체 데이터에서 연도별 최고 배출 국가 추출
global_df = df[[country_col] + selected_years]
melted_global = global_df.melt(id_vars=country_col, var_name="Year", value_name="CO2 Emissions")
melted_global.dropna(inplace=True)
melted_global["Year"] = melted_global["Year"].astype(int)

top_emitters = (
    melted_global.sort_values(["Year", "CO2 Emissions"], ascending=[True, False])
    .groupby("Year")
    .first()
    .reset_index()
)

st.dataframe(top_emitters, use_container_width=True)

# 시각화
fig_top = px.bar(
    top_emitters,
    x="Year",
    y="CO2 Emissions",
    text="Country Name",
    title="연도별 CO₂ 배출량 1위 국가",
    labels={"CO2 Emissions": "배출량 (톤)", "Country Name": "국가"},
    color="Country Name"
)
fig_top.update_traces(textposition="outside")
st.plotly_chart(fig_top, use_container_width=True)

# 📋 데이터 확인 옵션
if st.checkbox("🔍 선택한 국가의 데이터 테이블 보기"):
    st.dataframe(melted_df)
