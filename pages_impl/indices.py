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
        
        try:
            idx = bp.Index(selected_code)
            
            # Chart
            st.subheader("Endeks Performansı")
            df = idx.history(period="1y")
            
            if not df.empty:
                fig = px.line(df, x=df.index, y="Close", title=f"{selected_code} Günlük Kapanış")
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig)
            
            # Components
            with st.expander("Endeks Bileşenleri (Hisseler)"):
                comps = idx.components
                if comps:
                    st.table(comps)
                else:
                    st.info("Bileşen listesi çekilemedi.")
                    
        except Exception as e:
            st.error(f"Veri alınırken hata oluştu: {str(e)}")
