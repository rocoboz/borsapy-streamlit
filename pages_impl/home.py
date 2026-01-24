import streamlit as st
from utils.ui import render_header, load_lottieurl, metric_card
from utils.data_loader import get_ticker_info, get_fx_rate, get_crypto_price, get_index_info
import plotly.graph_objects as go

def app():
    # Animations
    lottie_chart = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_rw0uop.json")
    
    # Header
    st.markdown("""
    <div class="animate-fade-in" style="margin-bottom: 30px; text-align: center;">
        <h1 style="font-size: 3.5em; background: linear-gradient(90deg, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;">
            BorsaPY Pro
        </h1>
        <p style="font-size: 1.2em; opacity: 0.8; max-width: 600px; margin: 0 auto;">
            Gelişmiş finansal analiz, yapay zeka destekli öngörüler ve profesyonel portföy yönetimi.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Market Glance
    st.subheader("📡 Piyasa Özeti")
    
    m1, m2, m3, m4 = st.columns(4)
    
    # Data Fetching
    bist = get_index_info("XU100") 
    
    usd_val, _ = get_fx_rate("USD")
    gold_val, _ = get_fx_rate("gram-altin")
    btc_val, _ = get_crypto_price("BTCTRY")
    
    with m1:
        metric_card("USD/TRY", f"{usd_val:.2f} ₺" if usd_val else "N/A", icon="💵")
    with m2:
        metric_card("Gram Altın", f"{gold_val:.2f} ₺" if gold_val else "N/A", icon="🥇")
    with m3:
        metric_card("Bitcoin", f"{btc_val:,.0f} ₺" if btc_val else "N/A", icon="₿")
    with m4:
         if bist:
             val = bist.info.get('last', 0)
             chg = bist.info.get('change_percent', 0)
             metric_card("BIST 100", f"{val:,.0f}", f"%{chg:.2f}", icon="📈")
         else:
             metric_card("BIST 100", "N/A", icon="📈")
    
    # Animations Section
    if lottie_chart:
        from streamlit_lottie import st_lottie
        c_anim, c_desc = st.columns([1, 2])
        with c_anim:
            st_lottie(lottie_chart, height=250, key="home_anim")
        with c_desc:
            st.markdown("### 🚀 Yeni Nesil Finans")
            st.info("Yapay zeka algoritmalarımız piyasayı 7/24 tarayarak size en doğru sinyalleri üretir.")
            
    st.markdown("---")
    
    # Feature Showcase
    st.markdown("### 🌟 Öne Çıkan Özellikler")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        #### 📈 Detaylı Hisse Analizi
        BIST hisselerinin teknik ve temel analizi.
        * Fiyat Grafikleri
        * Bilançolar
        * KAP Haberleri
        """)
    
    with c2:
        st.markdown("""
        #### 💰 Fon Karşılaştırma
        TEFAS fonlarını analiz edin ve kıyaslayın.
        * Getiri Sıralaması
        * Portföy Dağılımı
        * Risk Analizi
        """)
    
    with c3:
        st.markdown("""
        #### 🤖 Yapay Zeka & Portföy
        Portföyünüzü oluşturun ve takip edin.
        * PnL Takibi
        * Varlık Dağılımı
        * Teknik Sinyaller
        """)
