import streamlit as st
import pandas as pd
from data_collector import merge_data
from io import BytesIO

st.set_page_config(page_title="NXT vs KRX 비교", layout="wide")

st.title("📊 KRX vs NXT 거래 데이터 비교")

# 🔄 데이터 새로고침 버튼 (Streamlit에서 직접 크롤링 실행)
if st.button("🔄 데이터 업데이트 실행"):
    with st.spinner('📡 데이터 수집 및 병합 중...'):
        merged_df, today = merge_data()
        merged_df.to_csv("data.csv", index=False)  # 최신 데이터 저장
    st.success("✅ 데이터가 성공적으로 업데이트되었습니다!")
    st.rerun()

# 🔍 기존 저장된 데이터 로드
try:
    merged_df = pd.read_csv("data.csv")
    st.dataframe(merged_df, use_container_width=True)
except FileNotFoundError:
    st.error("⚠️ 데이터 파일이 없습니다. 먼저 '데이터 업데이트 실행' 버튼을 눌러주세요.")

# 📊 요약 정보 계산
total_nxt_volume = merged_df["NXT 거래량"].astype(float).sum()
total_krx_volume = merged_df["KRX 거래량"].astype(float).sum()
total_nxt_trade = merged_df["NXT 거래대금"].astype(float).sum()

krx_vs_nxt_ratio = round((total_nxt_volume / total_krx_volume) * 100, 1) if total_krx_volume > 0 else 0
total_market_ratio = round((total_nxt_volume / (total_nxt_volume + total_krx_volume)) * 100, 1)
krx_revenue_loss = round(total_nxt_trade * 0.0022763 * 0.01 * 2)
ats_revenue_gain = round(krx_revenue_loss * 0.7)

st.subheader("📋 요약 정보")
col1, col2 = st.columns(2)

with col1:
    st.write("##### 📊 거래량 및 비중 요약")
    st.table(pd.DataFrame({
        "항목": ["기준시간", "NXT 거래량 총합", "KRX 거래량 총합",
                "KRX 대비 NXT 거래량 비중", "전체시장 대비 NXT 거래량 비중"],
        "값": [merged_df['기준시간'].iloc[0], f'{total_nxt_volume:,.0f}', f'{total_krx_volume:,.0f}',
               f'{krx_vs_nxt_ratio}%', f'{total_market_ratio}%']
    }))

with col2:
    st.write("##### 💰 거래대금 및 수익 요약")
    st.table(pd.DataFrame({
        "항목": ["NXT 총 거래대금", "KRX 수익 감소분", "ATS 수익 증가분"],
        "값": [f'{total_nxt_trade:,.0f}', f'{krx_revenue_loss:,.0f}', f'{ats_revenue_gain:,.0f}']
    }))

# 📥 엑셀 다운로드 기능 추가
@st.cache_data
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='데이터')
    return output.getvalue()

st.download_button(
    label="📥 엑셀 다운로드",
    data=convert_df_to_excel(merged_df),
    file_name=f"KRX_NXT_merged_{today}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
