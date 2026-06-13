import player_scraper
import team_scraper

if __name__ == "__main__":
    target_years = range(2003, 2024)
    
    print("========================================")
    print("   MLB Historical Data Web Scraper    ")
    print(f"   目標年份: {target_years}   ")
    print("========================================\n")
    
    # 球員資料爬取
    print(">>> 啟動球員資料爬取模組...")
    player_scraper.run(target_years)
    
    print("\n----------------------------------------\n")
    
    # 球隊資料爬取
    print(">>> 啟動球隊資料爬取模組...")
    team_scraper.run(target_years)
    print("   所有爬蟲任務執行完畢！檔案已順利匯出。   ")