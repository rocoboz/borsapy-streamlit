import streamlit as st
import borsapy as bp
import plotly.graph_objects as go
from utils.ui import render_header
from utils.data_loader import get_stock_history

def app():
    render_header("Teknik Analiz", "İndikatörler ve Sinyaller")
    
    symbol = st.text_input("Analiz Edilecek Sembol", "THYAO").upper()
    
    if symbol:
        ticker = bp.Ticker(symbol)
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Göstergeler")
            rsi = st.checkbox("RSI (14)", value=True)
            sma = st.checkbox("SMA (20/50)", value=True)
            bb = st.checkbox("Bollinger Bands", value=True)
            macd = st.checkbox("MACD")
            
        with col2:
            st.subheader("Grafik")
            df = get_stock_history(symbol, period="1y")
            
            if not df.empty:
                fig = go.Figure()
                
                # Candlestick
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"))
                
                # Indicators
                if sma:
                    try:
                        sma20 = ticker.sma(sma_period=20)
                        # Note: borsapy returns value, we need series for chart. 
                        # Using manual calculation for chart viz or TechnicalAnalyzer if available
                        ta = ticker.technicals(period="1y")
                        fig.add_trace(go.Scatter(x=df.index, y=ta.sma(20), name="SMA 20", line=dict(color='orange')))
                        fig.add_trace(go.Scatter(x=df.index, y=ta.sma(50), name="SMA 50", line=dict(color='blue')))
                    except: pass
                    
                if bb:
                    try:
                        ta = ticker.technicals(period="1y")
                        bb_df = ta.bollinger_bands()
                        fig.add_trace(go.Scatter(x=df.index, y=bb_df['BB_Upper'], line=dict(color='gray', dash='dash'), name="BB Upper"))
                        fig.add_trace(go.Scatter(x=df.index, y=bb_df['BB_Lower'], line=dict(color='gray', dash='dash'), name="BB Lower", fill='tonexty'))
                    except: pass
                
                fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig)
                
                # RSI Chart below
                if rsi:
                    try:
                        ta = ticker.technicals(period="1y")
                        rsi_series = ta.rsi()
                        fig_rsi = go.Figure(go.Scatter(x=df.index, y=rsi_series, name="RSI"))
                        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                        fig_rsi.update_layout(template="plotly_dark", height=200, title="RSI", yaxis_range=[0,100])
                        st.plotly_chart(fig_rsi)
                    except: pass

        # Signals
        st.subheader("Teknik Sinyaller (Beta)")
        try:
            # Manual calculation since ta_signals is not available in this version
            ta = ticker.technicals(period="1y")
            
            # Fetch latest values
            last_rsi = ta.rsi().iloc[-1]
            last_sma20 = ta.sma(20).iloc[-1]
            last_sma50 = ta.sma(50).iloc[-1]
            current_price = ticker.fast_info.get('last_price', 0)
            
            signals_list = []
            
            # RSI Strategy
            if last_rsi < 30: signals_list.append(("RSI", "AL", f"RSI: {last_rsi:.2f} < 30"))
            elif last_rsi > 70: signals_list.append(("RSI", "SAT", f"RSI: {last_rsi:.2f} > 70"))
            else: signals_list.append(("RSI", "NÖTR", f"RSI: {last_rsi:.2f}"))
            
            # SMA Strategy
            if current_price > last_sma20: signals_list.append(("SMA 20", "AL", "Fiyat > SMA20"))
            else: signals_list.append(("SMA 20", "SAT", "Fiyat < SMA20"))
            
            # Golden Cross
            if last_sma20 > last_sma50: signals_list.append(("SMA Cross", "AL", "SMA20 > SMA50"))
            else: signals_list.append(("SMA Cross", "SAT", "SMA20 < SMA50"))
            
            # Display
            for ind, sig, desc in signals_list:
                color = "green" if sig == "AL" else "red" if sig == "SAT" else "gray"
                st.markdown(f"**{ind}**: :{color}[{sig}] - *{desc}*")
            
        except Exception as e:
            st.warning(f"Sinyal hesaplanamadı: {str(e)}")
