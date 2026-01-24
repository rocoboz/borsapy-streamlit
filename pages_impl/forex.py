import streamlit as st
import borsapy as bp
import pandas as pd
from utils.ui import render_header, metric_card
from utils.data_loader import get_fx_rate

def app():
    render_header("Döviz & Altın", "Canlı Döviz Kurları ve Altın Fiyatları")
    
    tab1, tab2, tab3 = st.tabs(["💱 Döviz", "🥇 Altın & Emtia", "🏦 Banka Kurları"])
    
    with tab1:
        c1, c2, c3 = st.columns(3)
        usd, usd_hist = get_fx_rate("USD")
        eur, eur_hist = get_fx_rate("EUR")
        gbp, gbp_hist = get_fx_rate("GBP")
        
        with c1:
            metric_card("USD/TRY", f"{usd:.4f}" if usd else "-", icon="💵")
            if not usd_hist.empty:
                st.line_chart(usd_hist['Close'], height=150)
        with c2:
            metric_card("EUR/TRY", f"{eur:.4f}" if eur else "-", icon="💶")
            if not eur_hist.empty:
                st.line_chart(eur_hist['Close'], height=150)
        with c3:
            metric_card("GBP/TRY", f"{gbp:.4f}" if gbp else "-", icon="💷")
            if not gbp_hist.empty:
                st.line_chart(gbp_hist['Close'], height=150)
                
    with tab2:
        c1, c2, c3 = st.columns(3)
        gram, _ = get_fx_rate("gram-altin")
        ons, _ = get_fx_rate("ons-altin")
        gumus, _ = get_fx_rate("gram-gumus")
        
        with c1: metric_card("Gram Altın", f"{gram:.2f} ₺", icon="🥇")
        with c2: metric_card("Ons Altın", f"{ons:.2f} $", icon="⚖️")
        with c3: metric_card("Gram Gümüş", f"{gumus:.2f} ₺", icon="🥈")
        
        st.info("Emtia verileri anlık piyasa ortalamasıdır.")

    with tab3:
        st.subheader("Banka Kur Karşılaştırması (USD)")
        try:
            usd_obj = bp.FX("USD")
            rates = usd_obj.bank_rates
            st.dataframe(rates)
        except:
            st.warning("Banka verilerine şu an ulaşılamıyor.")
