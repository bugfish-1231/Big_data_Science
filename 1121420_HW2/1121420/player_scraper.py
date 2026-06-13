import time
import pandas as pd
import os
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import utils

def scrape_player_pages(driver, year, stat_type, tab):

    print(f"    -> 準備抓取球員 {tab} 表格 (年份: {year})...")
    
    if stat_type == "hitting":
        # 打擊的網址結構：https://www.mlb.com/stats/2022
        base_url = f"https://www.mlb.com/stats/{year}/player" 
    else: 
        # 投球的網址結構：https://www.mlb.com/stats/pitching/2022
        base_url = f"https://www.mlb.com/stats/pitching/{year}"
        
    # 前往正確的網址
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
            next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='next page button']")
            if not next_btn.is_enabled():
                break
            driver.execute_script("arguments[0].click();", next_btn)
            page_num += 1
        except NoSuchElementException:
            break

    return pd.concat(all_pages_data, ignore_index=True) if all_pages_data else pd.DataFrame()

def clean_mlb_df(df, is_expanded=False):
    if df.empty:
        return df
    
    # Clean Headers
    df.columns = df.columns.str.replace('caret-upcaret-down ', '', regex=False)
    df.columns = df.columns.str.replace('caret-upcaret-down', '', regex=False)
    df.columns = df.columns.str.replace('TEAMTEAM', 'TEAM', regex=False)
    
    cleaned_cols = []
    for col in df.columns:
        if ' ' in str(col) and col != 'PLAYER':
            cleaned_cols.append(str(col).split(' ')[0])
        else:
            cleaned_cols.append(col)
    df.columns = cleaned_cols

    if 'PLAYER' in df.columns:
        def parse_player(raw_name):
            if not isinstance(raw_name, str):
                return pd.Series([None, raw_name, None])
            
            rank = ""
            position = ""
            cleaned_name = raw_name
            
            # A. RANK
            rank_match = re.match(r'^(\d+)', cleaned_name)
            if rank_match:
                rank = rank_match.group(1)
                cleaned_name = cleaned_name[len(rank):]
                
            # B. 移除結尾的多餘數字
            cleaned_name = re.sub(r'\d*[\u200b-\u200f\ufeff\s]*$', '', cleaned_name)
            
            # C. 抓取結尾的守備位置 (POSITION)
            pos_match = re.search(r'(C|1B|2B|3B|SS|LF|CF|RF|OF|DH|P|TWP)$', cleaned_name)
            if pos_match:
                position = pos_match.group(1)
                cleaned_name = cleaned_name[:-len(position)]
                
            # D. 清理名字 
            dup_match = re.search(r'(.+?)\1$', cleaned_name)
            if dup_match:
                last_name = dup_match.group(1).strip()
                first_part = cleaned_name[:-len(dup_match.group(0))].strip()
                if len(first_part) > 0:
                    first_name = first_part[:-1].strip() # 砍掉最後一個縮寫字母
                    cleaned_name = f"{first_name} {last_name}"
                    
            return pd.Series([rank, cleaned_name, position])

        # 執行拆分，並將結果存入三個新欄位
        df[['RANK', 'PLAYER_CLEAN', 'POSITION']] = df['PLAYER'].apply(parse_player)
        
        # 刪除舊的髒名字，把乾淨的名字改回 PLAYER
        df = df.drop(columns=['PLAYER'])
        df = df.rename(columns={'PLAYER_CLEAN': 'PLAYER'})
        
        if is_expanded:
            # 如果是 Expanded 表格，直接把 RANK 跟 POSITION 丟掉，
            df = df.drop(columns=['RANK', 'POSITION'], errors='ignore')
        else:
            cols = df.columns.tolist()
            for c in ['RANK', 'PLAYER', 'POSITION']:
                if c in cols:
                    cols.remove(c)
            df = df[['RANK', 'PLAYER', 'POSITION'] + cols]
            
    return df

def run(years):
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
                    # 確保 Standard 表格的第一個欄位叫做 'PLAYER'
                    if len(df_std.columns) > 0:
                        df_std.rename(columns={df_std.columns[0]: 'PLAYER'}, inplace=True)
                        
                    # 確保 Expanded 表格的第一個欄位叫做 'PLAYER'
                    if len(df_exp.columns) > 0:
                        df_exp.rename(columns={df_exp.columns[0]: 'PLAYER'}, inplace=True)
                    # ====================================

                    # 注意：Expanded 傳入 True，讓它自動隱藏重複的排名與守位
                    df_std = clean_mlb_df(df_std, is_expanded=False)
                    df_exp = clean_mlb_df(df_exp, is_expanded=True)
                    # ==============================================================

                    # 球員的合併 Key 是乾淨的 'PLAYER'
                    df_merged = pd.merge(df_std, df_exp, on='PLAYER', how='inner', suffixes=('', '_expanded'))
                    
                    # 把年份插在最前面 (Index 0)
                    df_merged.insert(0, 'YEAR', year)
                    final_data.append(df_merged)
                    print(f"      => {year} 年球員 {stat} 合併成功！共 {len(df_merged)} 筆。")
                except KeyError as e:
                    print(f"      [錯誤] 找不到 'PLAYER' 欄位，請檢查擷取狀況。詳細錯誤: {e}")

            if final_data:
                pd.concat(final_data, ignore_index=True).to_csv(out_file, index=False, encoding='utf-8-sig')
                print(f" 已產出乾淨完美的檔案: {out_file} ")
    finally:
        driver.quit()