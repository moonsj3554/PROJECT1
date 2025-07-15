import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="CO₂ 배출량 시각화", layout="wide")

st.title("🌍 국가별 이산화탄소 배출량 (1960-2018)")

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("CO2_Emissions_1960-2018.csv")
    return df

df = load_data()
country_col = "Country Name"
year_cols = [col for col in df.columns if col.isdigit()]
year_ints = list(map(int, year_cols))

# 🎛️ 사용자 입력
st.markdown("### ✅ 국가 및 연도 범위 선택")

selected_countries = st.multiselect("🌐 국가 선택", df[country_col].unique(), default=["Korea, Rep.", "Qatar", "United States"])

start_year, end_year = st.slider("📅 연도 범위 선택", min_value=min(year_ints), max_value=max(year_ints),
                                 value=(1990, 2018), step=1)

# 연도 범위 필터링
selected_years = [str(y) for y in range(start_year, end_year + 1)]
filtered_df = df[df[country_col].isin(selected_countries)][[country_col] + selected_years]

# 데이터 전처리
melted_df = filtered_df.melt(id_vars=country_col, var_name="Year", value_name="CO2 Emissions")
melted_df.dropna(subset=["CO2 Emissions"], inplace=True)
melted_df["Year"] = melted_df["Year"].astype(int)

# 📊 CO₂ 배출량 변화 그래프
left_col, right_col = st.columns([3, 1])

with left_col:
    st.markdown("### 📈 CO₂ 배출량 변화 그래프 (선형)")
    fig = px.line(melted_df,
                  x="Year",
                  y="CO2 Emissions",
                  color=country_col,
                  markers=True,
                  title="📈 선택한 국가들의 연도별 이산화탄소 배출량",
                  labels={"CO2 Emissions": "이산화탄소 배출량 (톤)"},
                  height=600)
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.markdown("### 📘 설명")
    st.markdown("""
    이 대시보드는 **1960년부터 2018년까지** 국가별 이산화탄소(CO₂) 배출량을 시각화한 것입니다.

    - 선택한 국가들의 연도별 CO₂ 배출량을 선형 그래프로 비교할 수 있어요.
    - 배출량 데이터는 **톤(t)** 단위로 제공됩니다.
    - 슬라이더를 통해 분석 연도 범위를 자유롭게 조절할 수 있어요.
    - 선형그래프는 **국가별 추세선**을 나타내는 데 유용합니다.

    ---

    ### 🔎 왜 카타르(Qatar)의 배출량이 높은가요?

    - **액화천연가스(LNG)** 생산 및 수출 중심의 에너지 구조
    - 인구는 적지만 산업 규모가 크고, **1인당 에너지 소비량이 세계 최고 수준**
    - 여름철 **냉방, 교통 등 에너지 소비가 매우 큼**
    - 재생에너지 비중이 낮고 **화석연료 중심의 경제 구조**

    👉 이런 이유로 카타르는 **국가별 CO₂ 배출량 세계 최고 수준**입니다.
    """)

# ✅ 국가별 합계 & 평균 계산
summary_df = melted_df.groupby(country_col)["CO2 Emissions"].agg(["sum", "mean"]).reset_index()
summary_df.columns = ["국가", "배출량 합계 (톤)", "연평균 배출량 (톤)"]
summary_df = summary_df.sort_values(by="배출량 합계 (톤)", ascending=False)

st.markdown("---")

# 📋 상세 데이터 테이블
if st.checkbox("📋 상세 데이터 테이블 보기"):
    st.markdown("#### 🔍 필터링된 상세 데이터 테이블")
    filter_countries_data = st.multiselect("🔎 국가 선택 (테이블 필터)", melted_df[country_col].unique(),
                                           default=selected_countries)
    filtered_data_table = melted_df[melted_df[country_col].isin(filter_countries_data)]
    st.dataframe(filtered_data_table)

# 📈 국가별 배출량 요약 (테이블 + 그래프)
if st.checkbox("📈 국가별 배출량 합계 및 평균 보기"):
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("#### 📊 국가별 이산화탄소 배출량 요약")
        filter_countries_summary = st.multiselect("🔎 국가 선택 (요약 필터)", summary_df["국가"].unique(),
                                                  default=selected_countries)
        filtered_summary_table = summary_df[summary_df["국가"].isin(filter_countries_summary)]
        st.dataframe(filtered_summary_table, use_container_width=True)

        # 📉 배출량 합계 그래프
        st.markdown("#### 📈 국가별 CO₂ 배출량 **합계** 그래프")
        fig_sum = px.line(
            filtered_summary_table,
            x="국가",
            y="배출량 합계 (톤)",
            markers=True,
            title="국가별 CO₂ 배출량 합계",
            labels={"배출량 합계 (톤)": "배출량 합계 (톤)", "국가": "Country"},
            height=450
        )
        st.plotly_chart(fig_sum, use_container_width=True)

        # 📉 연평균 배출량 그래프
        st.markdown("#### 📈 국가별 CO₂ 배출량 **연평균** 그래프")
        fig_mean = px.line(
            filtered_summary_table,
            x="국가",
            y="연평균 배출량 (톤)",
            markers=True,
            title="국가별 CO₂ 배출량 연평균",
            labels={"연평균 배출량 (톤)": "연평균 배출량 (톤)", "국가": "Country"},
            height=450
        )
        st.plotly_chart(fig_mean, use_container_width=True)

    with col2:
        st.markdown("### 📘 설명")
        st.markdown("""
        - 이 섹션에서는 선택한 국가들의 **총 배출량**과 **연평균 배출량**을 비교합니다.
        - **배출량 합계 그래프**는 해당 기간 동안 각 국가가 배출한 CO₂의 총량을 보여줍니다.
        - **연평균 배출량 그래프**는 국가별로 평균적으로 얼마나 많은 CO₂를 매년 배출했는지를 나타냅니다.
        - 이 두 그래프를 통해 국가별 배출 규모뿐만 아니라 **지속적인 배출 패턴**도 비교할 수 있습니다.
        """)
