import streamlit as st
import pandas as pd
from data_collector import merge_data
from io import BytesIO

st.set_page_config(page_title="NXT vs KRX 비교", layout="wide")

st.title("📊 KRX vs NXT 거래 데이터 비교")

if st.button("🔄 데이터 새로고침"):
    st.cache_data.clear()
    st.rerun()

with st.spinner('데이터 수집 및 병합 중...'):
    merged_df, today = merge_data()

# 1000단위 콤마 적용
for col in ["NXT 현재가", "NXT 거래량", "NXT 거래대금", "KRX 현재가", "KRX 거래량", "KRX 거래대금"]:
    merged_df[col] = merged_df[col].apply(lambda x: f'{x:,}')

st.dataframe(merged_df, use_container_width=True)

total_nxt_volume = merged_df["NXT 거래량"].str.replace(',', '').astype(float).sum()
total_krx_volume = merged_df["KRX 거래량"].str.replace(',', '').astype(float).sum()
total_nxt_trade = merged_df["NXT 거래대금"].str.replace(',', '').astype(float).sum()

krx_vs_nxt_ratio = round((total_nxt_volume / total_krx_volume) * 100, 1) if total_krx_volume > 0 else 0
total_market_ratio = round((total_nxt_volume / (total_nxt_volume + total_krx_volume)) * 100, 1)
krx_revenue_loss = round(total_nxt_trade * 0.0022763 * 0.01 * 2)
ats_revenue_gain = round(krx_revenue_loss * 0.7)

st.subheader("📋 요약 정보")

summary_data = {
    "항목": [
        "기준시간", "NXT 거래량 총합", "KRX 거래량 총합",
        "KRX 대비 NXT 거래량 비중", "전체시장 대비 NXT 거래량 비중",
        "NXT 총 거래대금", "KRX 수익 감소분", "ATS 수익 증가분"
    ],
    "값": [
        merged_df['기준시간'].iloc[0], f'{total_nxt_volume:,.0f}', f'{total_krx_volume:,.0f}',
        f'{krx_vs_nxt_ratio}%', f'{total_market_ratio}%',
        f'{total_nxt_trade:,.0f}', f'{krx_revenue_loss:,.0f}', f'{ats_revenue_gain:,.0f}'
    ]
}

st.table(pd.DataFrame(summary_data))

@st.cache_data
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='데이터')
        pd.DataFrame(summary_data).to_excel(writer, index=False, sheet_name='요약')
    return output.getvalue()

st.download_button(
    label="📥 엑셀 다운로드",
    data=convert_df_to_excel(merged_df),
    file_name=f"KRX_NXT_merged_{today}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
