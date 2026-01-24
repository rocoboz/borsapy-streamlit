import streamlit as st
import borsapy as bp
import pandas as pd
import plotly.express as px
from utils.ui import render_header, metric_card
from utils.data_loader import get_fund_info, get_fund_list
from streamlit_searchbox import st_searchbox

def app():
    render_header("Yatırım Fonları", "TEFAS Fon Analizi ve Karşılaştırma")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Fon Detay", "⚖️ Fon Karşılaştırma", "🕵️ Fon Tarama"])
    
    with tab1:
        # Search Function
        def search_funds(searchterm: str):
            fund_list = get_fund_list()
            if not searchterm:
                return []
            
            searchterm = searchterm.lower()
            return [f for f in fund_list if searchterm in f.lower()]

        # Use Searchbox
        selected_fund = st_searchbox(
            search_funds,
            key="fund_searchbox",
            label="Fon Ara",
            placeholder="Fon kodu veya adı giriniz (örn: AAK)",
            clear_on_submit=True,
        )

        # State management
        if "selected_fund_code" not in st.session_state:
            st.session_state.selected_fund_code = "AAK"
            
        if selected_fund:
            code = selected_fund.split(" - ")[0]
            st.session_state.selected_fund_code = code
            
        code = st.session_state.selected_fund_code
            
        if code:
            fund = get_fund_info(code)
            if fund:
                # Info
                st.markdown(f"### {code} - {fund.info.get('title', '')}")
                
                m1, m2, m3 = st.columns(3)
                with m1: metric_card("Son Fiyat", f"{fund.info.get('price', 0)} ₺", icon="💵")
                with m2: metric_card("Günlük Getiri", f"%{fund.info.get('daily_return', 0)}", icon="📈")
                with m3: metric_card("Kategori", fund.info.get('category', '-'), icon="🏷️")
                
                # Allocation
                st.subheader("Varlık Dağılımı")
                alloc = fund.allocation
                if not alloc.empty:
                    fig = px.pie(alloc, values='weight', names='asset_name', hole=0.4)
                    st.plotly_chart(fig)
                
                # History
                st.subheader("Fiyat Geçmişi (1 Yıl)")
                hist = fund.history(period="1y")
                st.line_chart(hist['Price'])
                
            else:
                st.error("Fon bulunamadı.")
                
    with tab2:
        st.subheader("Fon Karşılaştırma Aracı")
        codes = st.text_input("Fon Kodları (Virgülle ayırın)", "AAK, TTE, MAC").upper()
        
        if st.button("Karşılaştır"):
            fund_list = [x.strip() for x in codes.split(",")]
            if len(fund_list) < 2:
                st.warning("En az 2 fon girmelisiniz.")
            else:
                try:
                    res = bp.compare_funds(fund_list)
                    st.write("### Sıralamalar")
                    st.json(res['rankings'])
                    
                    st.write("### Özet Tablo")
                    st.dataframe(pd.DataFrame(res['funds']))
                except Exception as e:
                    st.error(f"Karşılaştırma hatası: {str(e)}")

    with tab3:
        st.subheader("Fon Filtreleme (Screener)")
        
        c1, c2 = st.columns(2)
        ftype = c1.selectbox("Fon Tipi", ["YAT", "EMK", "Tümü"], index=0)
        ret_per = c2.selectbox("Getiri Kriteri", ["1 Ay", "3 Ay", "Yılbaşı", "1 Yıl"])
        min_ret = st.slider("Minimum Getiri (%)", 0, 200, 20)
        
        if st.button("Fonları Tara"):
            try:
                # Map inputs to borsapy args
                ft_code = "YAT" if ftype == "YAT" else "EMK" if ftype == "EMK" else None
                
                kwargs = {}
                if ret_per == "1 Ay": kwargs['min_return_1m'] = min_ret
                elif ret_per == "3 Ay": kwargs['min_return_3m'] = min_ret
                elif ret_per == "Yılbaşı": kwargs['min_return_ytd'] = min_ret
                elif ret_per == "1 Yıl": kwargs['min_return_1y'] = min_ret
                
                res = bp.screen_funds(fund_type=ft_code, **kwargs)
                
                if not res.empty:
                    st.success(f"{len(res)} fon bulundu.")
                    st.dataframe(res)
                else:
                    st.warning("Kriterlere uygun fon bulunamadı.")
                    
            except Exception as e:
                st.error(f"Tarama hatası: {str(e)}")
