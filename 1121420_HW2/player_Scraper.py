import time
import pandas as pd
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import utils

def scrape_player_pages(driver, year, stat_type, tab):
    """處理球員特有的多頁面抓取邏輯"""
    print(f"    -> 準備抓取球員 {tab} 表格...")
    base_url = f"https://www.mlb.com/stats/player/{stat_type}?year={year}"
    driver.get(base_url)
    wait = WebDriverWait(driver, 15)
    
    try:
        if tab.lower() == "expanded":
            expanded_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Expanded')]")))
            driver.execute_script("arguments[0].click();", expanded_tab)
            time.sleep(2)
    except TimeoutException:
        print(f"      [警告] 找不到 {tab} 標籤。")
        return pd.DataFrame()

    all_pages_data = []
    page_num = 1
    
    while True:
        print(f"      正在擷取第 {page_num} 頁...")
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
            time.sleep(1)
        except TimeoutException:
            break
            
        df = utils.extract_table_from_page(driver)
        if not df.empty:
            all_pages_data.append(df)
            
        try:
            # 尋找下一頁按鈕
            next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='next page button']")
            if not next_btn.is_enabled():
                break # 按鈕被 disabled，代表是最後一頁
            driver.execute_script("arguments[0].click();", next_btn)
            page_num += 1
        except NoSuchElementException:
            break

    return pd.concat(all_pages_data, ignore_index=True) if all_pages_data else pd.DataFrame()

def run(years):
    """執行球員資料的爬取與合併"""
    driver = utils.init_driver()
    tasks = ["hitting", "pitching"]

    save_dir = r"D:\Big_data_Science\1121420_HW2"
    try:
        for stat in tasks:

            out_file = f"mlb_player_{stat}_{years[0]}_{years[-1]}.csv"
            out_file = os.path.join(save_dir, out_file)
            print(f"\n========== [球員任務] 開始處理: {stat.upper()} ==========")
            final_data = []
            
            for year in years:
                print(f"【球員 - 年份: {year}】")
                df_std = scrape_player_pages(driver, year, stat, "standard")
                df_exp = scrape_player_pages(driver, year, stat, "expanded")
                
                if df_std.empty or df_exp.empty:
                    continue

                try:
                    # 球員的合併 Key 是 'PLAYER'
                    df_merged = pd.merge(df_std, df_exp, on='PLAYER', how='inner', suffixes=('', '_expanded'))
                    df_merged.insert(0, 'YEAR', year)
                    final_data.append(df_merged)
                    print(f"      => {year} 年球員 {stat} 合併成功！共 {len(df_merged)} 筆。")
                except KeyError:
                    print(f"      [錯誤] 找不到 'PLAYER' 欄位，請檢查擷取狀況。")

            if final_data:
                pd.concat(final_data, ignore_index=True).to_csv(out_file, index=False, encoding='utf-8-sig')
                print(f"★★★ 已產出檔案: {out_file} ★★★")
    finally:
        driver.quit()