import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CO₂ 배출량 TOP 10", layout="wide")
st.title("🌍 연도별 국가 CO₂ 배출량 상위 10")

@st.cache_data
def load_data():
    df = pd.read_csv("CO2_Emissions_1960-2018.csv", header=1)
    df.columns = df.columns.astype(str)
    df = df.rename(columns={df.columns[0]: "Country"})
    df.set_index("Country", inplace=True)

    # 연도 컬럼만 정리 (숫자형으로 변환 가능한 열만 선택)
    year_cols = [col for col in df.columns if col.replace('.', '', 1).isdigit()]
    df = df[year_cols].apply(pd.to_numeric, errors="coerce")
    return df.reset_index()

df = load_data()

# 선택 가능한 연도 추출
available_years = [col for col in df.columns if col != "Country"]

# 연도 선택
selected_year = st.selectbox("연도를 선택하세요", sorted(available_years))

# 해당 연도의 상위 10개 국가 추출
top10 = df[["Country", selected_year]].dropna().sort_values(by=selected_year, ascending=False).head(10)

# Plotly 막대 그래프
fig = px.bar(
    top10,
    x="Country",
    y=selected_year,
    text=selected_year,
    title=f"{selected_year}년 CO₂ 배출량 상위 10개 국가",
    labels={selected_year: "CO₂ 배출량 (톤)", "Country": "국가"},
    color="Country"
)
fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

st.plotly_chart(fig, use_container_width=True)
