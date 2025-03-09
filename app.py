import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="NXT 거래 데이터 분석", layout="wide")

st.title("📊 KRX vs NXT 거래 데이터 분석")

# 최신 데이터 파일 찾기
files = [f for f in os.listdir() if f.startswith("nxt_data_") and f.endswith(".csv")]
if files:
    latest_file = max(files, key=os.path.getctime)  # 최신 파일 찾기
    df = pd.read_csv(latest_file)
    st.write(f"📅 최신 데이터: {latest_file}")

    # 데이터 1000단위 콤마 적용
    for col in ["현재가", "거래량", "거래대금"]:
        df[col] = df[col].apply(lambda x: f"{x:,.0f}")

    st.dataframe(df, use_container_width=True)

    # 🔹 요약 정보 계산
    total_volume = df["거래량"].str.replace(",", "").astype(float).sum()
    total_trade = df["거래대금"].str.replace(",", "").astype(float).sum()

    summary_data = {
        "항목": [
            "기준시간", "총 거래량", "총 거래대금"
        ],
        "값": [
            df["종목코드"].iloc[0],  # 첫 번째 종목 기준
            f"{total_volume:,.0f}",
            f"{total_trade:,.0f}"
        ]
    }

    st.subheader("📋 요약 정보")

    # 요약 정보 출력
    st.table(pd.DataFrame(summary_data))

    # 🔹 CSV 다운로드 버튼
    st.download_button(
        label="📥 CSV 다운로드",
        data=open(latest_file, "rb"),
        file_name=latest_file,
        mime="text/csv",
    )

else:
    st.warning("⚠️ 데이터 파일이 없습니다. 먼저 크롤링을 실행하세요.")
