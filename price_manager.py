import pandas as pd
import os
from datetime import datetime

CSV_FILE = "current_prices.csv"

def load_prices():
    """Load prices from CSV file"""
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        return df
    return pd.DataFrame()

def save_prices(df):
    """Save prices to CSV file"""
    df.to_csv(CSV_FILE, index=False)

def update_stock_price(symbol, price, change=None, change_pct=None, volume=None):
    """Update a single stock price"""
    df = load_prices()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if symbol in df['symbol'].values:
        # Update existing
        df.loc[df['symbol'] == symbol, 'price'] = price
        df.loc[df['symbol'] == symbol, 'date'] = today
        if change is not None:
            df.loc[df['symbol'] == symbol, 'change'] = change
        if change_pct is not None:
            df.loc[df['symbol'] == symbol, 'change_pct'] = change_pct
        if volume is not None:
            df.loc[df['symbol'] == symbol, 'volume'] = volume
    else:
        # Add new
        new_row = {
            'symbol': symbol,
            'name': symbol,
            'price': price,
            'change': change or 0,
            'change_pct': change_pct or 0,
            'volume': volume or 0,
            'date': today
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    save_prices(df)
    return True

def get_stock_price(symbol):
    """Get price for a single stock"""
    df = load_prices()
    if symbol in df['symbol'].values:
        row = df[df['symbol'] == symbol].iloc[0]
        return {
            'symbol': symbol,
            'name': row['name'],
            'price': row['price'],
            'change': row['change'],
            'change_pct': row['change_pct'],
            'volume': row['volume'],
            'date': row['date']
        }
    return None

def get_all_prices():
    """Get all prices"""
    return load_prices()

def get_last_update():
    """Get the last update date"""
    df = load_prices()
    if not df.empty and 'date' in df.columns:
        return df['date'].max()
    return "Never"