import player_scraper
import team_scraper

if __name__ == "__main__":
    # 設定要抓取的年份範圍
    target_years = [2022, 2023]
    
    print("========================================")
    print("   MLB Historical Data Web Scraper 啟動   ")
    print(f"   目標年份: {target_years}   ")
    print("========================================\n")
    
    # 執行模組 1: 球員資料爬取
    print(">>> 啟動球員資料爬取模組...")
    player_scraper.run(target_years)
    
    print("\n----------------------------------------\n")
    
    # 執行模組 2: 球隊資料爬取
    print(">>> 啟動球隊資料爬取模組...")
    team_scraper.run(target_years)
    
    print("\n========================================")
    print("   所有爬蟲任務執行完畢！檔案已順利匯出。   ")
    print("========================================")