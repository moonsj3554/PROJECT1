import streamlit as st
import pandas as pd
import plotly.express as px
import re
import pycountry

# ===== 페이지 설정 =====
st.set_page_config(
    page_title="CO₂ 배출량 지도 시각화",
    layout="wide",
    page_icon="🗺️"
)

st.title("🗺️ 연도별 CO₂ 배출량 Top 10 (지도 시각화)")

# ===== CSV 파일 로드 =====
csv_file = "CO2_Emissions_1960-2018.csv"

try:
    df = pd.read_csv(csv_file, header=0)
except FileNotFoundError:
    st.error(f"❌ 데이터 파일이 존재하지 않습니다: `{csv_file}`")
    st.stop()

# ===== 연도 컬럼 감지 =====
year_cols = [col for col in df.columns if re.fullmatch(r"\d{4}", str(col).strip())]
if not year_cols:
    st.warning("⚠️ '1960', '1970' 같은 연도 형식의 컬럼이 없습니다.")
    st.stop()

# ===== ISO Alpha-3 국가 코드 생성 =====
def get_country_code(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None

df["Country Code"] = df["Country Name"].apply(get_country_code)

# ===== 연도 선택 및 Top 10 추출 =====
year_list = sorted(map(int, year_cols))
selected_year = st.selectbox("📅 연도를 선택하세요", year_list, index=year_list.index(2018))
year_col = str(selected_year)

data_filtered = df[["Country Name", "Country Code", year_col]].dropna(subset=[year_col])
top10 = data_filtered.sort_values(by=year_col, ascending=False).head(10)

# ===== 지도 시각화 =====
st.markdown("### 🌍 Top 10 국가별 CO₂ 배출량 (지도)")

map_fig = px.scatter_geo(
    top10,
    locations="Country Code",
    color="Country Name",
    size=year_col,
    hover_name="Country Name",
    size_max=60,
    projection="natural earth",
    title=f"🗺️ {selected_year}년 CO₂ 배출량 Top 10 지도 시각화",
    labels={year_col: "CO₂ 배출량 (톤)"}
)
st.plotly_chart(map_fig, use_container_width=True)
