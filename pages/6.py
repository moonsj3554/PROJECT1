import streamlit as st
import pandas as pd
import plotly.express as px
import re

# ===== CSV 파일 로드 =====
csv_file = "CO2_Emissions_1960-2018.csv"

try:
    df = pd.read_csv(csv_file, header=0)
except FileNotFoundError:
    st.error(f"❌ '{csv_file}' 파일이 없습니다.")
    st.stop()

# ===== 연도 컬럼 자동 감지 =====
year_cols = [col for col in df.columns if re.fullmatch(r"\d{4}", str(col).strip())]
if not year_cols:
    st.warning("⚠️ '1960', '1970' 같은 연도 컬럼이 없습니다.")
    st.stop()

# ===== 연도 선택 UI =====
year_list = sorted(map(int, year_cols))
selected_year = st.selectbox("📅 연도를 선택하세요", year_list)
year_col = str(selected_year)

# ===== 상위 10개 국가 추출 =====
top10 = df[["Country Name", year_col]].dropna(subset=[year_col])
top10 = top10.sort_values(by=year_col, ascending=False).head(10)

# ===== 표 출력 =====
st.subheader(f"🌍 {selected_year}년 CO₂ 배출량 Top 10")
st.dataframe(top10.rename(columns={year_col: "CO₂ 배출량"}))

# ===== Plotly 선형 그래프 =====
fig = px.line(
    top10,
    x="Country Name",
    y=year_col,
    markers=True,
    title=f"{selected_year}년 국가별 CO₂ 배출량 (선형 그래프)",
    labels={year_col: "CO₂ 배출량", "Country Name": "국가"}
)
st.plotly_chart(fig, use_container_width=True)
