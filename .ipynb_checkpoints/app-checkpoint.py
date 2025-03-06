import streamlit as st
import pandas as pd
from data_collector import merge_data

st.set_page_config(page_title="NXT vs KRX 비교", layout="wide")

st.title("📊 NXT vs KRX 거래 데이터 비교")

with st.spinner('데이터 수집 및 병합 중...'):
    merged_df, today = merge_data()

# 1000단위 콤마 적용
for col in ["NXT 현재가", "NXT 거래량", "NXT 거래대금", "KRX 현재가", "KRX 거래량", "KRX 거래대금"]:
    merged_df[col] = merged_df[col].apply(lambda x: f'{x:,}')

st.dataframe(merged_df)

total_nxt_volume = merged_df["NXT 거래량"].str.replace(',', '').astype(float).fillna(0).sum()
total_krx_volume = merged_df["KRX 거래량"].str.replace(',', '').astype(float).fillna(0).sum()
total_nxt_trade = merged_df["NXT 거래대금"].str.replace(',', '').astype(float).fillna(0).sum()

krx_vs_nxt_ratio = round((total_nxt_volume / total_krx_volume) * 100, 1) if total_krx_volume > 0 else 0
total_market_ratio = round((total_nxt_volume / (total_nxt_volume + total_krx_volume)) * 100, 1)

krx_revenue_loss = round(total_nxt_trade * 0.0022763 * 0.01 * 2)
ats_revenue_gain = round(krx_revenue_loss * 0.7)

st.subheader("📋 요약 정보")
st.write(f"**기준시간:** {merged_df['기준시간'].iloc[0]}")
st.write(f"**NXT 거래량 총합:** {total_nxt_volume:,.0f}")
st.write(f"**KRX 거래량 총합:** {total_krx_volume:,.0f}")
st.write(f"**KRX 대비 NXT 거래량 비중:** {krx_vs_nxt_ratio}%")
st.write(f"**전체시장 대비 NXT 거래량 비중:** {total_market_ratio}%")
st.write(f"**NXT 총 거래대금:** {total_nxt_trade:,.0f}")
st.write(f"**KRX 수익 감소분:** {krx_revenue_loss:,.0f}")
st.write(f"**ATS 수익 증가분:** {ats_revenue_gain:,.0f}")

if st.button("엑셀로 저장"):
    file_name = f"KRX_NXT_merged_{today}.xlsx"
    merged_df.to_excel(file_name, index=False)
    st.success(f"엑셀 저장 완료: {file_name}")
