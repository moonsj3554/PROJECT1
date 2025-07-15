import streamlit as st
import pandas as pd
import re

# ===== 📁 CSV 로딩 =====
csv_file = "CO2_Emissions_1960-2018.csv"

# 1. header=0로 시도
try:
    df = pd.read_csv(csv_file, header=0)
except FileNotFoundError:
    st.error(f"❌ '{csv_file}' 파일을 찾을 수 없습니다.")
    st.stop()

# 2. 컬럼 확인
st.write("🧾 CSV 컬럼명 확인:", df.columns.tolist())

# 3. 연도 형식의 컬럼 자동 감지 (공백 제거 + 정규식)
year_cols = [col for col in df.columns if re.fullmatch(r"\d{4}", str(col).strip())]

if not year_cols:
    st.warning("⚠️ '1960', '1970' 같은 연도 컬럼을 찾을 수 없습니다. 위의 컬럼명을 참고하세요.")
    st.stop()

# 연도 선택
year_list = sorted(map(int, year_cols))
selected_year = st.selectbox("📅 연도를 선택하세요", year_list)

# 선택된 연도 기준 정렬
year_col = str(selected_year)

top10 = df[["Country Name", year_col]].dropna(subset=[year_col])
top10 = top10.sort_values(by=year_col, ascending=False).head(10)

# 출력
st.subheader(f"🌍 {selected_year}년 CO₂ 배출량 Top 10")
st.dataframe(top10.rename(columns={year_col: "CO₂ 배출량"}))
st.bar_chart(top10.set_index("Country Name"))
