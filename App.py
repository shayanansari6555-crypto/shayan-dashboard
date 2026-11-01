import streamlit as st
import ccxt
import pandas as pd

# 1. Page Configuration (Mobile Friendly)
st.set_page_config(page_title="SHAYAN TRADING DASHBOARD", layout="wide", initial_sidebar_state="expanded")

# 2. Sidebar & Theme Switcher
st.sidebar.title("⚙️ Settings")
theme = st.sidebar.radio("Select Theme", ["Midnight Dark", "Clean Light", "Cyberpunk Neon"])

# Theme Logic
if theme == "Midnight Dark":
    bg_color, text_color, chart_color = "#0E1117", "#FAFAFA", "#00FF00"
elif theme == "Clean Light":
    bg_color, text_color, chart_color = "#FFFFFF", "#000000", "#0000FF"
else:  # Cyberpunk Neon
    bg_color, text_color, chart_color = "#0D0221", "#00FF41", "#FF00FF"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    h1, h2, h3, p, label, div {{ color: {text_color} !important; }}
    </style>
""", unsafe_allow_html=True)

# 3. Main Title
st.title("🚀 SHAYAN TRADING DASHBOARD")
st.write("24/7 Live Crypto Market Monitoring")

# 4. Input Parameters
symbol = st.sidebar.text_input("Enter Coin Symbol", "BTC/USDT").upper()
timeframe = st.sidebar.selectbox("Select Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)

# 5. Manual Indicator Functions (No pandas-ta needed)
def calculate_sma(df, window):
    return df['close'].rolling(window=window).mean()

def calculate_rsi(df, window=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 6. Fetch Data and Display
@st.cache_data(ttl=60) # Cache for 60 seconds for mobile speed
def fetch_market_data(sym, tf):
    exchange = ccxt.binance()
    bars = exchange.fetch_ohlcv(sym, timeframe=tf, limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

try:
    with st.spinner(f"Fetching live data for {symbol}..."):
        df = fetch_market_data(symbol, timeframe)
        
        # Calculate Indicators Manually
        df['SMA_20'] = calculate_sma(df, 20)
        df['RSI_14'] = calculate_rsi(df, 14)
        
        # Display Current Price
        current_price = df['close'].iloc[-1]
        st.subheader(f"Current Price: ${current_price:,.2f}")
        
        # Display Chart
        st.line_chart(df.set_index('timestamp')['close'], color=chart_color)
        
        # Display Data Table
        st.write("### Market Data & Indicators")
        st.dataframe(df.tail(10).set_index('timestamp'), use_container_width=True)

except Exception as e:
    st.error("Error fetching data. Please check the coin symbol (e.g., BTC/USDT) or your internet connection.")
