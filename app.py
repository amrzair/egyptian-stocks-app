import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from stocks_data import EGYPTIAN_STOCKS, get_stock_list, get_all_sectors, get_stock_by_sector
from price_manager import load_prices, save_prices, update_stock_price, get_stock_price, get_all_prices, get_last_update
from datetime import datetime

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from stocks_data import EGYPTIAN_STOCKS, get_stock_list, get_all_sectors, get_stock_by_sector
from price_manager import load_prices, save_prices, update_stock_price, get_stock_price, get_all_prices, get_last_update
from datetime import datetime

# Page config
st.set_page_config(
    page_title="EGX Stocks",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced Mobile PWA Styles
st.markdown("""
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="EGX Stocks">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

<style>
    /* Hide Streamlit elements for app feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Full screen app feel */
    .main .block-container {
        padding-top: 20px;
        padding-bottom: 20px;
        max-width: 100%;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 10px;
            padding-right: 10px;
        }
        
        h1 {
            font-size: 22px !important;
        }
        
        h2 {
            font-size: 18px !important;
        }
        
        h3 {
            font-size: 16px !important;
        }
        
        .stSelectbox, .stMultiSelect {
            width: 100% !important;
        }
        
        .stButton button {
            width: 100% !important;
            padding: 15px !important;
            font-size: 16px !important;
            border-radius: 12px !important;
            font-weight: bold !important;
        }
        
        .stDataFrame {
            font-size: 12px !important;
        }
    }
    
    /* App Header */
    .app-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #1e3c72 100%);
        padding: 25px 15px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .app-header h1 {
        color: white;
        margin: 0;
        font-size: 28px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .app-header p {
        color: #e0e0e0;
        margin: 5px 0 0 0;
        font-size: 14px;
    }
    
    /* Navigation Cards */
    .nav-card {
        background: linear-gradient(145deg, #2d2d2d, #1a1a1a);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 10px 0;
        border: 1px solid #333;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .nav-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.4);
    }
    
    .nav-card h3 {
        color: white;
        margin: 10px 0 5px 0;
    }
    
    .nav-card p {
        color: #888;
        margin: 0;
        font-size: 12px;
    }
    
    /* Stock Cards */
    .stock-card-green {
        background: linear-gradient(145deg, #1b4332, #081c15);
        padding: 15px;
        border-radius: 12px;
        border-left: 4px solid #40c057;
        margin: 10px 0;
    }
    
    .stock-card-red {
        background: linear-gradient(145deg, #4a1a1a, #1a0505);
        padding: 15px;
        border-radius: 12px;
        border-left: 4px solid #e03131;
        margin: 10px 0;
    }
    
    /* Better Buttons */
    .stButton button {
        background: linear-gradient(145deg, #2a5298, #1e3c72);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background: linear-gradient(145deg, #3a6bc5, #2a5298);
        transform: translateY(-2px);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: bold !important;
    }
    
    /* Recommendation Box */
    .rec-box {
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
    }
    
    .rec-buy {
        background: linear-gradient(145deg, #40c057, #2b8a3e);
    }
    
    .rec-sell {
        background: linear-gradient(145deg, #e03131, #c92a2a);
    }
    
    .rec-hold {
        background: linear-gradient(145deg, #fab005, #f59f00);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        font-size: 16px !important;
        font-weight: bold !important;
    }
    
    /* Bottom Navigation */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #1a1a1a;
        padding: 10px;
        display: flex;
        justify-content: space-around;
        border-top: 1px solid #333;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
<div class="app-header">
    <h1>🇪🇬 EGX Stocks</h1>
    <p>Your Personal Egyptian Stock Analyzer</p>
</div>
""", unsafe_allow_html=True)

# Helper Functions for Technical Analysis
def calculate_sma(data, window):
    return data.rolling(window=window).mean()

def calculate_ema(data, window):
    return data.ewm(span=window, adjust=False).mean()

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data):
    ema12 = calculate_ema(data, 12)
    ema26 = calculate_ema(data, 26)
    macd = ema12 - ema26
    signal = calculate_ema(macd, 9)
    histogram = macd - signal
    return macd, signal, histogram

def get_trend(data):
    sma20 = calculate_sma(data, 20)
    sma50 = calculate_sma(data, 50)
    
    if len(sma20.dropna()) == 0 or len(sma50.dropna()) == 0:
        return "Unknown", "⚪"
    
    current_price = data.iloc[-1]
    sma20_current = sma20.iloc[-1]
    sma50_current = sma50.iloc[-1]
    
    if current_price > sma20_current > sma50_current:
        return "Strong Uptrend", "🟢"
    elif current_price > sma20_current:
        return "Uptrend", "🟢"
    elif current_price < sma20_current < sma50_current:
        return "Strong Downtrend", "🔴"
    elif current_price < sma20_current:
        return "Downtrend", "🔴"
    else:
        return "Sideways", "🟡"

# Main App
st.title("Egyptian Stock Market Analyzer")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a feature:", [
    "Live Prices",
    "Update Prices",
    "Stock Analysis", 
    "Buy/Sell Advice",
    "Learn Investing"
])

# Show last update in sidebar
last_update = get_last_update()
st.sidebar.markdown(f"**Last Price Update:** {last_update}")

