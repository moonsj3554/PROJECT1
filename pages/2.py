import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # CSV 파일 로드 시 예외 처리
    try:
        df = pd.read_csv("CO2_Emissions_1960-2018.csv", header=1)
    except FileNotFoundError:
        st.error("❌ 'CO2_Emissions.csv' 파일을 찾을 수 없습니다.")
        return pd.DataFrame(), []

    # 연도 컬럼만 추출 (컬럼명이 숫자인 경우)
    year_cols = [col for col in df.columns if str(col).isdigit()]

    # 연도 컬럼이 없을 경우 경고
    if not year_cols:
        st.warning("⚠️ 연도 형식의 컬럼이 없습니다. CSV 구조를 확인하세요.")
        return df.reset_index(), []

    # 정수형으로 변환 시도 (예: "1960" → 1960)
    try:
        year_list = list(map(int, year_cols))
    except ValueError as e:
        st.error(f"❌ 연도 컬럼을 정수형으로 변환하는 중 오류 발생: {e}")
        return df.reset_index(), []

    return df.reset_index(), year_list


# 아래는 메인 실행 부분 예시
df, available_years = load_data()

if not df.empty:
    st.write("✅ 데이터 로드 성공")
    st.write("사용 가능한 연도 목록:", available_years)
    st.dataframe(df.head())
