import requests
import pandas as pd
from io import BytesIO
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")

    chrome_options.binary_location = '/usr/bin/google-chrome'
    service = Service('/usr/bin/chromedriver')

    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_nxt_data():
    driver = create_driver()
    url = "https://www.nextrade.co.kr/menu/transactionStatusMain/menuList.do"
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    data = []
    rows = soup.select("table tr")
    now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 8:
            continue
        if any(not col.text.strip() for col in cols[:8]):
            continue
        stock_code = cols[0].text.strip().lstrip('A')
        stock_name = cols[1].text.strip()
        try:
            current_price = int(cols[3].text.replace(',', '') or 0)
            volume = int(cols[9].text.replace(',', '') or 0)
            trade = int(cols[10].text.replace(',', '') or 0)
        except ValueError:
            continue
        data.append([stock_code, stock_name, current_price, volume, trade, now_time])

    df = pd.DataFrame(data, columns=["종목코드", "종목명", "NXT 현재가", "NXT 거래량", "NXT 거래대금", "기준시간"])
    return df

def get_krx_data(input_date):
    gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
    headers = {
        'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    gen_otp_data = {
        'locale': 'ko_KR',
        'mktId': 'ALL',
        'trdDd': input_date,
        'share': '1',
        'money': '1',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT01501'
    }

    otp = requests.post(gen_otp_url, data=gen_otp_data, headers=headers).text
    down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
    down_res = requests.post(down_url, data={'code': otp}, headers=headers)

    df_krx = pd.read_csv(BytesIO(down_res.content), encoding='EUC-KR')
    df_krx['시장구분'] = df_krx['시장구분'].replace('KOSDAQ GLOBAL', 'KOSDAQ')
    if '단축코드' in df_krx.columns:
        df_krx = df_krx.rename(columns={'단축코드': '종목코드'})

    cols_needed = ['종목코드', '시장구분', '종가', '거래량', '거래대금']
    df_krx = df_krx[[c for c in cols_needed if c in df_krx.columns]]

    df_krx = df_krx.rename(columns={
        '종가': 'KRX 현재가',
        '거래량': 'KRX 거래량',
        '거래대금': 'KRX 거래대금'
    })

    return df_krx

def merge_data():
    today = datetime.today().strftime('%Y%m%d')
    now_time = datetime.now().strftime('%Y.%m.%d, %H:%M분 기준')

    nxt_df = get_nxt_data()
    krx_df = get_krx_data(today)

    merged_df = pd.merge(nxt_df, krx_df, on="종목코드", how="inner")

    merged_df["KRX 대비 NXT 거래량 비중"] = (merged_df["NXT 거래량"] / merged_df["KRX 거래량"]) * 100
    merged_df["KRX 대비 NXT 거래량 비중"] = merged_df["KRX 대비 NXT 거래량 비중"].round(2)

    merged_df["기준시간"] = now_time

    return merged_df, today
