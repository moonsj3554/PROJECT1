import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CO₂ 배출량 시각화", layout="wide")

# 🔶 타이틀 & 설명 (마크다운 사용)
st.markdown("""
# 🌍 국가별 이산화탄소 배출량 분석 (1960-2018)

본 시각화 도구는 여러 국가의 이산화탄소(CO₂) 배출량을 비교할 수 있도록 만들어졌습니다.
선택한 국가들의 배출량을 연도별로 선형 그래프 혹은 막대그래프로 확인할 수 있습니다.

""")

# 📁 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("CO2_Emissions_1960-2018.csv")
    return df

df = load_data()
country_col = "Country Name"
year_cols = [col for col in df.columns if col.isdigit()]
year_ints = list(map(int, year_cols))

# 🎯 사용자 입력
st.markdown("### ✅ 국가 및 연도 범위 선택")
selected_countries = st.multiselect("국가 선택", df[country_col].unique(), default=["Korea, Rep.", "United States"])
start_year, end_year = st.slider("연도 범위 선택", min_value=min(year_ints), max_value=max(year_ints),
                                 value=(1990, 2018), step=1)

# 🎯 선택한 범위의 데이터 필터링
selected_years = [str(y) for y in range(start_year, end_year + 1)]
filtered_df = df[df[country_col].isin(selected_countries)][[country_col] + selected_years]

# 📊 데이터 전처리
melted_df = filtered_df.melt(id_vars=country_col, var_name="Year", value_name="CO2 Emissions")
melted_df.dropna(subset=["CO2 Emissions"], inplace=True)
melted_df["Year"] = melted_df["Year"].astype(int)

# 📈 그래프 그리기
st.markdown("### 📊 CO₂ 배출량 변화 그래프")
fig = px.bar(melted_df,
             x="Year",
             y="CO2 Emissions",
             color=country_col,
             barmode="group",
             title="연도별 이산화탄소 배출량 비교",
             labels={"CO2 Emissions": "이산화탄소 배출량 (톤)"},
             height=600)

st.plotly_chart(fig, use_container_width=True)

# 📄 데이터 테이블 확인
st.markdown("---")
if st.checkbox("📋 데이터 테이블 보기"):
    st.markdown("#### 🔍 상세 데이터")
    st.dataframe(melted_df)
