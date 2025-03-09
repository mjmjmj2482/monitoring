import pandas as pd
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_nxt_data():
    # 크롬 드라이버 실행
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 브라우저 없이 실행
    driver = webdriver.Chrome(service=service, options=options)

    # NXT 거래현황 페이지 접속
    url = "https://www.nextrade.co.kr/menu/transactionStatusMain/menuList.do"
    driver.get(url)
    time.sleep(5)  # 데이터 로딩 대기

    # 데이터 크롤링 (예: 테이블에서 정보 가져오기)
    data = []
    rows = driver.find_elements("xpath", "//table[@id='trade1']/tbody/tr")

    for row in rows:
        cols = row.find_elements("tag name", "td")
        if cols:
            data.append([col.text for col in cols])

    driver.quit()

    # 데이터프레임 생성
    df = pd.DataFrame(data, columns=["종목코드", "종목명", "현재가", "거래량", "거래대금"])
    
    # 데이터 변환 (숫자형 데이터 변환)
    for col in ["현재가", "거래량", "거래대금"]:
        df[col] = df[col].str.replace(",", "").astype(float)

    # 데이터 저장 (CSV)
    today = datetime.today().strftime("%Y-%m-%d")
    filename = f"nxt_data_{today}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    
    return filename, df

if __name__ == "__main__":
    filename, df = get_nxt_data()
    print(f"✅ 데이터 저장 완료: {filename}")
