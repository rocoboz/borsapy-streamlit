import streamlit as st
import borsapy as bp
from utils.ui import render_header

def app():
    render_header("Vadeli İşlemler (VİOP)", "Hisse, Endeks, Döviz ve Emtia Vadeli Sözleşmeleri")
    
    st.info("Borsa İstanbul Vadeli İşlem ve Opsiyon Piyasası verileri")
    
    try:
        v = bp.VIOP()
        
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Hisse Vadeli", "📊 Endeks Vadeli", "💵 Döviz Vadeli", "🥇 Emtia Vadeli"])
        
        with tab1:
            st.subheader("Hisse Senedi Vadeli Sözleşmeleri")
            try:
                df = v.stock_futures
                if df is not None and not df.empty:
                    st.dataframe(df, width="stretch")
                else:
                    st.info("Veri bulunamadı.")
            except Exception as e:
                st.error(f"Hata: {e}")
                
        with tab2:
            st.subheader("Endeks Vadeli Sözleşmeleri")
            try:
                df = v.index_futures
                if df is not None and not df.empty:
                    st.dataframe(df, width="stretch")
                else:
                    st.info("Veri bulunamadı.")
            except Exception as e:
                st.error(f"Hata: {e}")
                
        with tab3:
            st.subheader("Döviz Vadeli Sözleşmeleri")
            try:
                df = v.currency_futures
                if df is not None and not df.empty:
                    st.dataframe(df, width="stretch")
                else:
                    st.info("Veri bulunamadı.")
            except Exception as e:
                st.error(f"Hata: {e}")
                
        with tab4:
            st.subheader("Emtia Vadeli Sözleşmeleri")
            try:
                df = v.commodity_futures
                if df is not None and not df.empty:
                    st.dataframe(df, width="stretch")
                else:
                    st.info("Veri bulunamadı.")
            except Exception as e:
                st.error(f"Hata: {e}")
                
    except Exception as e:
        st.error(f"VİOP modülü yüklenirken hata oluştu: {e}")
