import streamlit as st
import pandas as pd
import plotly.express as px
import re
import pycountry

# ===== 페이지 설정 =====
st.set_page_config(
    page_title="CO₂ 배출량 Top 10 시각화",
    layout="wide",
    page_icon="🌍"
)

st.title("🌍 연도별 CO₂ 배출량 상위 10개국 분석")

# ===== CSV 파일 로드 =====
csv_file = "CO2_Emissions_1960-2018.csv"

try:
    df = pd.read_csv(csv_file, header=0)
except FileNotFoundError:
    st.error(f"❌ 데이터 파일이 존재하지 않습니다: `{csv_file}`")
    st.stop()

# ===== 연도 컬럼 자동 감지 =====
year_cols = [col for col in df.columns if re.fullmatch(r"\d{4}", str(col).strip())]
if not year_cols:
    st.warning("⚠️ '1960', '1970' 같은 연도 형식의 컬럼이 없습니다.")
    st.stop()

# ===== ISO Alpha-3 국가 코드 자동 생성 =====
def get_country_code(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None

df["Country Code"] = df["Country Name"].apply(get_country_code)

# ===== 사용자 인터페이스 =====
st.markdown("### ✅ 연도 선택")

col_left, col_right = st.columns([3, 1])

with col_left:
    year_list = sorted(map(int, year_cols))
    selected_year = st.selectbox("📅 분석할 연도 선택", year_list, index=year_list.index(2018))
    year_col = str(selected_year)

    # ===== 상위 10개 국가 추출 =====
    data_filtered = df[["Country Name", "Country Code", year_col]].dropna(subset=[year_col])
    top10 = data_filtered.sort_values(by=year_col, ascending=False).head(10)

    # ===== 표 출력 =====
    st.markdown(f"### 🌐 {selected_year}년 CO₂ 배출량 Top 10 국가")
    st.dataframe(top10.rename(columns={year_col: "CO₂ 배출량"}), use_container_width=True)

    # ===== 선형 그래프 =====
    fig = px.line(
        top10,
        x="Country Name",
        y=year_col,
        markers=True,
        title=f"📈 {selected_year}년 CO₂ 배출량 Top 10 (선형 그래프)",
        labels={year_col: "CO₂ 배출량 (톤)", "Country Name": "국가"},
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # ===== 지도 시각화 =====
    st.markdown("### 🗺️ Top 10 국가별 CO₂ 배출량 (지도)")
    map_fig = px.scatter_geo(
        top10,
        locations="Country Code",
        color="Country Name",
        size=year_col,
        hover_name="Country Name",
        size_max=60,
        projection="natural earth",
        title=f"🗺️ {selected_year}년 CO₂ 배출량 Top 10 지도 시각화",
        labels={year_col: "CO₂ 배출량"}
    )
    st.plotly_chart(map_fig, use_container_width=True)

with col_right:
    st.markdown("### 📘 설명")
    st.markdown(f"""
    - 이 시각화는 **{selected_year}년**의 이산화탄소(CO₂) 배출 데이터를 기반으로 합니다.
    - **상위 10개국의 배출량**을 표, 선형 그래프, 그리고 세계 지도 위에서 시각화합니다.
    - 지도에서는 각 국가의 위치에 마커가 표시되며, 마우스를 올리면 **국가명과 배출량**이 표시됩니다.
    - 데이터는 **톤(t)** 단위입니다.

    ---
    **카타르(Qatar)의 높은 배출량 이유**  
    ▸ LNG 산업 중심, 인구는 적지만 산업용 에너지 소비가 높음  
    ▸ 여름 냉방 수요와 교통 의존도 큼  
    ▸ 재생에너지 비중 낮고 화석연료 의존도가 큼

    ℹ️ 데이터 출처: World Bank, IEA, Global Carbon Project
    """)