# ============== LIVE PRICES PAGE ==============
if page == "Live Prices":
    st.header("Live Egyptian Stock Prices")
    
    # Load current prices
    prices_df = get_all_prices()
    
    if not prices_df.empty:
        st.success(f"📊 Showing {len(prices_df)} stocks | Last updated: {get_last_update()}")
        
        # Filter by sector
        all_sectors = get_all_sectors()
        selected_sector = st.selectbox("Filter by sector:", ["All Sectors"] + all_sectors)
        
        # Filter dataframe
        if selected_sector != "All Sectors":
            sector_symbols = [EGYPTIAN_STOCKS[name]['symbol'] for name in get_stock_by_sector(selected_sector).keys()]
            display_df = prices_df[prices_df['symbol'].isin(sector_symbols)]
        else:
            display_df = prices_df
        
        # Add color indicators
        display_df = display_df.copy()
        display_df['Status'] = display_df['change'].apply(lambda x: "🟢" if x >= 0 else "🔴")
        
        # Format columns
        display_df['price'] = display_df['price'].apply(lambda x: f"EGP {x:.2f}")
        display_df['change'] = display_df['change'].apply(lambda x: f"{x:+.2f}")
        display_df['change_pct'] = display_df['change_pct'].apply(lambda x: f"{x:+.2f}%")
        display_df['volume'] = display_df['volume'].apply(lambda x: f"{x:,.0f}")
        
        # Rename columns for display
        display_df = display_df.rename(columns={
            'symbol': 'Symbol',
            'name': 'Stock Name',
            'price': 'Price',
            'change': 'Change',
            'change_pct': 'Change %',
            'volume': 'Volume',
            'date': 'Date'
        })
        
        # Display table
        st.dataframe(
            display_df[['Status', 'Symbol', 'Stock Name', 'Price', 'Change', 'Change %', 'Volume']],
            use_container_width=True,
            hide_index=True
        )
        
        # Quick Stats
        st.subheader("📈 Market Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        raw_df = get_all_prices()
        gainers = len(raw_df[raw_df['change'] > 0])
        losers = len(raw_df[raw_df['change'] < 0])
        unchanged = len(raw_df[raw_df['change'] == 0])
        
        with col1:
            st.metric("Total Stocks", len(raw_df))
        with col2:
            st.metric("Gainers 🟢", gainers)
        with col3:
            st.metric("Losers 🔴", losers)
        with col4:
            st.metric("Unchanged ⚪", unchanged)
        
        # Top Gainers & Losers
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔥 Top Gainers")
            top_gainers = raw_df.nlargest(5, 'change_pct')[['symbol', 'name', 'price', 'change_pct']]
            top_gainers['change_pct'] = top_gainers['change_pct'].apply(lambda x: f"+{x:.2f}%")
            st.dataframe(top_gainers, use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("📉 Top Losers")
            top_losers = raw_df.nsmallest(5, 'change_pct')[['symbol', 'name', 'price', 'change_pct']]
            top_losers['change_pct'] = top_losers['change_pct'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(top_losers, use_container_width=True, hide_index=True)
    
    else:
        st.warning("No price data available. Please go to 'Update Prices' to add current prices.")

# ============== UPDATE PRICES PAGE ==============
elif page == "Update Prices":
    st.header("Update Stock Prices")
    st.write("Keep your data fresh by updating prices manually or uploading a CSV file.")
    
    tab1, tab2, tab3 = st.tabs(["📝 Update Single Stock", "📤 Upload CSV", "📋 Download Template"])
    
    with tab1:
        st.subheader("Update Single Stock")
        
        available_stocks = get_stock_list()
        selected_stock = st.selectbox("Select stock:", available_stocks)
        
        if selected_stock:
            symbol = EGYPTIAN_STOCKS[selected_stock]['symbol']
            current_data = get_stock_price(symbol)
            
            if current_data:
                st.info(f"Current price: EGP {current_data['price']:.2f} (Last updated: {current_data['date']})")
            
            col1, col2 = st.columns(2)
            with col1:
                new_price = st.number_input("New Price (EGP):", min_value=0.01, step=0.01)
                new_change = st.number_input("Change (EGP):", step=0.01)
            with col2:
                new_change_pct = st.number_input("Change %:", step=0.01)
                new_volume = st.number_input("Volume:", min_value=0, step=1000)
            
            if st.button("💾 Update Price"):
                if new_price > 0:
                    update_stock_price(symbol, new_price, new_change, new_change_pct, new_volume)
                    st.success(f"✅ Updated {selected_stock} to EGP {new_price:.2f}")
                    st.rerun()
                else:
                    st.error("Please enter a valid price")
    
    with tab2:
        st.subheader("Upload CSV File")
        st.write("Upload a CSV file with the latest prices.")
        st.write("Required columns: `symbol`, `name`, `price`, `change`, `change_pct`, `volume`")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file is not None:
            try:
                new_df = pd.read_csv(uploaded_file)
                st.write("Preview:")
                st.dataframe(new_df.head(10))
                
                if st.button("✅ Import Prices"):
                    new_df['date'] = datetime.now().strftime("%Y-%m-%d")
                    save_prices(new_df)
                    st.success(f"✅ Imported {len(new_df)} stock prices!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    with tab3:
        st.subheader("Download Template")
        st.write("Download a template CSV file to fill with current prices.")
        
        # Create template
        template_data = []
        for name, info in EGYPTIAN_STOCKS.items():
            template_data.append({
                'symbol': info['symbol'],
                'name': name,
                'price': 0.00,
                'change': 0.00,
                'change_pct': 0.00,
                'volume': 0,
                'date': datetime.now().strftime("%Y-%m-%d")
            })
        
        template_df = pd.DataFrame(template_data)
        
        csv = template_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Template CSV",
            data=csv,
            file_name="egx_prices_template.csv",
            mime="text/csv"
        )

# ============== STOCK ANALYSIS PAGE ==============
elif page == "Stock Analysis":
    st.header("Stock Analysis")
    
    all_sectors = get_all_sectors()
    selected_sector = st.selectbox("Filter by sector:", ["All Sectors"] + all_sectors)
    
    if selected_sector == "All Sectors":
        available_stocks = get_stock_list()
    else:
        available_stocks = list(get_stock_by_sector(selected_sector).keys())
    
    selected_stock = st.selectbox("Select a stock to analyze:", available_stocks)
    period = st.selectbox("Analysis period:", ["3mo", "6mo", "1y", "2y"])
    
    if selected_stock:
        symbol = EGYPTIAN_STOCKS[selected_stock]['symbol']
        ticker = f"{symbol}.CA"
        
        # Show current price from our data
        current_data = get_stock_price(symbol)
        if current_data:
            st.info(f"📊 Current Price (from your data): **EGP {current_data['price']:.2f}** | Change: {current_data['change_pct']:.2f}% | Updated: {current_data['date']}")
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if not hist.empty and len(hist) > 20:
                
                # Calculate indicators
                hist['SMA20'] = calculate_sma(hist['Close'], 20)
                hist['SMA50'] = calculate_sma(hist['Close'], 50)
                hist['EMA12'] = calculate_ema(hist['Close'], 12)
                hist['RSI'] = calculate_rsi(hist['Close'])
                hist['MACD'], hist['Signal'], hist['MACD_Hist'] = calculate_macd(hist['Close'])
                
                trend, trend_icon = get_trend(hist['Close'])
                
                # Display Stats
                st.subheader("Key Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    yahoo_price = hist['Close'].iloc[-1]
                    st.metric("Yahoo Price", f"EGP {yahoo_price:.2f}")
                
                with col2:
                    high_52w = hist['High'].max()
                    st.metric("Period High", f"EGP {high_52w:.2f}")
                
                with col3:
                    low_52w = hist['Low'].min()
                    st.metric("Period Low", f"EGP {low_52w:.2f}")
                
                with col4:
                    avg_volume = hist['Volume'].mean()
                    st.metric("Avg Volume", f"{avg_volume:,.0f}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Trend", f"{trend_icon} {trend}")
                
                with col2:
                    rsi_current = hist['RSI'].iloc[-1]
                    rsi_status = "Overbought 🔴" if rsi_current > 70 else "Oversold 🟢" if rsi_current < 30 else "Neutral 🟡"
                    st.metric("RSI (14)", f"{rsi_current:.1f} - {rsi_status}")
                
                with col3:
                    macd_current = hist['MACD'].iloc[-1]
                    signal_current = hist['Signal'].iloc[-1]
                    macd_status = "Bullish 🟢" if macd_current > signal_current else "Bearish 🔴"
                    st.metric("MACD", macd_status)
                
                # Charts
                st.subheader("Technical Chart")
                
                show_sma20 = st.checkbox("Show SMA 20", value=True)
                show_sma50 = st.checkbox("Show SMA 50", value=True)
                show_volume = st.checkbox("Show Volume", value=True)
                
                if show_volume:
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                       vertical_spacing=0.1, row_heights=[0.7, 0.3])
                else:
                    fig = make_subplots(rows=1, cols=1)
                
                fig.add_trace(go.Candlestick(
                    x=hist.index, open=hist['Open'], high=hist['High'],
                    low=hist['Low'], close=hist['Close'], name="Price"
                ), row=1, col=1)
                
                if show_sma20:
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA20'],
                        name="SMA 20", line=dict(color='orange', width=1)), row=1, col=1)
                
                if show_sma50:
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA50'],
                        name="SMA 50", line=dict(color='blue', width=1)), row=1, col=1)
                
                if show_volume:
                    colors = ['green' if hist['Close'].iloc[i] >= hist['Open'].iloc[i] else 'red' 
                             for i in range(len(hist))]
                    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'],
                        name="Volume", marker_color=colors), row=2, col=1)
                
                fig.update_layout(title=f"{selected_stock} Technical Analysis",
                    template="plotly_dark", height=600, showlegend=True)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # RSI Chart
                st.subheader("RSI Indicator")
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=hist.index, y=hist['RSI'],
                    name="RSI", line=dict(color='purple', width=2)))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
                fig_rsi.update_layout(title="RSI (14)", template="plotly_dark", height=300)
                st.plotly_chart(fig_rsi, use_container_width=True)
                
                # MACD Chart
                st.subheader("MACD Indicator")
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(x=hist.index, y=hist['MACD'],
                    name="MACD", line=dict(color='blue', width=2)))
                fig_macd.add_trace(go.Scatter(x=hist.index, y=hist['Signal'],
                    name="Signal", line=dict(color='orange', width=2)))
                fig_macd.add_trace(go.Bar(x=hist.index, y=hist['MACD_Hist'],
                    name="Histogram", marker_color=['green' if v >= 0 else 'red' for v in hist['MACD_Hist']]))
                fig_macd.update_layout(title="MACD", template="plotly_dark", height=300)
                st.plotly_chart(fig_macd, use_container_width=True)
                
            else:
                st.warning("Not enough historical data available for this stock.")
                
        except Exception as e:
            st.error(f"Error loading data: {e}")

