import streamlit as st
import pandas as pd

# 📌 CSV 파일 직접 로딩 (load_data 함수 없이!)
csv_file = "CO2_Emissions_1960-2018.csv"

try:
    df = pd.read_csv(csv_file, header=1)
except FileNotFoundError:
    st.error(f"❌ '{csv_file}' 파일을 찾을 수 없습니다. 파일 경로를 확인하세요.")
    st.stop()

# 📌 연도 컬럼만 추출
year_cols = [col for col in df.columns if str(col).isdigit()]
if not year_cols:
    st.warning("⚠️ 연도 형식의 컬럼이 없습니다. CSV 파일 구조를 확인하세요.")
    st.stop()

# ✅ 사용자에게 연도 선택 UI 제공
year_list = sorted(map(int, year_cols))
selected_year = st.selectbox("📅 연도를 선택하세요", year_list)

# ✅ 선택된 연도 기준 상위 10개 국가 추출
year_col = str(selected_year)

if year_col not in df.columns:
    st.warning(f"선택한 연도 '{year_col}'에 해당하는 데이터가 없습니다.")
    st.stop()

# 결측값 제거 후 상위 10개 추출
top10 = df[["Country Name", year_col]].dropna(subset=[year_col])
top10 = top10.sort_values(by=year_col, ascending=False).head(10)

# ✅ 결과 출력
st.subheader(f"🌍 {selected_year}년 국가별 CO₂ 배출량 Top 10")
st.dataframe(top10.rename(columns={year_col: "CO₂ 배출량"}))

# ✅ 시각화 (bar chart)
st.bar_chart(top10.set_index("Country Name"))
