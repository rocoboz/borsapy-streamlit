import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from utils.ui import render_header
from utils.data_loader import get_stock_history
import borsapy.technical as ta

def run_backtest(df, initial_capital, rsi_period, rsi_lower, rsi_upper):
    """
    Simple RSI Backtest Engine
    """
    # Calculate Indicators
    df['RSI'] = ta.calculate_rsi(df, period=rsi_period)
    
    # Logic
    capital = initial_capital
    position = 0 # shares
    
    trades = []
    equity_curve = []
    
    for i in range(len(df)):
        if i < rsi_period: 
            equity_curve.append(capital)
            continue
            
        price = df['Close'].iloc[i]
        date = df.index[i]
        rsi = df['RSI'].iloc[i]
        
        # Buy Signal
        if rsi < rsi_lower and position == 0:
            shares = capital / price
            position = shares
            capital = 0
            trades.append({
                "Date": date, "Type": "BUY", "Price": price, "Shares": shares, "Value": shares * price
            })
            
        # Sell Signal
        elif rsi > rsi_upper and position > 0:
            capital = position * price
            trades.append({
                "Date": date, "Type": "SELL", "Price": price, "Shares": position, "Value": capital
            })
            position = 0
            
        # Record Equity
        current_equity = capital + (position * price)
        equity_curve.append(current_equity)
        
    df['Equity'] = equity_curve
    return df, pd.DataFrame(trades)

def app():
    render_header("Araçlar (Beta)", "Backtest ve Market Replay")
    
    tab1, tab2 = st.tabs(["⚙️ Backtest", "⏪ Market Replay"])
    
    # --- Backtest Tab ---
    with tab1:
        st.subheader("RSI Strateji Testi")
        
        c1, c2, c3, c4 = st.columns(4)
        symbol = c1.text_input("Sembol", "THYAO", key="bt_sym").upper()
        period = c2.selectbox("Veri Aralığı", ["1y", "2y", "5y"], index=0)
        capital = c3.number_input("Başlangıç Sermayesi", 10000, 1000000, 100000)
        
        c_rsi_l, c_rsi_u = st.columns(2)
        rsi_lower = c_rsi_l.slider("RSI Alt Sınır (AL)", 10, 50, 30)
        rsi_upper = c_rsi_u.slider("RSI Üst Sınır (SAT)", 50, 90, 70)
        
        if st.button("Testi Başlat", type="primary"):
            with st.spinner("Backtest çalışıyor..."):
                df = get_stock_history(symbol, period=period)
                if df.empty:
                    st.error("Veri alınamadı.")
                else:
                    df_res, trades = run_backtest(df, capital, 14, rsi_lower, rsi_upper)
                    
                    # Results
                    final_equity = df_res['Equity'].iloc[-1]
                    profit = final_equity - capital
                    profit_pct = (profit / capital) * 100
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Sonuç Sermaye", f"{final_equity:,.2f} ₺")
                    m2.metric("Net Kar", f"{profit:,.2f} ₺", delta=f"%{profit_pct:.2f}")
                    m3.metric("İşlem Sayısı", len(trades))
                    
                    # Charts
                    st.line_chart(df_res['Equity'])
                    
                    with st.expander("İşlem Geçmişi"):
                        st.dataframe(trades)

    # --- Replay Tab ---
    with tab2:
        st.info("Geçmiş piyasa verilerini simüle edin.")
        
        col_sym, col_spd = st.columns(2)
        rep_sym = col_sym.text_input("Sembol", "GARAN", key="rep_sym_input").upper()
        
        if 'replay_data' not in st.session_state:
            st.session_state.replay_data = None
            st.session_state.replay_index = 0
            
        if st.button("Verileri Yükle / Sıfırla"):
            df = get_stock_history(rep_sym, period="3mo")
            if not df.empty:
                st.session_state.replay_data = df
                st.session_state.replay_index = 20 # Start with some data
                st.success(f"{len(df)} mum yüklendi.")
            else:
                st.error("Veri yok.")
                
        if st.session_state.replay_data is not None:
            df = st.session_state.replay_data
            idx = st.session_state.replay_index
            
            # Controls
            c_prev, c_play, c_next = st.columns([1,1,1])
            if c_next.button("İleri ⏩"):
                if idx < len(df) - 1:
                    st.session_state.replay_index += 1
                    st.rerun()
            
            # Display
            current_slice = df.iloc[:st.session_state.replay_index+1]
            last_candle = current_slice.iloc[-1]
            
            st.metric("Tarih", str(last_candle.name.date()), f"{last_candle['Close']:.2f} ₺")
            
            fig = go.Figure(data=[go.Candlestick(x=current_slice.index,
                            open=current_slice['Open'],
                            high=current_slice['High'],
                            low=current_slice['Low'],
                            close=current_slice['Close'])])
            fig.update_layout(height=400, template="plotly_dark", title=f"{rep_sym} Replay")
            st.plotly_chart(fig)
