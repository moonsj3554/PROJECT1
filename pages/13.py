import streamlit as st
import pandas as pd
import re
import pycountry
import folium
import json
import os
import requests
from streamlit_folium import st_folium

# ===== Streamlit 페이지 설정 =====
st.set_page_config(page_title="CO₂ 배출량 지도 시각화", layout="wide", page_icon="🗺️")
st.title("🗺️ 연도별 CO₂ 배출량 Top 10 (지도 기반 시각화)")

# ===== 파일 경로 설정 =====
csv_file = "CO2_Emissions_1960-2018.csv"
geojson_file = "world-countries.json"

# ===== 데이터 로딩 =====
try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    st.error(f"❌ 데이터 파일이 없습니다: `{csv_file}`")
    st.stop()

# ===== 연도 컬럼 감지 =====
year_cols = [col for col in df.columns if re.fullmatch(r"\d{4}", str(col).strip())]
if not year_cols:
    st.warning("⚠️ 연도 형식 컬럼(예: 1960, 1990 등)이 없습니다.")
    st.stop()

# ===== ISO Alpha-3 국가 코드 생성 =====
def get_country_code(name):
    manual = {
        "Korea, Rep.": "KOR",
        "Iran, Islamic Rep.": "IRN",
        "Egypt, Arab Rep.": "EGY",
        "Venezuela, RB": "VEN",
        "Russian Federation": "RUS",
        "Bahamas, The": "BHS",
        "Gambia, The": "GMB",
        "Yemen, Rep.": "YEM",
        "Congo, Dem. Rep.": "COD",
        "Congo, Rep.": "COG",
    }
    if name in manual:
        return manual[name]
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None

df["Country Code"] = df["Country Name"].apply(get_country_code)

# ===== 연도 선택 =====
year_list = sorted(map(int, year_cols))
selected_year = st.selectbox("📅 연도를 선택하세요", year_list, index=year_list.index(2018))
year_col = str(selected_year)

# ===== 상위 10개국 필터링 =====
data_filtered = df[["Country Name", "Country Code", year_col]].dropna(subset=[year_col])
top10 = data_filtered.sort_values(by=year_col, ascending=False).head(10)

# ===== GeoJSON 자동 다운로드 =====
def download_geojson_if_missing(file_path):
    if not os.path.exists(file_path):
        url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            st.success(f"✅ GeoJSON 파일 자동 다운로드 완료: `{file_path}`")
        except Exception as e:
            st.error(f"❌ GeoJSON 다운로드 실패: {e}")
            st.stop()

download_geojson_if_missing(geojson_file)

# ===== GeoJSON 로드 =====
with open(geojson_file, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# ===== 지도 데이터 매핑 =====
choropleth_df = top10.rename(columns={year_col: "CO2 Emissions"})
choropleth_df = choropleth_df[["Country Name", "CO2 Emissions"]]
name_to_value = dict(zip(choropleth_df["Country Name"], choropleth_df["CO2 Emissions"]))

for feature in geojson_data["features"]:
    cname = feature["properties"].get("name")
    feature["properties"]["co2"] = name_to_value.get(cname)

# ===== 지도 출력 (Folium 기반) =====
st.markdown("### 🗺️ 세계 지도에서 CO₂ 배출량 Top 10 보기")
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
        aliases=["국가", "CO₂ 배출량 (톤)"],
        localize=True
    )
).add_to(m)

st_folium(m, width=1000, height=600)