# ============== BUY/SELL ADVICE PAGE ==============
elif page == "Buy/Sell Advice":
    st.header("Buy/Sell/Hold Advice")
    st.write("Get AI-powered recommendations based on technical analysis")
    
    all_sectors = get_all_sectors()
    selected_sector = st.selectbox("Filter by sector:", ["All Sectors"] + all_sectors, key="advice_sector")
    
    if selected_sector == "All Sectors":
        available_stocks = get_stock_list()
    else:
        available_stocks = list(get_stock_by_sector(selected_sector).keys())
    
    selected_stock = st.selectbox("Select a stock for advice:", available_stocks, key="advice_stock")
    
    # Show current price from our data
    if selected_stock:
        symbol = EGYPTIAN_STOCKS[selected_stock]['symbol']
        current_data = get_stock_price(symbol)
        if current_data:
            st.info(f"📊 Current Price: **EGP {current_data['price']:.2f}** | Updated: {current_data['date']}")
    
    if st.button("🔍 Analyze & Get Recommendation"):
        
        symbol = EGYPTIAN_STOCKS[selected_stock]['symbol']
        ticker = f"{symbol}.CA"
        
        with st.spinner("Analyzing stock data..."):
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="6mo")
                
                if not hist.empty and len(hist) > 50:
                    
                    hist['SMA20'] = calculate_sma(hist['Close'], 20)
                    hist['SMA50'] = calculate_sma(hist['Close'], 50)
                    hist['RSI'] = calculate_rsi(hist['Close'])
                    hist['MACD'], hist['Signal'], hist['MACD_Hist'] = calculate_macd(hist['Close'])
                    
                    current_price = hist['Close'].iloc[-1]
                    sma20 = hist['SMA20'].iloc[-1]
                    sma50 = hist['SMA50'].iloc[-1]
                    rsi = hist['RSI'].iloc[-1]
                    macd = hist['MACD'].iloc[-1]
                    signal = hist['Signal'].iloc[-1]
                    
                    price_1w_ago = hist['Close'].iloc[-5] if len(hist) > 5 else current_price
                    price_1m_ago = hist['Close'].iloc[-22] if len(hist) > 22 else current_price
                    change_1w = ((current_price - price_1w_ago) / price_1w_ago) * 100
                    change_1m = ((current_price - price_1m_ago) / price_1m_ago) * 100
                    
                    score = 0
                    reasons_buy = []
                    reasons_sell = []
                    reasons_hold = []
                    
                    if current_price > sma20 > sma50:
                        score += 2
                        reasons_buy.append("✅ Strong uptrend: Price > SMA20 > SMA50")
                    elif current_price > sma20:
                        score += 1
                        reasons_buy.append("✅ Price above SMA20 (short-term bullish)")
                    elif current_price < sma20 < sma50:
                        score -= 2
                        reasons_sell.append("❌ Strong downtrend: Price < SMA20 < SMA50")
                    elif current_price < sma20:
                        score -= 1
                        reasons_sell.append("❌ Price below SMA20 (short-term bearish)")
                    
                    if rsi < 30:
                        score += 2
                        reasons_buy.append(f"✅ RSI is {rsi:.1f} (Oversold - potential bounce)")
                    elif rsi < 40:
                        score += 1
                        reasons_buy.append(f"✅ RSI is {rsi:.1f} (Approaching oversold)")
                    elif rsi > 70:
                        score -= 2
                        reasons_sell.append(f"❌ RSI is {rsi:.1f} (Overbought - potential pullback)")
                    elif rsi > 60:
                        score -= 1
                        reasons_sell.append(f"⚠️ RSI is {rsi:.1f} (Approaching overbought)")
                    else:
                        reasons_hold.append(f"➖ RSI is {rsi:.1f} (Neutral zone)")
                    
                    if macd > signal and hist['MACD'].iloc[-2] <= hist['Signal'].iloc[-2]:
                        score += 2
                        reasons_buy.append("✅ MACD just crossed above Signal (Buy signal)")
                    elif macd > signal:
                        score += 1
                        reasons_buy.append("✅ MACD above Signal line (Bullish)")
                    elif macd < signal and hist['MACD'].iloc[-2] >= hist['Signal'].iloc[-2]:
                        score -= 2
                        reasons_sell.append("❌ MACD just crossed below Signal (Sell signal)")
                    elif macd < signal:
                        score -= 1
                        reasons_sell.append("❌ MACD below Signal line (Bearish)")
                    
                    if change_1w > 5:
                        score += 1
                        reasons_buy.append(f"✅ Strong weekly momentum: +{change_1w:.1f}%")
                    elif change_1w < -5:
                        score -= 1
                        reasons_sell.append(f"❌ Weak weekly momentum: {change_1w:.1f}%")
                    
                    if change_1m > 10:
                        score += 1
                        reasons_buy.append(f"✅ Strong monthly momentum: +{change_1m:.1f}%")
                    elif change_1m < -10:
                        score -= 1
                        reasons_sell.append(f"❌ Weak monthly momentum: {change_1m:.1f}%")
                    
                    avg_volume = hist['Volume'].mean()
                    recent_volume = hist['Volume'].iloc[-5:].mean()
                    if recent_volume > avg_volume * 1.5:
                        if change_1w > 0:
                            score += 1
                            reasons_buy.append("✅ High volume with price increase")
                        else:
                            score -= 1
                            reasons_sell.append("❌ High volume with price decrease")
                    
                    if score >= 3:
                        recommendation = "STRONG BUY"
                        rec_color = "green"
                        rec_icon = "🟢"
                    elif score >= 1:
                        recommendation = "BUY"
                        rec_color = "lightgreen"
                        rec_icon = "🟢"
                    elif score <= -3:
                        recommendation = "STRONG SELL"
                        rec_color = "red"
                        rec_icon = "🔴"
                    elif score <= -1:
                        recommendation = "SELL"
                        rec_color = "lightcoral"
                        rec_icon = "🔴"
                    else:
                        recommendation = "HOLD"
                        rec_color = "yellow"
                        rec_icon = "🟡"
                    
                    st.markdown("---")
                    st.subheader(f"Recommendation for {selected_stock}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current Price", f"EGP {current_price:.2f}")
                    with col2:
                        st.metric("Weekly Change", f"{change_1w:.2f}%")
                    with col3:
                        st.metric("Monthly Change", f"{change_1m:.2f}%")
                    
                    st.markdown(f"""
                    <div style="background-color: {rec_color}; padding: 30px; border-radius: 10px; text-align: center; margin: 20px 0;">
                        <h1 style="color: black; margin: 0;">{rec_icon} {recommendation}</h1>
                        <p style="color: black; margin: 10px 0 0 0;">Analysis Score: {score}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.subheader("📊 Detailed Analysis")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### 🟢 Bullish Signals")
                        if reasons_buy:
                            for reason in reasons_buy:
                                st.write(reason)
                        else:
                            st.write("No bullish signals detected")
                    
                    with col2:
                        st.markdown("### 🔴 Bearish Signals")
                        if reasons_sell:
                            for reason in reasons_sell:
                                st.write(reason)
                        else:
                            st.write("No bearish signals detected")
                    
                    if reasons_hold:
                        st.markdown("### 🟡 Neutral Signals")
                        for reason in reasons_hold:
                            st.write(reason)
                    
                    st.subheader("📈 Technical Summary")
                    summary_data = {
                        "Indicator": ["Price", "SMA 20", "SMA 50", "RSI (14)", "MACD", "Signal Line"],
                        "Value": [f"EGP {current_price:.2f}", f"EGP {sma20:.2f}", f"EGP {sma50:.2f}",
                                 f"{rsi:.2f}", f"{macd:.4f}", f"{signal:.4f}"],
                        "Status": [
                            "🟢" if current_price > sma20 else "🔴",
                            "🟢" if current_price > sma20 else "🔴",
                            "🟢" if current_price > sma50 else "🔴",
                            "🟢" if rsi < 30 else "🔴" if rsi > 70 else "🟡",
                            "🟢" if macd > signal else "🔴",
                            "🟢" if macd > signal else "🔴"
                        ]
                    }
                    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    st.warning("⚠️ **Disclaimer**: This is for educational purposes only. Always do your own research.")
                    
                else:
                    st.warning("Not enough data available for this stock.")
                    
            except Exception as e:
                st.error(f"Error analyzing stock: {e}")

# ============== LEARN INVESTING PAGE ==============
elif page == "Learn Investing":
    st.header("📚 Learn Investing")
    st.write("Master the art of stock analysis and become a smarter investor!")
    
    # Topic Selection
    topic = st.selectbox("Choose a topic to learn:", [
        "📊 Introduction to Stock Market",
        "📈 Technical Indicators (SMA, EMA, RSI, MACD)",
        "🕯️ Reading Candlestick Charts",
        "💰 Fundamental Analysis",
        "🛡️ Risk Management",
        "🎯 Trading Strategies",
        "🇪🇬 Egyptian Stock Market (EGX) Guide"
    ])
    
    # ============== INTRODUCTION ==============
    if topic == "📊 Introduction to Stock Market":
        st.subheader("📊 Introduction to Stock Market")
        
        st.markdown("""
        ### What is a Stock?
        A **stock** (also called a share) represents ownership in a company. When you buy a stock, 
        you become a partial owner of that company.
        
        ### Why Do Companies Issue Stocks?
        Companies sell stocks to raise money for:
        - 🏭 Expanding their business
        - 🔬 Research and development
        - 💳 Paying off debt
        - 🚀 Launching new products
        
        ### How Do You Make Money from Stocks?
        
        **1. Capital Gains** 💹
        - Buy low, sell high
        - Example: Buy at EGP 50, sell at EGP 70 = EGP 20 profit
        
        **2. Dividends** 💵
        - Some companies share profits with shareholders
        - Paid quarterly or annually
        
        ### Key Terms to Know
        
        | Term | Meaning |
        |------|---------|
        | **Bull Market** 🐂 | Prices are rising, optimism is high |
        | **Bear Market** 🐻 | Prices are falling, pessimism is high |
        | **Volume** | Number of shares traded |
        | **Market Cap** | Total value of company (Price × Shares) |
        | **Liquidity** | How easily you can buy/sell a stock |
        | **Volatility** | How much the price moves up and down |
        
        ### The Egyptian Stock Exchange (EGX)
        
        - 🏛️ Located in Cairo
        - ⏰ Trading hours: Sunday-Thursday, 10:00 AM - 2:30 PM
        - 📊 Main indices: EGX30, EGX70, EGX100
        - 💱 Currency: Egyptian Pound (EGP)
        """)
        
        st.info("💡 **Tip**: Start by understanding the basics before jumping into trading!")

    # ============== TECHNICAL INDICATORS ==============
    elif topic == "📈 Technical Indicators (SMA, EMA, RSI, MACD)":
        st.subheader("📈 Technical Indicators")
        
        st.markdown("""
        Technical indicators help you analyze price movements and predict future trends.
        """)
        
        # SMA
        with st.expander("📏 Simple Moving Average (SMA)", expanded=True):
            st.markdown("""
            ### What is SMA?
            SMA calculates the **average price** over a specific period.
            
            ### Formula:
            ```
            SMA = (Sum of closing prices) ÷ (Number of periods)
            ```
            
            ### Common SMAs:
            - **SMA 20**: Short-term trend (20 days)
            - **SMA 50**: Medium-term trend (50 days)
            - **SMA 200**: Long-term trend (200 days)
            
            ### How to Use:
            | Signal | Meaning |
            |--------|---------|
            | Price > SMA | 🟢 Bullish (Uptrend) |
            | Price < SMA | 🔴 Bearish (Downtrend) |
            | SMA 20 crosses above SMA 50 | 🟢 Golden Cross (Buy signal) |
            | SMA 20 crosses below SMA 50 | 🔴 Death Cross (Sell signal) |
            
            ### Example:
            If CIB's price is **EGP 75** and SMA 20 is **EGP 70**, the stock is in an **uptrend** 
            because the price is above the moving average.
            """)
        
        # EMA
        with st.expander("📈 Exponential Moving Average (EMA)"):
            st.markdown("""
            ### What is EMA?
            EMA is similar to SMA but gives **more weight to recent prices**.
            
            ### Why Use EMA?
            - Reacts faster to price changes
            - Better for short-term trading
            - More sensitive than SMA
            
            ### Common EMAs:
            - **EMA 12**: Fast line (used in MACD)
            - **EMA 26**: Slow line (used in MACD)
            
            ### SMA vs EMA:
            | Feature | SMA | EMA |
            |---------|-----|-----|
            | Speed | Slower | Faster |
            | Best for | Long-term | Short-term |
            | Sensitivity | Less | More |
            """)
        
        # RSI
        with st.expander("💪 Relative Strength Index (RSI)"):
            st.markdown("""
            ### What is RSI?
            RSI measures the **speed and change of price movements** on a scale of 0-100.
            
            ### How to Read RSI:
            | RSI Value | Meaning | Action |
            |-----------|---------|--------|
            | Above 70 | 🔴 Overbought | Consider selling |
            | Below 30 | 🟢 Oversold | Consider buying |
            | 30-70 | 🟡 Neutral | Wait for signal |
            
            ### RSI Strategies:
            
            **1. Overbought/Oversold Strategy**
            - Buy when RSI drops below 30 and starts rising
            - Sell when RSI goes above 70 and starts falling
            
            **2. Divergence Strategy**
            - **Bullish Divergence**: Price makes lower low, but RSI makes higher low → Buy signal
            - **Bearish Divergence**: Price makes higher high, but RSI makes lower high → Sell signal
            
            ### Example:
            If Fawry's RSI is **25**, the stock is **oversold** and might bounce back up soon.
            """)
        
        # MACD
        with st.expander("📊 MACD (Moving Average Convergence Divergence)"):
            st.markdown("""
            ### What is MACD?
            MACD shows the relationship between two moving averages and helps identify momentum.
            
            ### Components:
            1. **MACD Line** = EMA 12 - EMA 26
            2. **Signal Line** = EMA 9 of MACD Line
            3. **Histogram** = MACD Line - Signal Line
            
            ### How to Read MACD:
            | Signal | Meaning |
            |--------|---------|
            | MACD crosses above Signal | 🟢 Buy signal |
            | MACD crosses below Signal | 🔴 Sell signal |
            | Histogram positive (green) | 🟢 Bullish momentum |
            | Histogram negative (red) | 🔴 Bearish momentum |
            
            ### Pro Tips:
            - ✅ Use MACD with other indicators for confirmation
            - ✅ Look for divergences between MACD and price
            - ❌ Don't rely on MACD alone
            """)
        
        st.success("🎓 **Practice**: Go to 'Stock Analysis' page and observe these indicators on real stocks!")

    # ============== CANDLESTICK CHARTS ==============
    elif topic == "🕯️ Reading Candlestick Charts":
        st.subheader("🕯️ Reading Candlestick Charts")
        
        st.markdown("""
        ### What is a Candlestick?
        A candlestick shows **4 prices** for a specific time period:
        
        ```
              │ ← High
           ┌──┴──┐
           │     │ ← Body (Open to Close)
           └──┬──┘
              │ ← Low
        ```
        
        ### Candlestick Colors:
        | Color | Meaning |
        |-------|---------|
        | 🟢 Green/White | Price went UP (Close > Open) |
        | 🔴 Red/Black | Price went DOWN (Close < Open) |
        
        ### Parts of a Candlestick:
        - **Body**: The thick part (difference between open and close)
        - **Upper Shadow/Wick**: Line above body (high price)
        - **Lower Shadow/Wick**: Line below body (low price)
        """)
        
        with st.expander("📈 Bullish Patterns (Buy Signals)"):
            st.markdown("""
            ### 1. Hammer 🔨
            - Small body at the top
            - Long lower shadow (2x body size)
            - Appears after downtrend
            - **Signal**: Reversal to uptrend
            
            ### 2. Bullish Engulfing
            - Green candle completely covers previous red candle
            - **Signal**: Strong buying pressure
            
            ### 3. Morning Star ⭐
            - Three candles: Red → Small body → Green
            - **Signal**: Reversal from downtrend
            
            ### 4. Three White Soldiers
            - Three consecutive green candles
            - Each closes higher than the previous
            - **Signal**: Strong uptrend
            """)
        
        with st.expander("📉 Bearish Patterns (Sell Signals)"):
            st.markdown("""
            ### 1. Shooting Star 🌠
            - Small body at the bottom
            - Long upper shadow
            - Appears after uptrend
            - **Signal**: Reversal to downtrend
            
            ### 2. Bearish Engulfing
            - Red candle completely covers previous green candle
            - **Signal**: Strong selling pressure
            
            ### 3. Evening Star 🌙
            - Three candles: Green → Small body → Red
            - **Signal**: Reversal from uptrend
            
            ### 4. Three Black Crows
            - Three consecutive red candles
            - Each closes lower than the previous
            - **Signal**: Strong downtrend
            """)
        
        with st.expander("🟡 Neutral/Indecision Patterns"):
            st.markdown("""
            ### 1. Doji
            - Open and close are almost equal
            - Looks like a cross (+)
            - **Signal**: Market indecision, possible reversal
            
            ### 2. Spinning Top
            - Small body with equal shadows
            - **Signal**: Neither buyers nor sellers in control
            """)
        
        st.info("💡 **Tip**: Always confirm patterns with volume and other indicators!")

    # ============== FUNDAMENTAL ANALYSIS ==============
    elif topic == "💰 Fundamental Analysis":
        st.subheader("💰 Fundamental Analysis")
        
        st.markdown("""
        Fundamental analysis evaluates a company's **financial health** and **true value**.
        
        ### Key Metrics to Analyze:
        """)
        
        with st.expander("📊 Price-to-Earnings Ratio (P/E)", expanded=True):
            st.markdown("""
            ### Formula:
            ```
            P/E Ratio = Stock Price ÷ Earnings Per Share (EPS)
            ```
            
            ### How to Interpret:
            | P/E Value | Meaning |
            |-----------|---------|
            | Low (< 15) | Stock might be undervalued |
            | Average (15-25) | Fairly valued |
            | High (> 25) | Stock might be overvalued OR high growth expected |
            
            ### Example:
            - CIB Price: EGP 75
            - EPS: EGP 5
            - P/E = 75 ÷ 5 = **15**
            
            This means investors pay EGP 15 for every EGP 1 of earnings.
            """)
        
        with st.expander("💵 Earnings Per Share (EPS)"):
            st.markdown("""
            ### Formula:
            ```
            EPS = (Net Income - Dividends) ÷ Outstanding Shares
            ```
            
            ### What to Look For:
            - ✅ Growing EPS year over year
            - ✅ Positive EPS (profitable company)
            - ❌ Declining EPS (potential problems)
            
            ### Example:
            If a company earned EGP 100 million and has 10 million shares:
            - EPS = 100M ÷ 10M = **EGP 10 per share**
            """)
        
        with st.expander("📚 Price-to-Book Ratio (P/B)"):
            st.markdown("""
            ### Formula:
            ```
            P/B Ratio = Stock Price ÷ Book Value Per Share
            ```
            
            ### Book Value:
            ```
            Book Value = Total Assets - Total Liabilities
            ```
            
            ### How to Interpret:
            | P/B Value | Meaning |
            |-----------|---------|
            | < 1 | Stock trading below its asset value (potentially undervalued) |
            | 1-3 | Fairly valued |
            | > 3 | Might be overvalued |
            """)
        
        with st.expander("💰 Dividend Yield"):
            st.markdown("""
            ### Formula:
            ```
            Dividend Yield = (Annual Dividend ÷ Stock Price) × 100
            ```
            
            ### Example:
            - Stock Price: EGP 100
            - Annual Dividend: EGP 5
            - Dividend Yield = (5 ÷ 100) × 100 = **5%**
            
            ### Good Dividend Yield:
            - Egyptian market: 3-7% is considered good
            - Higher yield = more income but check if it's sustainable
            """)
        
        with st.expander("📈 Return on Equity (ROE)"):
            st.markdown("""
            ### Formula:
            ```
            ROE = (Net Income ÷ Shareholder Equity) × 100
            ```
            
            ### What to Look For:
            - ✅ ROE > 15% is generally good
            - ✅ Consistent ROE over years
            - ✅ Compare with industry average
            """)
        
        st.success("🎓 **Tip**: Combine fundamental analysis with technical analysis for best results!")

    # ============== RISK MANAGEMENT ==============
    elif topic == "🛡️ Risk Management":
        st.subheader("🛡️ Risk Management")
        
        st.markdown("""
        ### The Golden Rules of Investing
        
        > "Rule #1: Never lose money. Rule #2: Never forget Rule #1." - Warren Buffett
        
        Risk management protects your capital and keeps you in the game!
        """)
        
        with st.expander("🛑 Stop Loss", expanded=True):
            st.markdown("""
            ### What is Stop Loss?
            A **stop loss** is a predetermined price at which you sell to limit your loss.
            
            ### Example:
            - You buy CIB at EGP 75
            - You set stop loss at EGP 67.50 (10% below)
            - If price drops to EGP 67.50, you sell automatically
            - Maximum loss: 10%
            
            ### Stop Loss Strategies:
            | Type | Description |
            |------|-------------|
            | **Percentage Stop** | Sell if price drops X% (e.g., 10%) |
            | **Support Level Stop** | Sell if price breaks below support |
            | **Moving Average Stop** | Sell if price drops below SMA 20 |
            | **Trailing Stop** | Moves up with price, locks in profits |
            
            ### Recommended Stop Loss:
            - Conservative: 5-7%
            - Moderate: 8-10%
            - Aggressive: 12-15%
            """)
        
        with st.expander("📊 Position Sizing"):
            st.markdown("""
            ### The 1% Rule
            Never risk more than **1-2%** of your total capital on a single trade.
            
            ### Example:
            - Total Capital: EGP 100,000
            - Maximum risk per trade: EGP 1,000-2,000 (1-2%)
            
            ### Calculating Position Size:
            ```
            Position Size = (Capital × Risk %) ÷ (Entry Price - Stop Loss)
            ```
            
            ### Example:
            - Capital: EGP 100,000
            - Risk: 1% = EGP 1,000
            - Entry: EGP 50
            - Stop Loss: EGP 45
            - Position Size = 1,000 ÷ (50-45) = **200 shares**
            """)
        
        with st.expander("🎯 Diversification"):
            st.markdown("""
            ### Don't Put All Eggs in One Basket!
            
            Spread your investments across:
            
            ### 1. Different Sectors
            - Banks (CIB, QNB Alahli)
            - Real Estate (TMG, Palm Hills)
            - Healthcare (Cleopatra, Ibnsina)
            - Technology (Fawry, E-Finance)
            
            ### 2. Different Risk Levels
            - 60% Low risk (Blue chips, banks)
            - 30% Medium risk (Growth stocks)
            - 10% High risk (Speculative)
            
            ### 3. Recommended Portfolio:
            | Stock Type | Allocation |
            |------------|------------|
            | Blue Chips | 50-60% |
            | Growth Stocks | 25-30% |
            | Speculative | 10-15% |
            | Cash Reserve | 5-10% |
            """)
        
        with st.expander("🧠 Emotional Control"):
            st.markdown("""
            ### Common Mistakes to Avoid:
            
            | Mistake | Solution |
            |---------|----------|
            | 😨 **Panic Selling** | Stick to your stop loss plan |
            | 🤑 **Greed** | Take profits at target price |
            | 😤 **Revenge Trading** | Take a break after losses |
            | 🙈 **Ignoring Losses** | Accept small losses early |
            | 📱 **Overtrading** | Quality over quantity |
            
            ### Tips:
            - ✅ Have a written trading plan
            - ✅ Set entry, exit, and stop loss BEFORE trading
            - ✅ Keep a trading journal
            - ✅ Never invest money you can't afford to lose
            """)

    # ============== TRADING STRATEGIES ==============
    elif topic == "🎯 Trading Strategies":
        st.subheader("🎯 Trading Strategies")
        
        st.markdown("""
        Choose a strategy that fits your personality and goals!
        """)
        
        with st.expander("📅 Long-term Investing (Buy & Hold)", expanded=True):
            st.markdown("""
            ### What is it?
            Buy quality stocks and hold for **years**.
            
            ### Best For:
            - 👨‍💼 Busy people with little time
            - 🎯 Long-term wealth building
            - 😌 Low-stress approach
            
            ### How to Do It:
            1. Research company fundamentals
            2. Buy quality stocks at fair prices
            3. Hold for 3-10+ years
            4. Reinvest dividends
            
            ### Best Stocks for This:
            - Banks: CIB, QNB Alahli
            - Blue chips: Eastern Company, Telecom Egypt
            """)
        
        with st.expander("📈 Swing Trading"):
            st.markdown("""
            ### What is it?
            Hold stocks for **days to weeks** to capture price swings.
            
            ### Best For:
            - 👀 People who can check market daily
            - 💰 Medium-term profits
            
            ### How to Do It:
            1. Find stocks in an uptrend
            2. Buy at support levels
            3. Sell at resistance levels
            4. Hold for 3-15 days
            
            ### Indicators to Use:
            - SMA 20 and SMA 50
            - RSI for entry/exit
            - MACD for confirmation
            """)
        
        with st.expander("⚡ Day Trading"):
            st.markdown("""
            ### What is it?
            Buy and sell within the **same day**.
            
            ### Best For:
            - 🖥️ Full-time traders
            - ⚡ Quick decision makers
            
            ### Requirements:
            - ❗ Full attention during market hours
            - ❗ Fast internet connection
            - ❗ Strong discipline
            - ❗ High risk tolerance
            
            ### Warning:
            ⚠️ Day trading is very risky and not recommended for beginners!
            """)
        
        with st.expander("💡 My Recommended Strategy for Beginners"):
            st.markdown("""
            ### The Hybrid Approach
            
            **70% Long-term + 30% Swing Trading**
            
            ### Step-by-Step:
            
            **1. Core Portfolio (70%)**
            - Buy 5-7 blue chip stocks
            - Hold for years
            - Examples: CIB, TMG, Eastern Company
            
            **2. Active Trading (30%)**
            - Swing trade with strong trends
            - Use technical analysis
            - Quick profits
            
            **3. Entry Checklist:**
            - ✅ Price above SMA 20
            - ✅ RSI between 40-60 (room to grow)
            - ✅ MACD bullish
            - ✅ Volume increasing
            
            **4. Exit Checklist:**
            - ✅ Take profit at 15-20% gain
            - ✅ Stop loss at 8-10% loss
            - ✅ RSI above 70 (overbought)
            """)

    # ============== EGX GUIDE ==============
    elif topic == "🇪🇬 Egyptian Stock Market (EGX) Guide":
        st.subheader("🇪🇬 Egyptian Stock Market (EGX) Guide")
        
        st.markdown("""
        ### About the Egyptian Exchange
        
        The **Egyptian Exchange (EGX)** is one of the oldest stock exchanges in the Middle East, 
        established in 1883.
        """)
        
        with st.expander("⏰ Trading Hours & Days", expanded=True):
            st.markdown("""
            ### Market Schedule:
            
            | Day | Status |
            |-----|--------|
            | Sunday | ✅ Open |
            | Monday | ✅ Open |
            | Tuesday | ✅ Open |
            | Wednesday | ✅ Open |
            | Thursday | ✅ Open |
            | Friday | ❌ Closed |
            | Saturday | ❌ Closed |
            
            ### Trading Sessions:
            | Session | Time |
            |---------|------|
            | Pre-opening | 9:30 AM - 10:00 AM |
            | Main Session | 10:00 AM - 2:30 PM |
            | Closing Auction | 2:30 PM - 2:35 PM |
            """)
        
        with st.expander("📊 Main Indices"):
            st.markdown("""
            ### EGX Indices:
            
            | Index | Description |
            |-------|-------------|
            | **EGX 30** | Top 30 companies by market cap & liquidity |
            | **EGX 70** | Next 70 companies after EGX 30 |
            | **EGX 100** | Combines EGX 30 + EGX 70 |
            
            ### EGX 30 Components (Major Companies):
            - Commercial International Bank (CIB)
            - Talaat Moustafa Group (TMG)
            - Eastern Company
            - Telecom Egypt
            - EFG Hermes
            - Fawry
            - And more...
            """)
        
        with st.expander("💰 How to Start Trading"):
            st.markdown("""
            ### Step-by-Step Guide:
            
            **1. Choose a Broker**
            - EFG Hermes
            - CI Capital
            - Beltone Financial
            - Pharos Holding
            - Arabeya Online
            
            **2. Open an Account**
            - Visit broker's office or apply online
            - Provide: National ID, proof of address
            - Minimum deposit varies (EGP 5,000 - 50,000)
            
            **3. Fund Your Account**
            - Bank transfer
            - Check deposit
            
            **4. Start Trading**
            - Use broker's platform
            - Place buy/sell orders
            
            ### Fees to Expect:
            | Fee Type | Amount |
            |----------|--------|
            | Broker Commission | 0.15% - 0.3% |
            | EGX Fee | 0.05% |
            | Clearing Fee | 0.0125% |
            | Capital Gains Tax | 0% (currently suspended) |
            """)
        
        with st.expander("🏆 Top Sectors in EGX"):
            st.markdown("""
            ### Sector Overview:
            
            | Sector | Key Stocks | Characteristics |
            |--------|------------|-----------------|
            | **Banks** | CIB, QNB Alahli | Stable, dividends |
            | **Real Estate** | TMG, Palm Hills, SODIC | Growth, cyclical |
            | **Healthcare** | Cleopatra, Ibnsina | Defensive, growing |
            | **FinTech** | Fawry, E-Finance | High growth |
            | **Food & Beverage** | Eastern, Juhayna | Stable, defensive |
            | **Construction** | Orascom, Ezz Steel | Cyclical |
            """)
        
        st.success("🎓 You're now ready to start your investing journey in the Egyptian market!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    ### 📚 Continue Learning
    
    **Recommended Next Steps:**
    1. Practice on the **Stock Analysis** page
    2. Get recommendations on **Buy/Sell Advice** page
    3. Start with small amounts
    4. Keep learning!
    
    **Remember:** *Investing involves risk. Never invest money you can't afford to lose.*
    """)