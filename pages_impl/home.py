import streamlit as st
from utils.ui import render_header, metric_card
from utils.data_loader import get_ticker_info, get_fx_rate, get_crypto_price, get_index_info, get_market_update_time
import plotly.graph_objects as go

def app():

    # Fetch timestamp
    update_time = get_market_update_time()
    time_str = f"Son Güncelleme: {update_time}" if update_time else "Güncel Veri Bekleniyor..."

    # Header
    from streamlit_lottie import st_lottie
    from utils.ui import load_lottieurl
    
    col1, col2 = st.columns([1, 4])
    with col1:
        lottie_url = "https://lottie.host/6b325256-d4f1-4db8-b59d-d8869ffbc8ec/oN0g7gA6kI.json"
        lottie_json = load_lottieurl(lottie_url)
        if lottie_json:
            st_lottie(lottie_json, height=120, key="home_lottie")
            
    with col2:
        st.markdown(f"""
        <div class="animate-fade-in" style="margin-bottom: 20px; text-align: left;">
            <h1 style="font-size: 3em; color: #f4f4f5; margin-bottom: 10px;">
                Piyasa Kokpiti
            </h1>
            <p style="font-size: 1.1em; color: #a1a1aa; max-width: 600px;">
                BorsaPY Pro'ya hoş geldiniz. Küresel ve yerel piyasaların anlık röntgeni.<br>
                <span style="font-size: 0.85em; color: #718096;">🕒 {time_str}</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 1. Değerli Metaller
    usd_val, _ = get_fx_rate("USD")
    gold_gr, _ = get_fx_rate("gram-altin")
    gold_ons_usd, _ = get_fx_rate("ons-altin")
    silver_gr, _ = get_fx_rate("gram-gumus")
    silver_ons_usd, _ = get_fx_rate("XAG-USD")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Gram Altın", f"{gold_gr:,.2f} ₺" if gold_gr else "N/A", icon="🥇")
    with m2:
        metric_card("Ons Altın", f"${gold_ons_usd:,.2f}" if gold_ons_usd else "N/A", icon="🥇")
    with m3:
        metric_card("Gram Gümüş", f"{silver_gr:,.2f} ₺" if silver_gr else "N/A", icon="🥈")
    with m4:
        metric_card("Ons Gümüş", f"${silver_ons_usd:,.2f}" if silver_ons_usd else "N/A", icon="🥈")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Genel Piyasa & Kripto
    g1, g2, g3, g4 = st.columns(4)
    bist = get_index_info("XU100") 
    btc_usd, _ = get_crypto_price("BTCUSDT")
    eth_usd, _ = get_crypto_price("ETHUSDT")
    
    with g1:
         if bist:
             val = bist.info.get('last', 0)
             chg = bist.info.get('change_percent', 0)
             metric_card("BIST 100", f"{val:,.0f}", f"%{chg:.2f}", icon="📈")
         else:
             metric_card("BIST 100", "N/A", icon="📈")
    with g2:
        metric_card("USD/TRY", f"{usd_val:.4f} ₺" if usd_val else "N/A", icon="💵")
    with g3:
        metric_card("Bitcoin", f"${btc_usd:,.0f}" if btc_usd else "N/A", icon="₿")
    with g4:
        metric_card("Ethereum", f"${eth_usd:,.0f}" if eth_usd else "N/A", icon="🪙")

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
        st.subheader("🪙 Diğer Popüler Kriptolar")
        crypto_symbols = [("Solana", "SOLUSDT"), ("Ripple", "XRPUSDT"), ("Avax", "AVAXUSDT")]
        ccols = st.columns(len(crypto_symbols))
        for idx, (name, sym) in enumerate(crypto_symbols):
            with ccols[idx]:
                val, _ = get_crypto_price(sym)
                if val:
                    decimals = 4 if val < 2 else 2
                    metric_card(name, f"${val:,.{decimals}f}", icon=None)
                else:
                    metric_card(name, "N/A", icon=None)

    with c_right:
        # 🔥 Yıldız Fonlar
        st.subheader("🔥 Ayın Yıldız Fonları (Top 5)")
        with st.spinner("Fonlar çekiliyor..."):
            import borsapy as bp
            @st.cache_data(ttl=3600, show_spinner=False)
            def _get_top_funds_cached():
                df = bp.screen_funds(limit=500)
                if df is not None and not df.empty:
                    return df.sort_values(by='return_1m', ascending=False).head(5)
                return None
            try:
                top_funds = _get_top_funds_cached()
                if top_funds is not None and not top_funds.empty:
                    for i, row in top_funds.iterrows():
                        fname = row['name']
                        name_short = fname[:25] + "..." if len(fname) > 25 else fname
                        ret1m = row.get('return_1m', 0)
                        if ret1m is None or str(ret1m) == 'nan': ret1m = 0
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
            except Exception:
                st.info("TEFAS verisine şu an ulaşılamıyor.")

                
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
            
        # 🗓️ Ekonomik Takvim
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🗓️ Ekonomik Takvim (Önemli)")
        from utils.data_loader import get_economic_calendar
        try:
            with st.spinner("Takvim yükleniyor..."):
                cal_df = get_economic_calendar()
                if cal_df is not None and not cal_df.empty:
                    # Filter high/mid importance and take top 4
                    high_mid = cal_df[cal_df['Importance'].isin(['high', 'mid'])].head(4)
                    if not high_mid.empty:
                        for _, row in high_mid.iterrows():
                            country_str = str(row['Country'])
                            FLAG_MAP = {
                                "TR": "🇹🇷", "US": "🇺🇸", "ABD": "🇺🇸",
                                "Euro": "🇪🇺", "EU": "🇪🇺", "DE": "🇩🇪",
                                "CN": "🇨🇳", "JP": "🇯🇵", "GB": "🇬🇧", "UK": "🇬🇧"
                            }
                            flag = next((v for k, v in FLAG_MAP.items() if k in country_str), "🌍")
                            imp_color = "#ff0055" if row['Importance'] == 'high' else "#f0b90b"
                            event_name = str(row['Event'])[:35] + "..." if len(str(row['Event'])) > 35 else str(row['Event'])
                            time_str = str(row['Time'])
                            st.markdown(f"""
                            <div class="custom-card" style="padding: 10px; margin-bottom: 8px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <span style="font-size: 1.2em; margin-right: 8px;">{flag}</span>
                                        <span style="font-size: 0.85em; color: #a0a5b9;">{time_str}</span>
                                        <br><span style="font-size: 0.9em; font-weight: 500;">{event_name}</span>
                                    </div>
                                    <div title="Önem Derecesi">
                                        <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: {imp_color}; box-shadow: 0 0 8px {imp_color};"></span>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Bugün için önemli veri akışı bulunmuyor.")
                else:
                    st.info("Takvim verisi alınamadı.")
        except Exception as e:
            st.error("Takvim yüklenemedi.")
