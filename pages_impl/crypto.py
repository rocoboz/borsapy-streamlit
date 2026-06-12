import streamlit as st
import borsapy as bp
import plotly.graph_objects as go
from utils.ui import render_header, metric_card
from utils.data_loader import get_crypto_list
from streamlit_searchbox import st_searchbox

def app():
    render_header("Kripto Piyasası", "Canlı Kripto Para Verileri (BtcTurk)")
    
    # Search Function
    def search_crypto(searchterm: str):
        pairs = get_crypto_list()
        if not pairs:
            return []
        
        if not searchterm:
            return pairs # Show all if empty query initially or handle differently
            
        searchterm = searchterm.upper()
        return [p for p in pairs if searchterm in p]

    # Use Searchbox
    selected_pair = st_searchbox(
        search_crypto,
        key="crypto_searchbox",
        label="Parite Ara",
        placeholder="Kripto parite giriniz (örn: BTC)",
        clear_on_submit=True,
    )
    
    # State management
    if "selected_crypto_pair" not in st.session_state:
        st.session_state.selected_crypto_pair = "BTCTRY"
        
    if selected_pair:
        st.session_state.selected_crypto_pair = selected_pair
        
    selected = st.session_state.selected_crypto_pair
    
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
