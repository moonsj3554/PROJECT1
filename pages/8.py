import streamlit as st
import pandas as pd
import plotly.express as px
import re

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

# ===== 간단한 대륙 매핑 (수동) =====
continent_dict = {
    "China": "Asia",
    "India": "Asia",
    "Japan": "Asia",
    "Korea, Rep.": "Asia",
    "Indonesia": "Asia",
    "Saudi Arabia": "Asia",
    "Iran, Islamic Rep.": "Asia",
    "United States": "North America",
    "Canada": "North America",
    "Mexico": "North America",
    "Brazil": "South America",
    "Argentina": "South America",
    "Germany": "Europe",
    "United Kingdom": "Europe",
    "France": "Europe",
    "Italy": "Europe",
    "Russian Federation": "Europe",
    "South Africa": "Africa",
    "Nigeria": "Africa",
    "Egypt, Arab Rep.": "Africa",
    "Australia": "Oceania",
    "Qatar": "Asia",
    "United Arab Emirates": "Asia",
    "Turkey": "Europe"
}

df["Continent"] = df["Country Name"].map(continent_dict)
df["Continent"].fillna("Other", inplace=True)

# ===== 사용자 인터페이스 =====
st.markdown("### ✅ 대륙 및 연도 선택")

col_left, col_right = st.columns([3, 1])

with col_left:
    continent_options = df["Continent"].unique().tolist()
    continent_options.sort()
    selected_continent = st.selectbox("🌐 대륙 선택", ["All"] + continent_options)

    year_list = sorted(map(int, year_cols))
    selected_year = st.selectbox("📅 분석할 연도 선택", year_list, index=year_list.index(2018))
    year_col = str(selected_year)

    # ===== 대륙 필터링 =====
    if selected_continent == "All":
        data_filtered = df[["Country Name", "Continent", year_col]].dropna(subset=[year_col])
    else:
        data_filtered = df[df["Continent"] == selected_continent][["Country Name", "Continent", year_col]].dropna(subset=[year_col])

    # ===== 상위 10개 국가 추출 =====
    top10 = data_filtered.sort_values(by=year_col, ascending=False).head(10)

    # ===== 표 출력 =====
    st.markdown(f"### 🌐 {selected_year}년 {selected_continent if selected_continent != 'All' else '전체 세계'} CO₂ 배출량 Top 10")
    st.dataframe(top10.rename(columns={year_col: "CO₂ 배출량"}), use_container_width=True)

    # ===== 선형 그래프 =====
    fig = px.line(
        top10,
        x="Country Name",
        y=year_col,
        markers=True,
        title=f"📈 {selected_year}년 {selected_continent if selected_continent != 'All' else '세계'} CO₂ 배출량 Top 10",
        labels={year_col: "CO₂ 배출량 (톤)", "Country Name": "국가"},
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### 📘 설명")
    st.markdown(f"""
    - 이 시각화는 **{selected_year}년**의 이산화탄소(CO₂) 배출 데이터를 기반으로 합니다.
    - 선택한 대륙: `{selected_continent}`  
    - **상위 10개국의 배출량**을 표와 그래프로 함께 제공합니다.
    - 데이터는 **톤(t)** 단위이며, 시계열 분석이 아닌 **특정 시점 비교**에 적합합니다.

    ---
    **카타르(Qatar)의 높은 배출량 이유**  
    ▸ LNG 산업 중심, 인구는 적지만 산업용 에너지 소비가 높음  
    ▸ 여름 냉방 수요와 교통 의존도 큼  
    ▸ 재생에너지 비중 낮고 화석연료 의존도가 큼

    ℹ️ 데이터 출처: World Bank, IEA, Global Carbon Project
    """)
