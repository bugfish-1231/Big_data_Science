import pandas as pd
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def init_driver():
    """初始化 Selenium WebDriver，加入基礎防爬蟲設定"""
    options = Options()
    # options.add_argument("--headless") # 除錯完畢後可以取消註解，讓他在背景跑
    options.add_argument("--disable-notifications")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1280, 800)
    return driver

def extract_table_from_page(driver):
    """從當下的網頁原始碼中萃取出 DataFrame (處理 MLB 凍結窗格問題)"""
    html = driver.page_source
    tables = pd.read_html(StringIO(html))
    
    if len(tables) >= 2:
        # 將左側球員/球隊名稱欄與右側數據欄合併
        df = pd.concat([tables[0], tables[1]], axis=1)
    elif len(tables) == 1:
        df = tables[0]
    else:
        return pd.DataFrame()
    
    # 清除全空的列與欄
    df = df.dropna(axis=1, how='all').dropna(axis=0, how='all')
    return df