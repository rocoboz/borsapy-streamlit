import streamlit as st
import borsapy as bp
import plotly.graph_objects as go
from utils.ui import render_header, metric_card

def app():
    render_header("Kripto Piyasası", "Canlı Kripto Para Verileri (BtcTurk)")
    
    pairs = ["BTCTRY", "ETHTRY", "SOLTRY", "AVAXTRY", "USDTTRY"]
    selected = st.selectbox("Parite Seçiniz", pairs)
    
    if selected:
        try:
            c = bp.Crypto(selected)
            curr = c.current
            # Handle if curr is dict
            price = curr.get('last') if isinstance(curr, dict) else curr
            chg = curr.get('change_percent', 0) if isinstance(curr, dict) else 0
            
            metric_card(selected, f"{price} ₺", f"%{chg}", icon="🪙")
            
            # Chart
            hist = c.history(period="1mo")
            if not hist.empty:
                fig = go.Figure(data=[go.Candlestick(x=hist.index,
                                open=hist['Open'],
                                high=hist['High'],
                                low=hist['Low'],
                                close=hist['Close'])])
                fig.update_layout(template="plotly_dark", title=f"{selected} 1 Aylık Grafik")
                st.plotly_chart(fig)
                
        except Exception as e:
            st.error(f"Veri hatası: {str(e)}")
