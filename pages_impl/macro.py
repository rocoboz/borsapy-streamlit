import streamlit as st
import borsapy as bp
import pandas as pd
from utils.ui import render_header, metric_card

def app():
    render_header("Makroekonomi", "Enflasyon ve Ekonomik Takvim")
    
    tab1, tab2 = st.tabs(["💰 Enflasyon", "📅 Ekonomik Takvim"])
    
    with tab1:
        st.subheader("Enflasyon Verileri (TÜFE/ÜFE)")
        try:
            inf = bp.Inflation()
            # Try to get latest data
            latest = inf.latest()
            
            # If latest returns a dict or dataframe, handle it
            if isinstance(latest, pd.DataFrame) and not latest.empty:
                # Assuming standard TUFE/UFE columns, let's display nicely
                st.dataframe(latest, width="stretch")
                
                # Metrics for top row if possible
                if 'TUFE_Yillik' in latest.columns:
                    val = latest['TUFE_Yillik'].iloc[0]
                    metric_card("TÜFE (Yıllık)", f"%{val:.2f}", icon="📉")
            elif isinstance(latest, dict) and latest:
                # Handle dictionary response
                c1, c2 = st.columns(2)
                
                yearly = latest.get('yearly_inflation')
                monthly = latest.get('monthly_inflation')
                
                with c1:
                    if yearly is not None:
                        metric_card("TÜFE (Yıllık)", f"%{yearly:.2f}", icon="📉")
                with c2:
                    if monthly is not None:
                        metric_card("TÜFE (Aylık)", f"%{monthly:.2f}", icon="📉")
                        
                st.dataframe(pd.DataFrame([latest]), width="stretch")

            else:
                st.info("Güncel enflasyon verisi alınamadı.")
                
        except Exception as e:
            st.error(f"Veri hatası: {str(e)}")
            st.info("Not: Enflasyon verisi TCMB kaynağından çekilmektedir.")

    with tab2:
        st.subheader("Ekonomik Takvim")
        try:
            # Check if economic_calendar is a function or property
            cal_data = bp.economic_calendar()
            
            if isinstance(cal_data, pd.DataFrame) and not cal_data.empty:
                st.dataframe(cal_data, width="stretch")
            elif isinstance(cal_data, list):
                st.dataframe(pd.DataFrame(cal_data), width="stretch")
            else:
                st.info("Takvim verisi boş.")
        except Exception as e:
            st.warning(f"Takvim verisi alınamadı: {str(e)}")
