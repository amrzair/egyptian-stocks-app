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
    
    # ============== STOCK MARKET BASICS ==============
    if topic == "📊 Stock Market Basics":
        st.markdown("""
        ### What is a Stock?
        A stock represents ownership in a company.
        
        ### How to Make Money:
        - **Capital Gains**: Buy low, sell high
        - **Dividends**: Company shares profits
        """)
        
        # Sample Price Growth Chart
        st.subheader("📈 Example: Capital Gains")
        
        sample_dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        sample_prices = [50]
        for i in range(99):
            change = np.random.randn() * 0.5 + 0.1
            sample_prices.append(sample_prices[-1] + change)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sample_dates,
            y=sample_prices,
            mode='lines',
            name='Stock Price',
            line=dict(color='#00ff88', width=2)
        ))
        fig.add_annotation(x=sample_dates[20], y=sample_prices[20],
            text="Buy Here: EGP 52", showarrow=True, arrowhead=1, bgcolor="green")
        fig.add_annotation(x=sample_dates[80], y=sample_prices[80],
            text="Sell Here: EGP 68", showarrow=True, arrowhead=1, bgcolor="red")
        fig.update_layout(
            title="Example: Buy Low, Sell High",
            template="plotly_dark",
            height=350,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("💡 Profit = EGP 68 - EGP 52 = **EGP 16 per share**")
        
        st.markdown("""
        ### Key Terms:
        - 🐂 **Bull Market**: Prices rising
        - 🐻 **Bear Market**: Prices falling
        - **Volume**: Shares traded
        - **Market Cap**: Company total value
        """)
        
        # Bull vs Bear Market Chart
        st.subheader("🐂 Bull vs 🐻 Bear Market")
        
        col1, col2 = st.columns(2)
        
        with col1:
            bull_prices = [50 + i*0.3 + np.random.randn()*0.5 for i in range(50)]
            fig_bull = go.Figure()
            fig_bull.add_trace(go.Scatter(y=bull_prices, mode='lines', line=dict(color='green', width=3)))
            fig_bull.update_layout(title="🐂 Bull Market (Uptrend)", template="plotly_dark", height=200, 
                                   margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
            st.plotly_chart(fig_bull, use_container_width=True)
        
        with col2:
            bear_prices = [70 - i*0.3 + np.random.randn()*0.5 for i in range(50)]
            fig_bear = go.Figure()
            fig_bear.add_trace(go.Scatter(y=bear_prices, mode='lines', line=dict(color='red', width=3)))
            fig_bear.update_layout(title="🐻 Bear Market (Downtrend)", template="plotly_dark", height=200,
                                   margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
            st.plotly_chart(fig_bear, use_container_width=True)
    
    # ============== TECHNICAL INDICATORS ==============
    elif topic == "📈 Technical Indicators":
        st.markdown("""
        ### Technical indicators help predict future price movements
        """)
        
        # Generate sample data
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        prices = [50]
        for i in range(99):
            prices.append(prices[-1] + np.random.randn() * 1.5)
        prices = pd.Series(prices)
        
        # SMA Section
        st.subheader("📏 SMA (Simple Moving Average)")
        st.markdown("""
        SMA smooths price data to show the trend direction.
        - **SMA 20**: Short-term trend
        - **SMA 50**: Medium-term trend
        """)
        
        sma20 = prices.rolling(20).mean()
        sma50 = prices.rolling(50).mean()
        
        fig_sma = go.Figure()
        fig_sma.add_trace(go.Scatter(x=dates, y=prices, name="Price", line=dict(color='white', width=1)))
        fig_sma.add_trace(go.Scatter(x=dates, y=sma20, name="SMA 20", line=dict(color='orange', width=2)))
        fig_sma.add_trace(go.Scatter(x=dates, y=sma50, name="SMA 50", line=dict(color='blue', width=2)))
        fig_sma.update_layout(
            title="Price with SMA 20 & SMA 50",
            template="plotly_dark",
            height=350,
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig_sma, use_container_width=True)
        
        st.markdown("""
        **How to Read:**
        | Signal | Meaning |
        |--------|---------|
        | Price > SMA | 🟢 Bullish (Uptrend) |
        | Price < SMA | 🔴 Bearish (Downtrend) |
        | SMA 20 crosses above SMA 50 | 🟢 Golden Cross (Buy!) |
        | SMA 20 crosses below SMA 50 | 🔴 Death Cross (Sell!) |
        """)
        
        # RSI Section
        st.subheader("💪 RSI (Relative Strength Index)")
        st.markdown("""
        RSI measures if a stock is **overbought** or **oversold** (0-100 scale).
        """)
        
        # Generate RSI-like data
        rsi_values = [50]
        for i in range(99):
            change = np.random.randn() * 5
            new_val = rsi_values[-1] + change
            new_val = max(10, min(90, new_val))  # Keep between 10-90
            rsi_values.append(new_val)
        
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=dates, y=rsi_values, name="RSI", line=dict(color='purple', width=2)))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
        fig_rsi.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1)
        fig_rsi.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1)
        fig_rsi.update_layout(
            title="RSI Indicator Example",
            template="plotly_dark",
            height=300,
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig_rsi, use_container_width=True)
        
        st.markdown("""
        **How to Read:**
        | RSI Value | Meaning | Action |
        |-----------|---------|--------|
        | > 70 | 🔴 Overbought | Consider Selling |
        | < 30 | 🟢 Oversold | Consider Buying |
        | 30-70 | 🟡 Neutral | Wait |
        """)
        
        # MACD Section
        st.subheader("📊 MACD (Moving Average Convergence Divergence)")
        st.markdown("""
        MACD shows momentum and trend changes.
        """)
        
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line
        
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=dates, y=macd_line, name="MACD", line=dict(color='blue', width=2)))
        fig_macd.add_trace(go.Scatter(x=dates, y=signal_line, name="Signal", line=dict(color='orange', width=2)))
        fig_macd.add_trace(go.Bar(x=dates, y=histogram, name="Histogram",
                                  marker_color=['green' if v >= 0 else 'red' for v in histogram]))
        fig_macd.update_layout(
            title="MACD Indicator Example",
            template="plotly_dark",
            height=300,
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig_macd, use_container_width=True)
        
        st.markdown("""
        **How to Read:**
        | Signal | Meaning |
        |--------|---------|
        | MACD crosses above Signal | 🟢 Buy Signal |
        | MACD crosses below Signal | 🔴 Sell Signal |
        | Green Histogram | 🟢 Bullish Momentum |
        | Red Histogram | 🔴 Bearish Momentum |
        """)
    
    # ============== CANDLESTICK PATTERNS ==============
    elif topic == "🕯️ Candlestick Patterns":
        st.markdown("""
        ### Understanding Candlesticks
        Each candle shows 4 prices: **Open, High, Low, Close**
        """)
        
        # Basic Candlestick Explanation
        st.subheader("📖 Anatomy of a Candlestick")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bullish Candle
            fig_bull_candle = go.Figure()
            fig_bull_candle.add_trace(go.Candlestick(
                x=['Bullish'],
                open=[50], high=[58], low=[48], close=[56],
                increasing_line_color='green',
                increasing_fillcolor='green'
            ))
            fig_bull_candle.update_layout(
                title="🟢 Bullish Candle",
                template="plotly_dark",
                height=300,
                showlegend=False,
                xaxis=dict(visible=False),
                annotations=[
                    dict(x='Bullish', y=58, text="High", showarrow=True, arrowhead=1, yshift=10),
                    dict(x='Bullish', y=48, text="Low", showarrow=True, arrowhead=1, yshift=-10),
                    dict(x='Bullish', y=50, text="Open", showarrow=True, arrowhead=1, xshift=-40),
                    dict(x='Bullish', y=56, text="Close", showarrow=True, arrowhead=1, xshift=40),
                ]
            )
            st.plotly_chart(fig_bull_candle, use_container_width=True)
            st.markdown("**Close > Open = Price went UP**")
        
        with col2:
            # Bearish Candle
            fig_bear_candle = go.Figure()
            fig_bear_candle.add_trace(go.Candlestick(
                x=['Bearish'],
                open=[56], high=[58], low=[48], close=[50],
                decreasing_line_color='red',
                decreasing_fillcolor='red'
            ))
            fig_bear_candle.update_layout(
                title="🔴 Bearish Candle",
                template="plotly_dark",
                height=300,
                showlegend=False,
                xaxis=dict(visible=False),
                annotations=[
                    dict(x='Bearish', y=58, text="High", showarrow=True, arrowhead=1, yshift=10),
                    dict(x='Bearish', y=48, text="Low", showarrow=True, arrowhead=1, yshift=-10),
                    dict(x='Bearish', y=56, text="Open", showarrow=True, arrowhead=1, xshift=-40),
                    dict(x='Bearish', y=50, text="Close", showarrow=True, arrowhead=1, xshift=40),
                ]
            )
            st.plotly_chart(fig_bear_candle, use_container_width=True)
            st.markdown("**Close < Open = Price went DOWN**")
        
        # Bullish Patterns
        st.subheader("🟢 Bullish Patterns (Buy Signals)")
        
        # Hammer Pattern
        st.markdown("#### 🔨 Hammer")
        st.markdown("Appears after a downtrend. Long lower shadow shows buyers pushing price up.")
        
        fig_hammer = go.Figure()
        hammer_data = [
            [52, 54, 50, 51],  # Downtrend
            [51, 52, 48, 49],  # Downtrend
            [49, 50, 45, 48],  # Downtrend
            [48, 52, 42, 51],  # Hammer!
            [51, 55, 50, 54],  # Recovery
        ]
        dates_h = ['Day 1', 'Day 2', 'Day 3', 'Hammer', 'Day 5']
        fig_hammer.add_trace(go.Candlestick(
            x=dates_h,
            open=[d[0] for d in hammer_data],
            high=[d[1] for d in hammer_data],
            low=[d[2] for d in hammer_data],
            close=[d[3] for d in hammer_data]
        ))
        fig_hammer.add_annotation(x='Hammer', y=42, text="🔨 Hammer Pattern", showarrow=True, arrowhead=1, yshift=-20, bgcolor="green")
        fig_hammer.update_layout(template="plotly_dark", height=300, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
        st.plotly_chart(fig_hammer, use_container_width=True)
        
        # Bullish Engulfing
        st.markdown("#### 📈 Bullish Engulfing")
        st.markdown("Green candle completely covers the previous red candle.")
        
        fig_engulf = go.Figure()
        engulf_data = [
            [52, 53, 50, 51],
            [51, 52, 49, 50],
            [50, 51, 48, 49],  # Red
            [48, 54, 47, 53],  # Big Green engulfs
            [53, 56, 52, 55],
        ]
        dates_e = ['Day 1', 'Day 2', 'Red', 'Engulfing', 'Day 5']
        fig_engulf.add_trace(go.Candlestick(
            x=dates_e,
            open=[d[0] for d in engulf_data],
            high=[d[1] for d in engulf_data],
            low=[d[2] for d in engulf_data],
            close=[d[3] for d in engulf_data]
        ))
        fig_engulf.add_annotation(x='Engulfing', y=54, text="📈 Bullish Engulfing", showarrow=True, arrowhead=1, yshift=15, bgcolor="green")
        fig_engulf.update_layout(template="plotly_dark", height=300, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
        st.plotly_chart(fig_engulf, use_container_width=True)
        
        # Bearish Patterns
        st.subheader("🔴 Bearish Patterns (Sell Signals)")
        
        # Shooting Star
        st.markdown("#### 🌠 Shooting Star")
        st.markdown("Appears after an uptrend. Long upper shadow shows sellers pushing price down.")
        
        fig_star = go.Figure()
        star_data = [
            [48, 50, 47, 49],  # Uptrend
            [49, 52, 48, 51],  # Uptrend
            [51, 54, 50, 53],  # Uptrend
            [53, 60, 52, 54],  # Shooting Star!
            [54, 55, 50, 51],  # Decline
        ]
        dates_s = ['Day 1', 'Day 2', 'Day 3', 'Star', 'Day 5']
        fig_star.add_trace(go.Candlestick(
            x=dates_s,
            open=[d[0] for d in star_data],
            high=[d[1] for d in star_data],
            low=[d[2] for d in star_data],
            close=[d[3] for d in star_data]
        ))
        fig_star.add_annotation(x='Star', y=60, text="🌠 Shooting Star", showarrow=True, arrowhead=1, yshift=15, bgcolor="red")
        fig_star.update_layout(template="plotly_dark", height=300, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
        st.plotly_chart(fig_star, use_container_width=True)
        
        # Bearish Engulfing
        st.markdown("#### 📉 Bearish Engulfing")
        st.markdown("Red candle completely covers the previous green candle.")
        
        fig_bear_engulf = go.Figure()
        bear_engulf_data = [
            [48, 50, 47, 49],
            [49, 52, 48, 51],
            [51, 53, 50, 52],  # Green
            [53, 54, 47, 48],  # Big Red engulfs
            [48, 49, 45, 46],
        ]
        dates_be = ['Day 1', 'Day 2', 'Green', 'Engulfing', 'Day 5']
        fig_bear_engulf.add_trace(go.Candlestick(
            x=dates_be,
            open=[d[0] for d in bear_engulf_data],
            high=[d[1] for d in bear_engulf_data],
            low=[d[2] for d in bear_engulf_data],
            close=[d[3] for d in bear_engulf_data]
        ))
        fig_bear_engulf.add_annotation(x='Engulfing', y=47, text="📉 Bearish Engulfing", showarrow=True, arrowhead=1, yshift=-20, bgcolor="red")
        fig_bear_engulf.update_layout(template="plotly_dark", height=300, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
        st.plotly_chart(fig_bear_engulf, use_container_width=True)
        
        # Doji
        st.subheader("🟡 Neutral Pattern: Doji")
        st.markdown("Open and Close are almost equal. Shows market indecision.")
        
        fig_doji = go.Figure()
        doji_data = [
            [50, 52, 48, 51],
            [51, 53, 49, 52],
            [52, 55, 49, 52.1],  # Doji
            [52, 54, 50, 53],
            [53, 56, 52, 55],
        ]
        dates_d = ['Day 1', 'Day 2', 'Doji', 'Day 4', 'Day 5']
        fig_doji.add_trace(go.Candlestick(
            x=dates_d,
            open=[d[0] for d in doji_data],
            high=[d[1] for d in doji_data],
            low=[d[2] for d in doji_data],
            close=[d[3] for d in doji_data]
        ))
        fig_doji.add_annotation(x='Doji', y=55, text="✚ Doji (Indecision)", showarrow=True, arrowhead=1, yshift=15, bgcolor="yellow")
        fig_doji.update_layout(template="plotly_dark", height=300, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
        st.plotly_chart(fig_doji, use_container_width=True)
    
    # ============== FUNDAMENTAL ANALYSIS ==============
    elif topic == "💰 Fundamental Analysis":
        st.markdown("""
        ### Fundamental Analysis evaluates a company's true value
        """)
        
        # P/E Ratio
        st.subheader("📊 P/E Ratio (Price to Earnings)")
        st.markdown("""
        **Formula:** P/E = Stock Price ÷ Earnings Per Share
        """)
        
        # P/E Comparison Chart
        companies = ['Company A', 'Company B', 'Company C', 'Company D']
        pe_values = [10, 18, 25, 45]
        colors = ['green', 'lightgreen', 'orange', 'red']
        
        fig_pe = go.Figure()
        fig_pe.add_trace(go.Bar(
            x=companies,
            y=pe_values,
            marker_color=colors,
            text=pe_values,
            textposition='auto'
        ))
        fig_pe.add_hline(y=15, line_dash="dash", line_color="white", annotation_text="Fair Value (15)")
        fig_pe.update_layout(
            title="P/E Ratio Comparison",
            template="plotly_dark",
            height=300,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_pe, use_container_width=True)
        
        st.markdown("""
        | P/E Value | Meaning |
        |-----------|---------|
        | < 15 | 🟢 Possibly undervalued |
        | 15-25 | 🟡 Fairly valued |
        | > 25 | 🔴 Possibly overvalued |
        """)
        
        # EPS Growth
        st.subheader("📈 EPS Growth (Earnings Per Share)")
        
        years = ['2020', '2021', '2022', '2023', '2024']
        eps_good = [2.0, 2.5, 3.0, 3.8, 4.5]
        eps_bad = [3.0, 2.8, 2.5, 2.0, 1.5]
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_eps_good = go.Figure()
            fig_eps_good.add_trace(go.Bar(x=years, y=eps_good, marker_color='green', text=eps_good, textposition='auto'))
            fig_eps_good.update_layout(title="✅ Good: Growing EPS", template="plotly_dark", height=250, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_eps_good, use_container_width=True)
        
        with col2:
            fig_eps_bad = go.Figure()
            fig_eps_bad.add_trace(go.Bar(x=years, y=eps_bad, marker_color='red', text=eps_bad, textposition='auto'))
            fig_eps_bad.update_layout(title="❌ Bad: Declining EPS", template="plotly_dark", height=250, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_eps_bad, use_container_width=True)
        
        # Dividend Yield
        st.subheader("💵 Dividend Yield")
        st.markdown("**Formula:** Yield = (Annual Dividend ÷ Price) × 100")
        
        div_companies = ['Bank A', 'Bank B', 'Tech Co', 'Real Estate', 'Startup']
        div_yields = [5.2, 4.8, 1.5, 3.2, 0]
        
        fig_div = go.Figure()
        fig_div.add_trace(go.Bar(
            x=div_companies,
            y=div_yields,
            marker_color=['green' if y > 3 else 'orange' if y > 0 else 'red' for y in div_yields],
            text=[f"{y}%" for y in div_yields],
            textposition='auto'
        ))
        fig_div.update_layout(
            title="Dividend Yield Comparison",
            template="plotly_dark",
            height=300,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_div, use_container_width=True)
        
        st.info("💡 Egyptian banks often have good dividend yields (3-6%)")
    
    # ============== RISK MANAGEMENT ==============
    elif topic == "🛡️ Risk Management":
        st.markdown("""
        ### Protect Your Capital!
        """)
        
        # Stop Loss Example
        st.subheader("🛑 Stop Loss Example")
        
        dates_sl = pd.date_range(start='2024-01-01', periods=30, freq='D')
        prices_sl = [100, 102, 101, 103, 105, 104, 103, 101, 99, 97, 95, 93, 91, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73]
        
        fig_sl = go.Figure()
        fig_sl.add_trace(go.Scatter(x=dates_sl, y=prices_sl, mode='lines', name='Price', line=dict(color='white', width=2)))
        fig_sl.add_hline(y=100, line_dash="dash", line_color="green", annotation_text="Buy: EGP 100")
        fig_sl.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="Stop Loss: EGP 90 (-10%)")
        fig_sl.add_annotation(x=dates_sl[10], y=95, text="❌ Stop Loss Triggered!", showarrow=True, arrowhead=1, bgcolor="red")
        fig_sl.update_layout(
            title="Stop Loss Protects You!",
            template="plotly_dark",
            height=350,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_sl, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.error("**Without Stop Loss:**\nLoss = EGP 100 → EGP 73 = **-27%**")
        with col2:
            st.success("**With Stop Loss:**\nLoss = EGP 100 → EGP 90 = **-10%**")
        
        # Position Sizing
        st.subheader("📊 Position Sizing (1% Rule)")
        st.markdown("Never risk more than **1-2%** of your capital per trade")
        
        capital = st.slider("Your Capital (EGP):", 10000, 500000, 100000, 10000)
        risk_pct = st.slider("Risk per trade (%):", 1, 5, 2)
        
        risk_amount = capital * (risk_pct / 100)
        
        st.markdown(f"""
        | Item | Value |
        |------|-------|
        | Total Capital | EGP {capital:,} |
        | Risk Percentage | {risk_pct}% |
        | **Max Loss Per Trade** | **EGP {risk_amount:,.0f}** |
        """)
        
        # Portfolio Diversification
        st.subheader("🥧 Portfolio Diversification")
        
        labels = ['Banks (40%)', 'Real Estate (20%)', 'Healthcare (15%)', 'Tech (15%)', 'Cash (10%)']
        values = [40, 20, 15, 15, 10]
        colors_pie = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B']
        
        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker_colors=colors_pie)])
        fig_pie.update_layout(
            title="Sample Diversified Portfolio",
            template="plotly_dark",
            height=350,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.success("💡 Don't put all eggs in one basket!")
    
    # ============== EGX GUIDE ==============
    elif topic == "🇪🇬 EGX Guide":
        st.markdown("""
        ### Egyptian Exchange (EGX)
        One of the oldest exchanges in the Middle East (Est. 1883)
        """)
        
        st.subheader("⏰ Trading Hours")
        st.markdown("""
        | Day | Status |
        |-----|--------|
        | Sunday | ✅ Open |
        | Monday | ✅ Open |
        | Tuesday | ✅ Open |
        | Wednesday | ✅ Open |
        | Thursday | ✅ Open |
        | Friday | ❌ Closed |
        | Saturday | ❌ Closed |
        
        **Trading Time:** 10:00 AM - 2:30 PM
        """)
        
        # EGX Indices
        st.subheader("📊 Main Indices Performance (Sample)")
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        egx30 = [25000, 25500, 26200, 25800, 27000, 28000]
        egx70 = [3000, 3100, 3250, 3180, 3300, 3450]
        
        fig_idx = go.Figure()
        fig_idx.add_trace(go.Scatter(x=months, y=egx30, name="EGX 30", line=dict(color='#00ff88', width=3)))
        fig_idx.update_layout(
            title="EGX 30 Index",
            template="plotly_dark",
            height=300,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_idx, use_container_width=True)
        
        # Sectors
        st.subheader("🏭 EGX Sectors")
        
        sectors = ['Banks', 'Real Estate', 'Food & Bev', 'Healthcare', 'FinTech', 'Construction']
        weights = [35, 20, 15, 12, 10, 8]
        
        fig_sectors = go.Figure()
        fig_sectors.add_trace(go.Bar(
            x=sectors,
            y=weights,
            marker_color=['#1e88e5', '#43a047', '#fb8c00', '#e53935', '#8e24aa', '#6d4c41'],
            text=[f"{w}%" for w in weights],
            textposition='auto'
        ))
        fig_sectors.update_layout(
            title="EGX Sector Weights",
            template="plotly_dark",
            height=300,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_sectors, use_container_width=True)
        
        st.subheader("🏦 Popular Brokers")
        st.markdown("""
        | Broker | Type |
        |--------|------|
        | EFG Hermes | Full Service |
        | CI Capital | Full Service |
        | Beltone | Full Service |
        | Arabeya Online | Online |
        | Mubasher Trade | Online |
        """)
        
        st.info("💡 Start with a reputable broker and small amounts!")

# Footer
st.markdown("---")
st.markdown("<center>Built with ❤️ for Egyptian Investors</center>", unsafe_allow_html=True)