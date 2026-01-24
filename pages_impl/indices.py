import streamlit as st
import borsapy as bp
from utils.ui import render_header
from utils.data_loader import get_all_indices
import plotly.express as px

def app():
    render_header("Endeksler", "Borsa İstanbul Endeksleri")
    
    indices = get_all_indices()
    
    # Dropdown for Index Selection
    # indices is list of dicts: {'symbol': 'XU100', 'name': '...', ...}
    
    index_options = {i['symbol']: i['name'] for i in indices}
    selected_code = st.selectbox("Endeks Seçiniz", list(index_options.keys()), index=0)
    
    if selected_code:
        st.caption(f"{selected_code} - {index_options[selected_code]}")
        
        idx = None
        try:
            idx = bp.Index(selected_code)
        except Exception as e:
            st.error(f"Endeks bağlantı hatası: {str(e)}")
            
        if idx:
            # Chart Section
            st.subheader("Endeks Performansı")
            try:
                df = idx.history(period="1y")
                if not df.empty:
                    fig = px.line(df, x=df.index, y="Close", title=f"{selected_code} Günlük Kapanış")
                    fig.update_layout(template="plotly_dark")
                    st.plotly_chart(fig)
                else:
                    st.info("Bu endeks için grafik verisi görüntülenemiyor.")
            except Exception as e:
                st.warning(f"Grafik verisi alınamadı: {str(e)}")
            
            # Components Section
            try:
                with st.expander("Endeks Bileşenleri (Hisseler)", expanded=True):
                    comps = idx.components
                    if comps:
                        st.table(comps)
                    else:
                        st.info("Bileşen listesi çekilemedi.")
            except Exception as e:
                st.warning(f"Bileşen listesi alınamadı: {str(e)}")
