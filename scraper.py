import requests
from bs4 import BeautifulSoup
import pandas as pd

class EGXScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def get_egx_stocks(self):
        """Get Egyptian stocks from EGX official website"""
        url = "https://www.egx.com.eg/en/stockswatch.aspx"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            print(f"Status Code: {response.status_code}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stocks = []
            
            # Find all tables
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables")
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cols = row.find_all('td')
                    if len(cols) >= 5:
                        stock = {
                            'name': cols[0].text.strip(),
                            'last': cols[1].text.strip() if len(cols) > 1 else '',
                            'change': cols[2].text.strip() if len(cols) > 2 else '',
                            'change_pct': cols[3].text.strip() if len(cols) > 3 else '',
                            'volume': cols[4].text.strip() if len(cols) > 4 else ''
                        }
                        if stock['name']:
                            stocks.append(stock)
            
            return pd.DataFrame(stocks)
        
        except Exception as e:
            print(f"Error: {e}")
            return pd.DataFrame()


# Test
if __name__ == "__main__":
    scraper = EGXScraper()
    print("Fetching from EGX...\n")
    df = scraper.get_egx_stocks()
    
    if not df.empty:
        print(f"Found {len(df)} stocks!\n")
        print(df.head(20))
        df.to_csv("egyptian_stocks_list.csv", index=False)
        print("\nSaved to egyptian_stocks_list.csv")
    else:
        print("No stocks found. Let's try alternative method...")