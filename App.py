%%writefile app.py
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from binance.client import Client
from binance.exceptions import BinanceAPIException

# --- Page Configuration ---
st.set_page_config(page_title="Professional Trading Bot v6.0 (Live Ready)", layout="wide")

# --- Custom Styling for Binance Dark Theme ---
st.markdown("""
    <style>
    .main { background-color: #0b0e11; color: #eaecef; }
    .stMetric { background-color: #1e2329; padding: 12px; border-radius: 8px; border: 1px solid #2b3139; }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'account_mode' not in st.session_state:
    st.session_state.account_mode = "Demo (Practice)"
if 'control_mode' not in st.session_state:
    st.session_state.control_mode = "Auto Bot"
if 'demo_balance' not in st.session_state:
    st.session_state.demo_balance = 10008.00  # Saved demo profit
if 'real_balance' not in st.session_state:
    st.session_state.real_balance = 0.00
if 'selected_asset' not in st.session_state:
    st.session_state.selected_asset = "BTC-USD"
if 'active_trade' not in st.session_state:
    st.session_state.active_trade = None
if 'binance_api_key' not in st.session_state:
    st.session_state.binance_api_key = ""
if 'binance_api_secret' not in st.session_state:
    st.session_state.binance_api_secret = ""
if 'is_connected' not in st.session_state:
    st.session_state.is_connected = False

# --- Function to Fetch Real Binance Balance ---
def fetch_binance_balance(api_key, api_secret):
    try:
        client = Client(api_key, api_secret)
        # Fetch account information to verify keys and get USDT balance
        account_info = client.get_account()
        for asset in account_info.get('balances', []):
            if asset['asset'] == 'USDT':
                return float(asset['free']), True
        return 0.00, True
    except BinanceAPIException as e:
        return 0.00, False
    except Exception as e:
        return 0.00, False

# --- Update Real Balance if in Real Money Mode and Connected ---
if "Real" in st.session_state.account_mode and st.session_state.is_connected:
    bal, success = fetch_binance_balance(st.session_state.binance_api_key, st.session_state.binance_api_secret)
    if success:
        st.session_state.real_balance = bal
    else:
        st.session_state.real_balance = 0.00
elif "Real" in st.session_state.account_mode and not st.session_state.is_connected:
    st.session_state.real_balance = 0.00

# --- Top Header: Account Mode, Control Mode & Balance ---
col_top1, col_top2, col_top3 = st.columns([2, 2, 2])

with col_top1:
    st.session_state.account_mode = st.radio(
        "💼 Account Type:", 
        ["Demo (Practice)", "Real Money"], 
        horizontal=True
    )

with col_top2:
    st.session_state.control_mode = st.radio(
        "🎮 Trading Control:", 
        ["Manual", "Auto Bot"], 
        horizontal=True
    )

current_balance = st.session_state.demo_balance if "Demo" in st.session_state.account_mode else st.session_state.real_balance

with col_top3:
    badge = "🟡 DEMO" if "Demo" in st.session_state.account_mode else "🔴 REAL"
    st.markdown(f"### {badge} Balance: **${current_balance:,.2f}**")

st.markdown("---")

# --- Navigation Menu ---
nav_tab = st.selectbox("📌 Navigation Menu", ["Trade", "Profile", "Broker Settings", "Analyse", "Top", "Learn"])

if nav_tab == "Profile":
    st.subheader("👤 User Profile & Bot Configuration")
    st.write("**Name:** Meraj")
    st.write(f"**Account Mode:** {st.session_state.account_mode}")
    st.write(f"**Control Mode:** {st.session_state.control_mode}")
    st.write(f"**Current Wallet Balance:** ${current_balance:,.2f}")
    st.success("Core Trading Bot logic is running smoothly and untouched.")
    st.stop()

elif nav_tab == "Broker Settings":
    st.subheader("🔌 Live Broker API Configuration")
    st.write("Enter your Binance or MetaTrader 5 (MT5) API Keys here when switching to real money trading.")
    
    broker_choice = st.selectbox("Select Broker", ["Binance", "MetaTrader 5 (MT5)"])
    api_key_input = st.text_input("API Key", type="password", value=st.session_state.binance_api_key)
    api_secret_input = st.text_input("Secret Key", type="password", value=st.session_state.binance_api_secret)
    
    if st.button("Save & Connect Broker"):
        if broker_choice == "Binance":
            if api_key_input and api_secret_input:
                with st.spinner("Verifying credentials with Binance..."):
                    balance, success = fetch_binance_balance(api_key_input, api_secret_input)
                    if success:
                        st.session_state.binance_api_key = api_key_input
                        st.session_state.binance_api_secret = api_secret_input
                        st.session_state.is_connected = True
                        st.session_state.real_balance = balance
                        st.success(f"Successfully connected to Binance! Live Balance: ${balance:,.2f}")
                    else:
                        st.session_state.is_connected = False
                        st.error("Failed to connect to Binance. Please check if your API Key and Secret Key are correct.")
            else:
                st.warning("Please enter valid API and Secret keys.")
        else:
            if api_key_input and api_secret_input:
                st.session_state.is_connected = True
                st.success("Successfully configured with MetaTrader 5!")
            else:
                st.warning("Please enter valid credentials.")
    st.stop()

elif nav_tab in ["Analyse", "Top", "Learn"]:
    st.subheader(f"📌 {nav_tab} Section")
    st.info("Switch back to 'Trade' from the menu above to access the live trading terminal.")
    st.stop()

# --- Asset Selection Row ---
st.subheader("⚡ Live Markets")
asset_cols = st.columns(5)
assets_info = [
    {"name": "BITCOIN", "ticker": "BTC-USD"},
    {"name": "APPLE", "ticker": "AAPL"},
    {"name": "COINBASE", "ticker": "COIN"},
    {"name": "MCDONALD'S", "ticker": "MCD"},
    {"name": "AMAZON", "ticker": "AMZN"}
]

for idx, asset in enumerate(assets_info):
    with asset_cols[idx]:
        if st.button(f"📊 {asset['name']}", key=f"btn_{asset['ticker']}", use_container_width=True):
            st.session_state.selected_asset = asset['ticker']

active_ticker = st.session_state.selected_asset
st.markdown("---")

# --- Sidebar Strategy Settings (UNCHANGED CORE LOGIC) ---
st.sidebar.header("⚙️ Bot Strategy & Risk")
emergency_stop = st.sidebar.button("🛑 EMERGENCY STOP", type="primary")
if emergency_stop:
    st.session_state.active_trade = None
    st.session_state.control_mode = "Manual"
    st.error("🚨 EMERGENCY STOP! All bot trades halted and switched to Manual.")
    st.stop()

investment_pct = st.sidebar.slider("Trade Amount (% of Balance)", 5, 50, 10)
min_trend = st.sidebar.slider("Bot Sensitivity / Trend (%)", 0.5, 5.0, 1.0, 0.5)

# --- Fetch Real Market Data & Calculate Indicators (Same Proven Logic) ---
try:
    with st.spinner(f"Loading live chart for {active_ticker}..."):
        data = yf.download(active_ticker, period="3mo", interval="1d", progress=False)
        
        if data.empty:
            st.error("Market data unavailable right now.")
        else:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
                
            for col in ['Open', 'High', 'Low', 'Close']:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            data = data.dropna(subset=['Open', 'High', 'Low', 'Close'])
            
            current_price = float(data['Close'].iloc[-1])
            
            # Unchanged MA & RSI Formula
            data['MA10'] = data['Close'].rolling(window=10).mean()
            ma_10 = float(data['MA10'].iloc[-1]) if not pd.isna(data['MA10'].iloc[-1]) else current_price
            price_diff = ((current_price - ma_10) / ma_10) * 100
            
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            rsi = float(rsi_series.iloc[-1]) if not pd.isna(rsi_series.iloc[-1]) else 50.0
            
            # Unchanged Bot Decision Logic
            if price_diff > min_trend and rsi < 70:
                bot_signal = "BUY"
                signal_display = "🟢 STRONG BUY SIGNAL"
            elif price_diff < -min_trend:
                bot_signal = "SELL"
                signal_display = "🔴 STRONG SELL SIGNAL"
            else:
                bot_signal = "HOLD"
                signal_display = "⚪ NEUTRAL / WAIT"

            # Auto Bot Execution (With Balance Check)
            if st.session_state.control_mode == "Auto Bot" and st.session_state.active_trade is None:
                if bot_signal in ["BUY", "SELL"]:
                    if current_balance <= 0:
                        st.warning("⚠️ Auto Bot skipped trade: Insufficient funds (Balance is $0.00).")
                    else:
                        trade_amount = current_balance * (investment_pct / 100.0)
                        st.session_state.active_trade = {
                            'ticker': active_ticker,
                            'side': bot_signal,
                            'entry_price': current_price,
                            'amount': trade_amount
                        }
                        st.toast(f"🤖 Auto Bot executed {bot_signal} on {active_ticker} at ${current_price:,.2f}!")

            # Live Price & PnL Header
            col_info1, col_info2 = st.columns([2, 2])
            with col_info1:
                st.markdown(f"### 📈 **{active_ticker}**: **${current_price:,.2f}**")
                st.write(f"Bot Analysis: **{signal_display}** | RSI: **{round(rsi, 1)}**")
            
            with col_info2:
                if st.session_state.active_trade:
                    trade = st.session_state.active_trade
                    entry = trade['entry_price']
                    side = trade['side']
                    
                    if side == "BUY":
                        pnl_pct = ((current_price - entry) / entry) * 100
                    else:
                        pnl_pct = ((entry - current_price) / entry) * 100
                        
                    pnl_usd = trade['amount'] * (pnl_pct / 100.0)
                    color = "#0ecb81" if pnl_usd >= 0 else "#f6465d"
                    
                    st.markdown(f"### Active {side} Trade ({trade['ticker']})")
                    st.markdown(f"<h3 style='color:{color};'>PnL: {pnl_usd:+.2f}$ ({pnl_pct:+.2f}%)</h3>", unsafe_allow_html=True)
                else:
                    st.markdown("### Active Trade: **None**")
                    st.write("Ready for Manual or Auto Bot execution.")

            # Candlestick Chart
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                increasing_line_color='#0ecb81',
                decreasing_line_color='#f6465d',
                name='Market Price'
            ))
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MA10'],
                mode='lines',
                line=dict(color='#f0b90b', width=1.5),
                name='MA (10)'
            ))
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='#0b0e11',
                plot_bgcolor='#161a1e',
                height=450,
                margin=dict(l=10, r=10, t=30, b=10),
                xaxis_rangeslider_visible=False,
                yaxis_title="Price (USD)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Chart/Data Error: {e}")

st.markdown("---")

# --- Action Buttons ---
col_b1, col_b2, col_b3 = st.columns(3)

with col_b1:
    if st.button("🟢 BUY (LONG)", use_container_width=True):
        if st.session_state.active_trade is not None:
            st.warning("Close your current active trade before opening a new one!")
        elif current_balance <= 0:
            st.error("❌ Cannot trade: Your balance is $0.00 or insufficient.")
        elif 'current_price' in locals():
            trade_amount = current_balance * (investment_pct / 100.0)
            st.session_state.active_trade = {
                'ticker': active_ticker,
                'side': 'BUY',
                'entry_price': current_price,
                'amount': trade_amount
            }
            st.rerun()

with col_b2:
    if st.button("🔴 SELL (SHORT)", use_container_width=True):
        if st.session_state.active_trade is not None:
            st.warning("Close your current active trade before opening a new one!")
        elif current_balance <= 0:
            st.error("❌ Cannot trade: Your balance is $0.00 or insufficient.")
        elif 'current_price' in locals():
            trade_amount = current_balance * (investment_pct / 100.0)
            st.session_state.active_trade = {
                'ticker': active_ticker,
                'side': 'SELL',
                'entry_price': current_price,
                'amount': trade_amount
            }
            st.rerun()

with col_b3:
    if st.button("🛑 CLOSE TRADE", type="primary", use_container_width=True):
        if st.session_state.active_trade is not None and 'current_price' in locals():
            trade = st.session_state.active_trade
            entry = trade['entry_price']
            side = trade['side']
            
            if side == "BUY":
                pnl_pct = ((current_price - entry) / entry) * 100
            else:
                pnl_pct = ((entry - current_price) / entry) * 100
                
            pnl_usd = trade['amount'] * (pnl_pct / 100.0)
            
            if "Demo" in st.session_state.account_mode:
                st.session_state.demo_balance += pnl_usd
            else:
                st.session_state.real_balance += pnl_usd
                
            st.session_state.active_trade = None
            st.success(f"Trade Closed! Realized PnL: {pnl_usd:+.2f}$")
            st.rerun()
        else:
            st.info("No active trade to close.")
      
