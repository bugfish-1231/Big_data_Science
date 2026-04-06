import time
import pandas as pd
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import utils

def scrape_team_single_page(driver, year, stat_type, tab):
    """處理球隊特有的單頁面抓取邏輯 (無須翻頁)"""
    print(f"    -> 準備抓取球隊 {tab} 表格...")
    base_url = f"https://www.mlb.com/stats/team/{stat_type}?year={year}"
    driver.get(base_url)
    wait = WebDriverWait(driver, 10)
    
    try:
        if tab.lower() == "expanded":
            expanded_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Expanded')]")))
            driver.execute_script("arguments[0].click();", expanded_tab)
            time.sleep(2)
            
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        time.sleep(1) # 緩衝渲染
        
        return utils.extract_table_from_page(driver)
        
    except TimeoutException:
        print(f"      [警告] 表格載入失敗。")
        return pd.DataFrame()

def run(years):
    """執行球隊資料的爬取與合併"""
    driver = utils.init_driver()
    tasks = ["hitting", "pitching"]

    save_dir = r"D:\Big_data_Science\1121420_HW2"
    
    try:
        for stat in tasks:
            out_file = f"mlb_team_{stat}_{years[0]}_{years[-1]}.csv"
            out_file = os.path.join(save_dir, out_file)
            print(f"\n========== [球隊任務] 開始處理: {stat.upper()} ==========")
            final_data = []
            
            for year in years:
                print(f"【球隊 - 年份: {year}】")
                df_std = scrape_team_single_page(driver, year, stat, "standard")
                df_exp = scrape_team_single_page(driver, year, stat, "expanded")
                
                if df_std.empty or df_exp.empty:
                    continue

                try:
                    # 球隊的合併 Key 是 'TEAM'
                    df_merged = pd.merge(df_std, df_exp, on='TEAM', how='inner', suffixes=('', '_expanded'))
                    df_merged.insert(0, 'YEAR', year)
                    final_data.append(df_merged)
                    print(f"      => {year} 年球隊 {stat} 合併成功！共 {len(df_merged)} 筆。")
                except KeyError:
                    print(f"      [錯誤] 找不到 'TEAM' 欄位，請檢查擷取狀況。")

            if final_data:
                pd.concat(final_data, ignore_index=True).to_csv(out_file, index=False, encoding='utf-8-sig')
                print(f"★★★ 已產出檔案: {out_file} ★★★")
    finally:
        driver.quit()