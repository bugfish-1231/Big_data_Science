import time
import pandas as pd
import os
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import utils

def scrape_team_single_page(driver, year, stat_type, tab):
    """處理球隊特有的單頁面抓取邏輯 (無須翻頁)"""
    print(f"    -> 準備抓取球隊 {tab} 表格 (年份: {year})...")
    
    # ⚾ 配合 MLB 最新網站架構，更改球隊的網址生成邏輯
    if stat_type == "hitting":
        # 球隊打擊網址結構：https://www.mlb.com/stats/team/2022
        base_url = f"https://www.mlb.com/stats/team/{year}" 
    else: 
        # 球隊投球網址結構：https://www.mlb.com/stats/team/pitching/2022
        base_url = f"https://www.mlb.com/stats/team/pitching/{year}"
        
    driver.get(base_url)
    time.sleep(3) 

    wait = WebDriverWait(driver, 15)
    
    try:
        if tab.lower() == "expanded":
            expanded_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Expanded']")))
            driver.execute_script("arguments[0].click();", expanded_tab)
            time.sleep(3) 
            
    except TimeoutException:
        print(f"      [警告] 找不到 {tab} 標籤。請確認畫面是否卡住。")
        return pd.DataFrame()

    print(f"      正在擷取表格資料...")
    try:
        # 確保表格已經出現
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        time.sleep(1)
    except TimeoutException:
        return pd.DataFrame()
        
    # 球隊資料只有一頁，抓一次就收工！
    df = utils.extract_table_from_page(driver)
    return df


def clean_team_df(df, is_expanded=False):
    """🌟 專門用來清洗球隊髒資料的函式"""
    if df.empty:
        return df
    
    # 1. 清洗標題 (Headers)
    df.columns = df.columns.str.replace('caret-upcaret-down ', '', regex=False)
    df.columns = df.columns.str.replace('caret-upcaret-down', '', regex=False)
    df.columns = df.columns.str.replace('TEAMTEAM', 'TEAM', regex=False)
    
    cleaned_cols = []
    for col in df.columns:
        if ' ' in str(col) and col != 'TEAM':
            cleaned_cols.append(str(col).split(' ')[0])
        else:
            cleaned_cols.append(col)
    df.columns = cleaned_cols
    
    # 2. 清洗球隊名稱並拆分出 RANK
    if 'TEAM' in df.columns:
        def parse_team(raw_name):
            if not isinstance(raw_name, str):
                return pd.Series([None, raw_name])
            
            rank = ""
            cleaned_name = raw_name
            
            # A. 抓取開頭的排名 (RANK)
            rank_match = re.match(r'^(\d+)', cleaned_name)
            if rank_match:
                rank = rank_match.group(1)
                cleaned_name = cleaned_name[len(rank):]
                
            # B. 🌟 核心修正：清除字尾的數字、空白與亂碼方框
            # \d+ 代表數字, \s+ 代表空白, [\u200b-\u200f\ufeff]+ 代表隱藏的排版字元或亂碼方框
            # $ 代表只針對字串的「最後面」進行清除，不會誤砍球隊名字中間的字
            cleaned_name = re.sub(r'(\d+|[\u200b-\u200f\ufeff]+|\s+)+$', '', cleaned_name)
                
            return pd.Series([rank, cleaned_name])

        # 執行拆分，並將結果存入新欄位
        df[['RANK', 'TEAM_CLEAN']] = df['TEAM'].apply(parse_team)
        
        # 刪除舊的髒名字，把乾淨的名字改回 TEAM
        df = df.drop(columns=['TEAM'])
        df = df.rename(columns={'TEAM_CLEAN': 'TEAM'})
        
        # ====== 🌟 排版與防呆設計 ======
        if is_expanded:
            # Expanded 表格不需要保留 RANK，避免合併後出現重複
            df = df.drop(columns=['RANK'], errors='ignore')
        else:
            # Standard 表格把 RANK 移到最前面
            cols = df.columns.tolist()
            for c in ['RANK', 'TEAM']:
                if c in cols:
                    cols.remove(c)
            df = df[['RANK', 'TEAM'] + cols]
            
    return df


def run(years):
    """執行球隊資料的爬取與合併"""
    driver = utils.init_driver()
    tasks = ["hitting", "pitching"]

    save_dir = r"D:\Big_data_Science\1121420_HW2"
    os.makedirs(save_dir, exist_ok=True)
    
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
                    print(f"      [警告] {year} 年資料不完整，跳過合併。")
                    continue

                try:
                    # 確保第一欄叫做 'TEAM'
                    if len(df_std.columns) > 0:
                        df_std.rename(columns={df_std.columns[0]: 'TEAM'}, inplace=True)
                    if len(df_exp.columns) > 0:
                        df_exp.rename(columns={df_exp.columns[0]: 'TEAM'}, inplace=True)

                    # 呼叫清洗函式
                    df_std = clean_team_df(df_std, is_expanded=False)
                    df_exp = clean_team_df(df_exp, is_expanded=True)

                    # 球隊的合併 Key 是 'TEAM'
                    df_merged = pd.merge(df_std, df_exp, on='TEAM', how='inner', suffixes=('', '_expanded'))
                    
                    df_merged.insert(0, 'YEAR', year)
                    final_data.append(df_merged)
                    print(f"      => {year} 年球隊 {stat} 合併成功！共 {len(df_merged)} 筆。")
                except KeyError as e:
                    print(f"      [錯誤] 找不到 'TEAM' 欄位，請檢查擷取狀況。詳細錯誤: {e}")

            if final_data:
                pd.concat(final_data, ignore_index=True).to_csv(out_file, index=False, encoding='utf-8-sig')
                print(f"★★★ 已產出乾淨完美的檔案: {out_file} ★★★")
    finally:
        driver.quit()