import streamlit as st
import pandas as pd
import re

# ===== 📁 CSV 로딩 =====
csv_file = "CO2_Emissions_1960-2018.csv"

try:
    df = pd.read_csv(csv_file, header=1)
except FileNotFoundError:
    st.error(f"❌ '{csv_file}' 파일을 찾을 수 없습니다. 파일을 업로드했는지 확인하세요.")
    st.stop()

# ===== 🧠 연도 컬럼 자동 감지 =====
# 연도는 "1960", "1970" 등 4자리 숫자로만 구성된 컬럼
year_cols = [col for col in df.columns if re.fullmatch(r"\d{4}", str(col).strip())]

if not year_cols:
    st.warning("⚠️ '1960', '1970' 같은 연도 컬럼을 찾을 수 없습니다. CSV 파일 구조를 확인하세요.")
    st.stop()

# 연도 정렬
year_list = sorted(map(int, year_cols))

# ===== 📅 연도 선택 UI =====
selected_year = st.selectbox("📅 연도를 선택하세요", year_list)

# ===== 📊 상위 10개 국가 추출 =====
year_col = str(selected_year)

if year_col not in df.columns:
    st.warning(f"{selected_year}년 데이터가 없습니다.")
    st.stop()

top10 = df[["Country Name", year_col]].dropna(subset=[year_col])
top10 = top10.sort_values(by=year_col, ascending=False).head(10)

# ===== ✅ 결과 출력 =====
st.subheader(f"🌍 {selected_year}년 CO₂ 배출량 상위 10개 국가")
st.dataframe(top10.rename(columns={year_col: "CO₂ 배출량"}))

# ===== 📈 시각화 =====
st.bar_chart(top10.set_index("Country Name"))
