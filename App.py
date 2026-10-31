import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
import requests
import time

# ==========================================
# 1. PAGE SETUP
# ==========================================
st.set_page_config(
    page_title="Shayan Trading Dashboard", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. THEME SELECTION & CSS INJECTION
# ==========================================
# Theme selector in the sidebar
st.sidebar.markdown("<h2 style='text-align: center; color: inherit;'>🎨 UI THEME</h2>", unsafe_allow_html=True)
selected_theme = st.sidebar.radio(
    "Select Terminal Theme:",
    ["Midnight Dark (Pro)", "Clean Light (Day)", "Cyberpunk Neon"]
)
st.sidebar.markdown("<hr style='border-color: gray; opacity: 0.3;'>", unsafe_allow_html=True)

# Define CSS based on the selected theme
if selected_theme == "Midnight Dark (Pro)":
    custom_css = """
        .stApp { background-color: #0B0E14 !important; color: #E0E6ED !important; }
        [data-testid="stSidebar"] { background-color: #121621 !important; border-right: 1px solid #1E2330 !important; }
        [data-testid="stSidebar"] * { color: #E0E6ED !important; }
        div.stButton > button:first-child { background: linear-gradient(90deg, #00C853 0%, #00E676 100%); color: white; border: none; font-weight: bold; border-radius: 6px; }
        [data-testid="metric-container"] { background-color: #161A25 !important; border: 1px solid #232838 !important; border-left: 4px solid #2979FF !important; border-radius: 8px !important; }
        [data-testid="stMetricValue"] { color: #FFFFFF !important; }
        [data-testid="stDataFrame"] { background-color: #161A25; border: 1px solid #232838; border-radius: 8px; }
        h1, h2, h3, p { color: #E0E6ED !important; }
    """
elif selected_theme == "Clean Light (Day)":
    custom_css = """
        .stApp { background-color: #F5F7FA !important; color: #1E2330 !important; }
        [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; }
        [data-testid="stSidebar"] * { color: #1E2330 !important; }
        div.stButton > button:first-child { background: linear-gradient(90deg, #2979FF 0%, #448AFF 100%); color: white; border: none; font-weight: bold; border-radius: 6px; }
        [data-testid="metric-container"] { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-left: 4px solid #2979FF !important; border-radius: 8px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important; }
        [data-testid="stMetricValue"] { color: #1E2330 !important; }
        [data-testid="stDataFrame"] { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; }
        h1, h2, h3, p { color: #1E2330 !important; }
        .stTabs [data-baseweb="tab"] { color: #1E2330 !important; }
    """
else: # Cyberpunk Neon
    custom_css = """
        .stApp { background-color: #090412 !important; color: #E0E6ED !important; }
        [data-testid="stSidebar"] { background-color: #10061E !important; border-right: 1px solid #2D0B5A !important; }
        [data-testid="stSidebar"] * { color: #00E5FF !important; }
        div.stButton > button:first-child { background: linear-gradient(90deg, #D500F9 0%, #FF1744 100%); color: white; border: none; font-weight: bold; border-radius: 6px; box-shadow: 0 0 15px rgba(213, 0, 249, 0.4); }
        [data-testid="metric-container"] { background-color: #120726 !important; border: 1px solid #2D0B5A !important; border-left: 4px solid #00E5FF !important; border-radius: 8px !important; box-shadow: 0 0 10px rgba(0, 229, 255, 0.1) !important; }
        [data-testid="stMetricValue"] { color: #00E5FF !important; text-shadow: 0 0 5px rgba(0,229,255,0.5) !important; }
        [data-testid="stDataFrame"] { background-color: #120726; border: 1px solid #2D0B5A; border-radius: 8px; }
        h1 { color: #00E5FF !important; text-shadow: 0 0 10px rgba(0, 229, 255, 0.5) !important; }
        h2, h3, p { color: #E0E6ED !important; }
    """

st.markdown(f"""
<style>
    /* Injecting Selected Theme CSS */
    {custom_css}
    
    /* Common UI Improvements */
    div.stButton > button:first-child {{ padding: 12px 24px; text-transform: uppercase; transition: all 0.3s ease; }}
    div.stButton > button:first-child:hover {{ transform: translateY(-2px); }}
    [data-testid="metric-container"] {{ padding: 15px 20px !important; transition: all 0.3s ease; }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. TITLE & HEADER SECTION (New Branding)
# ==========================================
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>⚡ SHAYAN TRADING DASHBOARD</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 14px; letter-spacing: 2px; text-transform: uppercase;'>Institutional-Grade Algorithmic Terminal</p>", unsafe_allow_html=True)
st.divider()

exchange = ccxt.binance()

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================
@st.cache_data(ttl=3600)
def get_fear_and_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1")
        data = r.json()
        return int(data['data'][0]['value']), data['data'][0]['value_classification']
    except Exception:
        return 50, "Neutral"

@st.cache_data(ttl=1800)
def get_top_volume_coins(limit=30):
    tickers = exchange.fetch_tickers()
    usdt_pairs = sorted(
        [{'symbol': s, 'vol': t['quoteVolume']} for s, t in tickers.items() if s.endswith('/USDT') and t['quoteVolume'] is not None],
        key=lambda x: x['vol'], reverse=True
    )
    return [coin['symbol'] for coin in usdt_pairs[:limit]]

def fetch_data(symbol, tf, lim):
    for _ in range(3):
        try:
            return exchange.fetch_ohlcv(symbol, timeframe=tf, limit=lim)
        except Exception:
            time.sleep(1)
    return None

def apply_all_indicators(df):
    df.ta.ema(length=200, append=True)
    df.ta.macd(append=True)
    df.ta.rsi(length=14, append=True)
    df.ta.atr(length=14, append=True)
    df.ta.adx(length=14, append=True)
    df.ta.mfi(length=14, append=True) 
    df.ta.supertrend(length=10, multiplier=3.0, append=True) 
    df.ta.bbands(length=20, std=2.0, append=True) 
    df['Vol_SMA'] = df['volume'].rolling(20).mean()
    return df

def get_col(df, partial_name):
    return [c for c in df.columns if c.startswith(partial_name)][0]

# ==========================================
# 5. SIDEBAR SETTINGS
# ==========================================
st.sidebar.markdown("<h2 style='text-align: center;'>⚙️ SETTINGS</h2>", unsafe_allow_html=True)
top_n = st.sidebar.selectbox("🎯 Target Coins to Scan", [10, 20, 50, 100], index=1)
entry_tf = st.sidebar.selectbox("⏱️ Trading Timeframe", ['15m', '30m', '1h', '4h'], index=2)

st.sidebar.markdown("<br><hr style='border-color: gray; opacity: 0.3;'>", unsafe_allow_html=True)
st.sidebar.info("💡 Pro Tip: Run this terminal on a desktop browser or rotate your mobile to landscape for the best UI experience.")

# ==========================================
# 6. TABS
# ==========================================
tab_scanner, tab_backtest = st.tabs(["🚀 LIVE MARKET SCANNER", "📊 STRATEGY BACKTEST"])

# ==========================================
# TAB 1: LIVE SCANNER
# ==========================================
with tab_scanner:
    
    fng_val, fng_status = get_fear_and_greed()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Market Sentiment", value=fng_status, delta=f"Index: {fng_val}", delta_color="off")
    with col2:
        st.metric(label="Active Timeframe", value=entry_tf)
    with col3:
        st.metric(label="Target Volume", value=f"Top {top_n} Pairs")
        
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("⚡ EXECUTE PRO MARKET SCAN", use_container_width=True):
        coins_to_scan = get_top_volume_coins(top_n)
        
        with st.status(f"Scanning Top {top_n} Assets with AI Indicators...", expanded=True) as status:
            generated_signals = []
            progress_bar = st.progress(0)
            
            for idx, symbol in enumerate(coins_to_scan):
                progress_bar.progress((idx + 1) / len(coins_to_scan))
                
                bars = fetch_data(symbol, entry_tf, 250)
                if not bars: continue
                
                df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df = apply_all_indicators(df)
                
                curr, prev = df.iloc[-2], df.iloc[-3]
                c_price, ema, atr, mfi = curr['close'], curr['EMA_200'], curr['ATRr_14'], curr['MFI_14']
                st_dir, bb_mid = curr[get_col(df, 'SUPERTd')], curr[get_col(df, 'BBM')]
                
                bull_cross = (prev['MACD_12_26_9'] < prev['MACDs_12_26_9']) and (curr['MACD_12_26_9'] > curr['MACDs_12_26_9'])
                bear_cross = (prev['MACD_12_26_9'] > prev['MACDs_12_26_9']) and (curr['MACD_12_26_9'] < curr['MACDs_12_26_9'])
                vol_ok = curr['volume'] > curr['Vol_SMA']
                
                # 🟢 LONG SIGNAL
                if (bull_cross and (c_price > ema) and (40 <= curr['RSI_14'] <= 60) and 
                   (curr['ADX_14'] > 20) and vol_ok and (st_dir == 1) and (mfi < 80) and (c_price > bb_mid)):
                    if fng_val >= 25 or symbol == 'BTC/USDT': 
                        generated_signals.append({
                            "Asset": symbol, "Signal": "🟢 BUY (LONG)", "Entry Price": f"${c_price:.4f}",
                            "Stop Loss": f"${(c_price - (1.5*atr)):.4f}", "Take Profit 1": f"${(c_price + (1.5*atr)):.4f}", 
                            "Take Profit 2": f"${(c_price + (4.0*atr)):.4f}"
                        })
                        
                # 🔴 SHORT SIGNAL
                elif (bear_cross and (c_price < ema) and (40 <= curr['RSI_14'] <= 60) and 
                     (curr['ADX_14'] > 20) and vol_ok and (st_dir == -1) and (mfi > 20) and (c_price < bb_mid)):
                    generated_signals.append({
                        "Asset": symbol, "Signal": "🔴 SELL (SHORT)", "Entry Price": f"${c_price:.4f}",
                        "Stop Loss": f"${(c_price + (1.5*atr)):.4f}", "Take Profit 1": f"${(c_price - (1.5*atr)):.4f}",
                        "Take Profit 2": f"${(c_price - (4.0*atr)):.4f}"
                    })
            
            progress_bar.empty()
            status.update(label="Market Analysis Complete!", state="complete", expanded=False)
        
        if generated_signals:
            st.success(f"🎯 Successfully found {len(generated_signals)} High-Probability Setups!")
            res_df = pd.DataFrame(generated_signals)
            st.dataframe(res_df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ No valid setups found right now. Algorithm blocked risky trades.")

# ==========================================
# TAB 2: BACKTESTING ENGINE
# ==========================================
with tab_backtest:
    st.markdown("<h3>🔍 Asset Historical Performance</h3>", unsafe_allow_html=True)
    
    with st.form("backtest_form"):
        b_col1, b_col2 = st.columns(2)
        test_coin = b_col1.text_input("Asset Ticker (e.g., BTC/USDT)", "BTC/USDT")
        test_tf = b_col2.selectbox("Backtest Timeframe", ['15m', '1h', '4h', '1d'], index=1)
        run_btn = st.form_submit_button("RUN STRATEGY TEST", use_container_width=True)
        
    if run_btn:
        with st.spinner(f"Simulating past 1000 candles for {test_coin}..."):
            bars = fetch_data(test_coin, test_tf, 1000)
            if bars:
                df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df = apply_all_indicators(df)
                
                wins, losses = 0, 0
                in_trade, t_type, tp, sl = False, None, 0, 0
                st_col = get_col(df, 'SUPERTd')
                bbm_col = get_col(df, 'BBM')
                
                for i in range(1, len(df)-1):
                    c, p = df.iloc[i], df.iloc[i-1]
                    price = c['close']
                    
                    if in_trade:
                        if t_type == 'LONG':
                            if price >= tp: wins+=1; in_trade=False
                            elif price <= sl: losses+=1; in_trade=False
                        elif t_type == 'SHORT':
                            if price <= tp: wins+=1; in_trade=False
                            elif price >= sl: losses+=1; in_trade=False
                    else:
                        bull = (p['MACD_12_26_9'] < p['MACDs_12_26_9']) and (c['MACD_12_26_9'] > c['MACDs_12_26_9'])
                        bear = (p['MACD_12_26_9'] > p['MACDs_12_26_9']) and (c['MACD_12_26_9'] < c['MACDs_12_26_9'])
                        st_dir, bb_mid, mfi = c[st_col], c[bbm_col], c['MFI_14']
                        
                        if bull and (price > c['EMA_200']) and (40 <= c['RSI_14'] <= 60) and (st_dir == 1) and (mfi < 80) and (price > bb_mid):
                            in_trade, t_type, sl, tp = True, 'LONG', price - (1.5*c['ATRr_14']), price + (3.0*c['ATRr_14'])
                        elif bear and (price < c['EMA_200']) and (40 <= c['RSI_14'] <= 60) and (st_dir == -1) and (mfi > 20) and (price < bb_mid):
                            in_trade, t_type, sl, tp = True, 'SHORT', price + (1.5*c['ATRr_14']), price - (3.0*c['ATRr_14'])
                
                tot = wins + losses
                wr = (wins/tot*100) if tot > 0 else 0
                
                st.markdown("<br>", unsafe_allow_html=True)
                r1, r2, r3 = st.columns(3)
                r1.metric("Total Trades Taken", tot)
                r2.metric("Winning Trades", wins)
                r3.metric("Win Rate (%)", f"{wr:.1f}%")
            else:
                st.error("Failed to fetch data. Please verify the asset ticker.")
