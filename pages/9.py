import streamlit as st
import pandas as pd
import plotly.express as px
import re
import pycountry
import folium
import json
from streamlit_folium import st_folium

# ===== 페이지 설정 =====
st.set_page_config(
    page_title="CO₂ 배출량 Top 10 시각화",
    layout="wide",
    page_icon="🌍"
)

st.title("🌍 연도별 CO₂ 배출량 상위 10개국 분석")

# ===== CSV 파일 로드 =====
csv_file = "CO2_Emissions_1960-2018.csv"
geojson_file = "world-countries.json"  # 🌍 국가 경계 GeoJSON 파일 필요

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
    manual_corrections = {
        "Korea, Rep.": "KOR",
        "Egypt, Arab Rep.": "EGY",
        "Iran, Islamic Rep.": "IRN",
        "Venezuela, RB": "VEN",
        "Russian Federation": "RUS",
    }
    if name in manual_corrections:
        return manual_corrections[name]
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

    # ===== 지도 시각화 (Folium 기반 Choropleth) =====
    st.markdown("### 🗺️ Top 10 국가별 CO₂ 배출량 (Folium 지도)")

    # GeoJSON 파일 로드
    try:
        with open(geojson_file, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
    except FileNotFoundError:
        st.error(f"❌ 지도 데이터 파일이 존재하지 않습니다: `{geojson_file}`")
        st.stop()

    # Choropleth용 데이터프레임 준비
    choropleth_df = top10.rename(columns={year_col: "CO2 Emissions"})
    choropleth_df = choropleth_df[["Country Name", "CO2 Emissions"]]

    # GeoJSON feature에 CO2 값 매핑
    name_to_value = dict(zip(choropleth_df["Country Name"], choropleth_df["CO2 Emissions"]))
    for feature in geojson_data["features"]:
        cname = feature["properties"].get("name")
        feature["properties"]["co2"] = name_to_value.get(cname)

    # 지도 생성
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="cartodb positron")

    folium.Choropleth(
        geo_data=geojson_data,
        name="choropleth",
        data=choropleth_df,
        columns=["Country Name", "CO2 Emissions"],
        key_on="feature.properties.name",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="CO₂ 배출량 (톤)",
    ).add_to(m)

    folium.GeoJson(
        geojson_data,
        name="국가 정보",
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "co2"],
            aliases=["국가", "CO₂ 배출량"],
            localize=True
        )
    ).add_to(m)

    st_folium(m, width=800, height=500)

with col_right:
    st.markdown("### 📘 설명")
    st.markdown(f"""
    - 이 시각화는 **{selected_year}년**의 이산화탄소(CO₂) 배출 데이터를 기반으로 합니다.
    - **상위 10개국의 배출량**을 표, 선형 그래프, 그리고 Folium 지도로 시각화합니다.
    - 지도에서는 국가에 마우스를 올리면 **배출량**이 표시됩니다.
    - 색상이 진할수록 배출량이 높다는 의미입니다.

    ---
    **카타르(Qatar)의 높은 배출량 이유**  
    ▸ LNG 산업 중심, 인구는 적지만 산업용 에너지 소비가 높음  
    ▸ 여름 냉방 수요와 교통 의존도 큼  
    ▸ 재생에너지 비중 낮고 화석연료 의존도가 큼

    ℹ️ 데이터 출처: World Bank, IEA, Global Carbon Project
    """)
