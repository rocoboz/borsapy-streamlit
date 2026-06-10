import streamlit as st
import borsapy as bp
from utils.ui import render_header

def app():
    render_header("Tahvil ve Bono", "Devlet İç Borçlanma Senetleri ve Eurobondlar")
    
    st.info("Güncel tahvil, bono ve eurobond faiz/fiyat verileri")
    
    tab1, tab2 = st.tabs(["🏛️ DİBS (Devlet Tahvilleri)", "🌍 Eurobondlar"])
    
    with tab1:
        st.subheader("Devlet İç Borçlanma Senetleri")
        try:
            df = bp.bonds()
            if df is not None and not df.empty:
                st.dataframe(df, width="stretch")
            else:
                st.info("Veri bulunamadı.")
        except Exception as e:
            st.error(f"Hata: {e}")
            
    with tab2:
        st.subheader("Eurobondlar")
        try:
            df = bp.eurobonds()
            if df is not None and not df.empty:
                st.dataframe(df, width="stretch")
            else:
                st.info("Veri bulunamadı.")
        except Exception as e:
            st.error(f"Hata: {e}")
