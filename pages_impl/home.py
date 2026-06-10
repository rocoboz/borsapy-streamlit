import streamlit as st
from utils.ui import render_header, load_lottieurl, metric_card
from utils.data_loader import get_ticker_info, get_fx_rate, get_crypto_price, get_index_info
import plotly.graph_objects as go

def app():
    # Animations
    lottie_chart = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_rw0uop.json")
    
    # Header
    st.markdown("""
    <div class="animate-fade-in" style="margin-bottom: 20px; text-align: center;">
        <h1 style="font-size: 3em; background: linear-gradient(90deg, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;">
            Piyasa Kokpiti
        </h1>
        <p style="font-size: 1.1em; opacity: 0.8; max-width: 600px; margin: 0 auto;">
            BorsaPY Pro'ya hoş geldiniz. Küresel ve yerel piyasaların anlık röntgeni.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 1. Quick Market Glance
    m1, m2, m3, m4 = st.columns(4)
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
             
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Dashboard Grid
    c_left, c_right = st.columns([1.2, 1])
    
    with c_left:
        # 📈 BIST Öncüleri (Majör Hisseler)
        st.subheader("📈 BIST Lokomotifleri")
        bist_symbols = ["THYAO", "TUPRS", "ISCTR", "KCHOL"]
        bcols = st.columns(len(bist_symbols))
        for idx, sym in enumerate(bist_symbols):
            with bcols[idx]:
                ticker = get_ticker_info(sym)
                if ticker:
                    try:
                        info = ticker.info
                        price = info.get('last', info.get('currentPrice', info.get('regularMarketPrice', 0)))
                        chg_pct = info.get('change_percent', info.get('regularMarketChangePercent', 0))
                        metric_card(sym, f"{price:.2f}", f"%{chg_pct:.2f}", icon=None)
                    except Exception as e:
                        metric_card(sym, "N/A", icon=None)
                else:
                    metric_card(sym, "N/A", icon=None)
                    
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 🪙 Kripto Takibi
        st.subheader("🪙 Popüler Kriptolar")
        crypto_symbols = [("Ethereum", "ETHTRY"), ("Solana", "SOLTRY"), ("Ripple", "XRPTRY")]
        ccols = st.columns(len(crypto_symbols))
        for idx, (name, sym) in enumerate(crypto_symbols):
            with ccols[idx]:
                val, _ = get_crypto_price(sym)
                if val:
                    metric_card(name, f"{val:,.2f} ₺", icon=None)
                else:
                    metric_card(name, "N/A", icon=None)

    with c_right:
        # 🔥 Yıldız Fonlar
        st.subheader("🔥 Ayın Yıldız Fonları (Top 5)")
        with st.spinner("Fonlar çekiliyor..."):
            import borsapy as bp
            try:
                # Fetch all and sort by 1-month return for a more dynamic "hot" list
                all_funds = bp.screen_funds(limit=5000)
                if all_funds is not None and not all_funds.empty:
                    top_funds = all_funds.sort_values(by='return_1m', ascending=False).head(5)
                    for i, row in top_funds.iterrows():
                        fname = row['name']
                        name_short = fname[:25] + "..." if len(fname) > 25 else fname
                        ret1m = row.get('return_1m', 0)
                        if ret1m is None or str(ret1m) == 'nan': ret1m = 0
                        
                        # Use a simpler index counter since iterrows index is the original dataframe index
                        display_index = list(top_funds.index).index(i) + 1
                        
                        st.markdown(f"""
                        <div class="custom-card" style="padding: 12px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span style="color: #a0a5b9; font-weight: bold; margin-right: 10px;">#{display_index}</span>
                                    <span style="font-weight: bold; color: #00d2ff;">{row['fund_code']}</span>
                                    <br><span style="font-size: 0.8em; opacity: 0.8;">{name_short}</span>
                                </div>
                                <div style="text-align: right;">
                                    <span style="color: #00ff9d; font-weight: bold;">+{ret1m:.2f}%</span>
                                    <br><span style="font-size: 0.7em; opacity: 0.5;">Son 1 Ay</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Fon verisi geçici olarak alınamadı.")
            except Exception as e:
                st.error("TEFAS bağlantı hatası.")
                
        # 📅 Makroekonomi Özeti
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📅 Makroekonomi")
        from utils.data_loader import get_real_policy_rate
        try:
            # Use custom fetcher to bypass borsapy sorting bug
            rate = get_real_policy_rate()
            if rate is None:
                rate = "N/A"
            if isinstance(rate, float) or isinstance(rate, int) or rate == "N/A":
                st.markdown(f"""
                <div class="custom-card" style="padding: 15px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 1.2em;">🇹🇷 TCMB Politika Faizi</span>
                    </div>
                    <div>
                        <span style="font-size: 1.5em; font-weight: bold; color: #ff0055;">%{rate}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except:
            pass
