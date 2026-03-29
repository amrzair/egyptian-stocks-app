import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class MubasherScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    def get_stock_price(self, symbol):
        """Get live price for a single stock from Mubasher"""
        url = f"https://www.mubasher.info/markets/EGX/stocks/{symbol}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to find price
                price_element = soup.find('span', class_='last-price')
                if not price_element:
                    price_element = soup.find('div', class_='last-price')
                if not price_element:
                    price_element = soup.find(attrs={'data-field': 'last'})
                
                # Try to find change
                change_element = soup.find('span', class_='change')
                change_pct_element = soup.find('span', class_='change-percent')
                
                # Extract text
                price = None
                change = None
                change_pct = None
                
                # Search for price in page text
                text = soup.get_text()
                
                # Look for price patterns
                price_match = re.search(r'(\d+\.?\d*)\s*EGP', text)
                if price_match:
                    price = float(price_match.group(1))
                
                return {
                    'symbol': symbol,
                    'price': price,
                    'change': change,
                    'change_pct': change_pct,
                    'source': 'Mubasher'
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None

    def get_egx_summary(self):
        """Get EGX market summary"""
        url = "https://www.mubasher.info/markets/EGX/stocks"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                stocks = []
                
                # Find stock table
                table = soup.find('table')
                
                if table:
                    rows = table.find_all('tr')[1:]  # Skip header
                    
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 5:
                            stock = {
                                'name': cols[0].text.strip(),
                                'last': cols[1].text.strip(),
                                'change': cols[2].text.strip(),
                                'change_pct': cols[3].text.strip(),
                                'volume': cols[4].text.strip() if len(cols) > 4 else ''
                            }
                            stocks.append(stock)
                
                return pd.DataFrame(stocks)
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Error: {e}")
            return pd.DataFrame()


# Alternative: Direct EGX Website
class EGXDirectScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    
    def get_all_prices(self):
        """Get all stock prices from EGX API"""
        # EGX has a data endpoint
        url = "https://www.egx.com.eg/en/stockswatch.aspx"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            print(f"EGX Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all stock data
                stocks = []
                
                # Look for stock rows
                for row in soup.find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        try:
                            stock = {
                                'symbol': cols[0].text.strip(),
                                'name': cols[1].text.strip() if len(cols) > 1 else '',
                                'last': cols[2].text.strip() if len(cols) > 2 else '',
                                'change': cols[3].text.strip() if len(cols) > 3 else '',
                                'change_pct': cols[4].text.strip() if len(cols) > 4 else '',
                                'volume': cols[5].text.strip() if len(cols) > 5 else ''
                            }
                            if stock['symbol'] and stock['last']:
                                stocks.append(stock)
                        except:
                            continue
                
                return pd.DataFrame(stocks)
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Error: {e}")
            return pd.DataFrame()


# Test the scrapers
if __name__ == "__main__":
    print("Testing Mubasher Scraper...")
    print("-" * 50)
    
    mubasher = MubasherScraper()
    
    # Test single stock
    result = mubasher.get_stock_price("COMI")
    print(f"CIB Result: {result}")
    
    print("\n" + "-" * 50)
    print("Testing EGX Direct Scraper...")
    
    egx = EGXDirectScraper()
    df = egx.get_all_prices()
    
    if not df.empty:
        print(f"Found {len(df)} stocks from EGX")
        print(df.head(10))
    else:
        print("No data from EGX direct")