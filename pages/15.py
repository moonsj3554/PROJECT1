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

# ===== 설명 추가 =====
with st.expander("▼ 전에 페이지 지도를 보기 쉽게 만든 지도", expanded=False):
    st.markdown("""
    이 지도는 상위 10개국의 이산화탄소 배출량을 **Plotly** 기반으로 시각화한 것입니다.  
    이전 페이지에서는 **Folium 기반 Choropleth 지도**로 표현하여 색상 농도에 따라 배출량을 구분했습니다.

    **🧭 두 지도 비교:**

    - **Plotly 지도**  
      ▸ 마커 크기와 색상으로 배출량 표현  
      ▸ 인터랙션 우수, 빠르게 시각화 가능

    - **Folium 지도**  
      ▸ 색상 농도로 지역 구분이 명확  
      ▸ 국경 단위 Choropleth 표현에 적합  

    필요에 따라 두 시각화 방식을 비교하여 활용할 수 있습니다.
    """)
