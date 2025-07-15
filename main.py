import streamlit as st
import pandas as pd
import plotly.express as px

st.title("국가별 이산화탄소 배출량 시각화 (1960-2018)")

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("CO2_Emissions_1960-2018.csv")
    return df

df = load_data()
country_col = "Country Name"
year_cols = [col for col in df.columns if col.isdigit()]
year_ints = list(map(int, year_cols))

# 사용자 입력
selected_countries = st.multiselect("국가 선택", df[country_col].unique(), default=["Korea, Rep.", "United States"])
start_year, end_year = st.slider("연도 범위 선택", min_value=min(year_ints), max_value=max(year_ints),
                                 value=(1990, 2018), step=1)

# 연도 범위에 해당하는 열만 추출
selected_years = [str(y) for y in range(start_year, end_year + 1)]
filtered_df = df[df[country_col].isin(selected_countries)][[country_col] + selected_years]

# 데이터 전처리: melt로 long-form 변환
melted_df = filtered_df.melt(id_vars=country_col, var_name="Year", value_name="CO2 Emissions")
melted_df.dropna(subset=["CO2 Emissions"], inplace=True)
melted_df["Year"] = melted_df["Year"].astype(int)

# 그래프 그리기
fig = px.bar(melted_df,
             x="Year",
             y="CO2 Emissions",
             color=country_col,
             barmode="group",
             title="선택한 국가들의 연도별 이산화탄소 배출량",
             labels={"CO2 Emissions": "이산화탄소 배출량 (톤)"},
             height=600)

st.plotly_chart(fig, use_container_width=True)

# 데이터 확인 옵션
if st.checkbox("데이터 테이블 보기"):
    st.dataframe(melted_df)
