import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from stocks_data import EGYPTIAN_STOCKS, get_stock_list, get_all_sectors, get_stock_by_sector
from price_manager import load_prices, save_prices, update_stock_price, get_stock_price, get_all_prices, get_last_update
from datetime import datetime

# Page config - NO SIDEBAR
st.set_page_config(
    page_title="EGX Stocks",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide sidebar completely and style
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main .block-container {
        padding-top: 10px;
        padding-bottom: 80px;
        padding-left: 10px;
        padding-right: 10px;
    }
    
    .app-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .app-header h2 {
        color: white;
        margin: 0;
    }
    
    .app-header p {
        color: #ccc;
        margin: 5px 0 0 0;
        font-size: 14px;
    }
    
    .stButton button {
        width: 100%;
        border-radius: 10px;
        padding: 10px;
        font-weight: bold;
    }
    
    .nav-btn button {
        background-color: #2a5298;
        color: white;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
<div class="app-header">
    <h2>🇪🇬 EGX Stocks</h2>
    <p>Egyptian Stock Market Analyzer</p>
</div>
""", unsafe_allow_html=True)

# TOP NAVIGATION - Works on Mobile!
page = st.selectbox(
    "📌 Select Page:",
    ["📊 Live Prices", "📈 Stock Analysis", "💡 Buy/Sell Advice", "🔄 Update Prices", "📚 Learn Investing"],
    label_visibility="visible"
)

st.markdown("---")

# Helper Functions
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


# ============== LIVE PRICES PAGE ==============
if page == "📊 Live Prices":
    st.header("📊 Live Prices")
    
    prices_df = get_all_prices()
    
    if not prices_df.empty:
        st.success(f"Last updated: {get_last_update()}")
        
        # Filter by sector
        all_sectors = get_all_sectors()
        selected_sector = st.selectbox("Filter by sector:", ["All Sectors"] + all_sectors)
        
        if selected_sector != "All Sectors":
            sector_symbols = [EGYPTIAN_STOCKS[name]['symbol'] for name in get_stock_by_sector(selected_sector).keys()]
            display_df = prices_df[prices_df['symbol'].isin(sector_symbols)]
        else:
            display_df = prices_df
        
        display_df = display_df.copy()
        display_df['Status'] = display_df['change'].apply(lambda x: "🟢" if x >= 0 else "🔴")
        display_df['price'] = display_df['price'].apply(lambda x: f"{x:.2f}")
        display_df['change_pct'] = display_df['change_pct'].apply(lambda x: f"{x:+.2f}%")
        
        st.dataframe(
            display_df[['Status', 'symbol', 'name', 'price', 'change_pct']],
            use_container_width=True,
            hide_index=True
        )
        
        # Quick Stats
        st.subheader("📈 Market Summary")
        raw_df = get_all_prices()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🟢 Gainers", len(raw_df[raw_df['change'] > 0]))
        with col2:
            st.metric("🔴 Losers", len(raw_df[raw_df['change'] < 0]))
    else:
        st.warning("No data. Go to 'Update Prices' to add prices.")


# ============== STOCK ANALYSIS PAGE ==============
elif page == "📈 Stock Analysis":
    st.header("📈 Stock Analysis")
    
    all_sectors = get_all_sectors()
    selected_sector = st.selectbox("Filter by sector:", ["All Sectors"] + all_sectors)
    
    if selected_sector == "All Sectors":
        available_stocks = get_stock_list()
    else:
        available_stocks = list(get_stock_by_sector(selected_sector).keys())
    
    selected_stock = st.selectbox("Select stock:", available_stocks)
    period = st.selectbox("Period:", ["3mo", "6mo", "1y", "2y"])
    
    if selected_stock:
        symbol = EGYPTIAN_STOCKS[selected_stock]['symbol']
        ticker = f"{symbol}.CA"
        
        current_data = get_stock_price(symbol)
        if current_data:
            st.info(f"Current: EGP {current_data['price']:.2f} | {current_data['change_pct']:.2f}%")
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if not hist.empty and len(hist) > 20:
                hist['SMA20'] = calculate_sma(hist['Close'], 20)
                hist['SMA50'] = calculate_sma(hist['Close'], 50)
                hist['RSI'] = calculate_rsi(hist['Close'])
                hist['MACD'], hist['Signal'], hist['MACD_Hist'] = calculate_macd(hist['Close'])
                
                trend, trend_icon = get_trend(hist['Close'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Trend", f"{trend_icon} {trend}")
                with col2:
                    rsi_current = hist['RSI'].iloc[-1]
                    st.metric("RSI", f"{rsi_current:.1f}")
                
                # Price Chart
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name="Price"
                ))
                fig.update_layout(
                    title=f"{selected_stock}",
                    template="plotly_dark",
                    height=400,
                    margin=dict(l=10, r=10, t=40, b=10)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # RSI Chart
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], name="RSI", line=dict(color='purple')))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                fig_rsi.update_layout(title="RSI", template="plotly_dark", height=250, margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig_rsi, use_container_width=True)
            else:
                st.warning("Not enough data for this stock.")
        except Exception as e:
            st.error(f"Error: {e}")


# ============== BUY/SELL ADVICE PAGE ==============
elif page == "💡 Buy/Sell Advice":
    st.header("💡 Buy/Sell Advice")
    
    all_sectors = get_all_sectors()
    selected_sector = st.selectbox("Filter by sector:", ["All Sectors"] + all_sectors, key="adv_sector")
    
    if selected_sector == "All Sectors":
        available_stocks = get_stock_list()
    else:
        available_stocks = list(get_stock_by_sector(selected_sector).keys())
    
    selected_stock = st.selectbox("Select stock:", available_stocks, key="adv_stock")
    
    if st.button("🔍 Get Recommendation", use_container_width=True):
        symbol = EGYPTIAN_STOCKS[selected_stock]['symbol']
        ticker = f"{symbol}.CA"
        
        with st.spinner("Analyzing..."):
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
                    
                    score = 0
                    reasons = []
                    
                    if current_price > sma20 > sma50:
                        score += 2
                        reasons.append("✅ Strong uptrend")
                    elif current_price > sma20:
                        score += 1
                        reasons.append("✅ Above SMA20")
                    elif current_price < sma20 < sma50:
                        score -= 2
                        reasons.append("❌ Strong downtrend")
                    elif current_price < sma20:
                        score -= 1
                        reasons.append("❌ Below SMA20")
                    
                    if rsi < 30:
                        score += 2
                        reasons.append(f"✅ RSI oversold ({rsi:.0f})")
                    elif rsi > 70:
                        score -= 2
                        reasons.append(f"❌ RSI overbought ({rsi:.0f})")
                    
                    if macd > signal:
                        score += 1
                        reasons.append("✅ MACD bullish")
                    else:
                        score -= 1
                        reasons.append("❌ MACD bearish")
                    
                    # Recommendation
                    if score >= 3:
                        rec, color = "🟢 STRONG BUY", "green"
                    elif score >= 1:
                        rec, color = "🟢 BUY", "lightgreen"
                    elif score <= -3:
                        rec, color = "🔴 STRONG SELL", "red"
                    elif score <= -1:
                        rec, color = "🔴 SELL", "lightcoral"
                    else:
                        rec, color = "🟡 HOLD", "yellow"
                    
                    st.markdown(f"""
                    <div style="background-color:{color}; padding:20px; border-radius:15px; text-align:center; margin:15px 0;">
                        <h2 style="color:black; margin:0;">{rec}</h2>
                        <p style="color:black;">Score: {score}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.subheader("Analysis:")
                    for reason in reasons:
                        st.write(reason)
                    
                    st.warning("⚠️ For educational purposes only!")
                else:
                    st.warning("Not enough data.")
            except Exception as e:
                st.error(f"Error: {e}")


# ============== UPDATE PRICES PAGE ==============
elif page == "🔄 Update Prices":
    st.header("🔄 Update Prices")
    
    tab1, tab2 = st.tabs(["📝 Single Stock", "📤 Upload CSV"])
    
    with tab1:
        available_stocks = get_stock_list()
        selected_stock = st.selectbox("Select stock:", available_stocks)
        
        if selected_stock:
            symbol = EGYPTIAN_STOCKS[selected_stock]['symbol']
            
            new_price = st.number_input("Price (EGP):", min_value=0.01, step=0.01)
            new_change = st.number_input("Change:", step=0.01)
            new_change_pct = st.number_input("Change %:", step=0.01)
            
            if st.button("💾 Save", use_container_width=True):
                if new_price > 0:
                    update_stock_price(symbol, new_price, new_change, new_change_pct, 0)
                    st.success(f"✅ Updated {selected_stock}")
                    st.rerun()
    
    with tab2:
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        
        if uploaded_file:
            try:
                new_df = pd.read_csv(uploaded_file)
                st.dataframe(new_df.head())
                
                if st.button("✅ Import", use_container_width=True):
                    new_df['date'] = datetime.now().strftime("%Y-%m-%d")
                    save_prices(new_df)
                    st.success("✅ Imported!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


# ============== LEARN INVESTING PAGE ==============
elif page == "📚 Learn Investing":
    st.header("📚 Learn Investing")
    
    topic = st.selectbox("Choose topic:", [
        "📊 Stock Market Basics",
        "📈 Technical Indicators",
        "🕯️ Candlestick Patterns",
        "💰 Fundamental Analysis",
        "🛡️ Risk Management",
        "🇪🇬 EGX Guide"
    ])
    
    if topic == "📊 Stock Market Basics":
        st.markdown("""
        ### What is a Stock?
        A stock represents ownership in a company.
        
        ### How to Make Money:
        - **Capital Gains**: Buy low, sell high
        - **Dividends**: Company shares profits
        
        ### Key Terms:
        - 🐂 **Bull Market**: Prices rising
        - 🐻 **Bear Market**: Prices falling
        - **Volume**: Shares traded
        - **Market Cap**: Company total value
        """)
    
    elif topic == "📈 Technical Indicators":
        st.markdown("""
        ### SMA (Simple Moving Average)
        Average price over a period.
        - Price > SMA = 🟢 Bullish
        - Price < SMA = 🔴 Bearish
        
        ### RSI (Relative Strength Index)
        Measures momentum (0-100).
        - RSI > 70 = Overbought (Sell signal)
        - RSI < 30 = Oversold (Buy signal)
        
        ### MACD
        Shows trend momentum.
        - MACD > Signal = 🟢 Buy
        - MACD < Signal = 🔴 Sell
        """)
    
    elif topic == "🕯️ Candlestick Patterns":
        st.markdown("""
        ### Reading Candlesticks
        - 🟢 Green = Price went UP
        - 🔴 Red = Price went DOWN
        
        ### Bullish Patterns (Buy):
        - **Hammer**: Reversal after downtrend
        - **Morning Star**: 3-candle reversal
        
        ### Bearish Patterns (Sell):
        - **Shooting Star**: Reversal after uptrend
        - **Evening Star**: 3-candle reversal
        """)
    
    elif topic == "💰 Fundamental Analysis":
        st.markdown("""
        ### P/E Ratio
        ```
        P/E = Stock Price ÷ Earnings Per Share
        ```
        - Low P/E (<15) = Possibly undervalued
        - High P/E (>25) = Possibly overvalued
        
        ### EPS (Earnings Per Share)
        Company profit per share.
        - Growing EPS = Good sign ✅
        
        ### Dividend Yield
        ```
        Yield = (Annual Dividend ÷ Price) × 100
        ```
        """)
    
    elif topic == "🛡️ Risk Management":
        st.markdown("""
        ### Golden Rules
        1. Never risk more than 1-2% per trade
        2. Always use stop loss
        3. Diversify your portfolio
        
        ### Stop Loss Example
        - Buy at EGP 100
        - Stop loss at EGP 90 (10%)
        - Maximum loss = 10%
        
        ### Portfolio Allocation
        - 60% Blue chips (safe)
        - 30% Growth stocks
        - 10% Speculative
        """)
    
    elif topic == "🇪🇬 EGX Guide":
        st.markdown("""
        ### Trading Hours
        - **Days**: Sunday - Thursday
        - **Time**: 10:00 AM - 2:30 PM
        
        ### Main Indices
        - **EGX 30**: Top 30 companies
        - **EGX 70**: Next 70 companies
        - **EGX 100**: Combined index
        
        ### How to Start
        1. Choose a broker (EFG Hermes, CI Capital)
        2. Open account with National ID
        3. Fund your account
        4. Start trading!
        """)

# Footer
st.markdown("---")
st.markdown("<center>Built with ❤️ for Egyptian Investors</center>", unsafe_allow_html=True)