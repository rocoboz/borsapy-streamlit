import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import get_ticker_info, get_stock_history
from utils.ui import render_header, metric_card

def app():
    render_header("Hisse Senedi Analizi", "BIST Şirketleri Detaylı Analiz Platformu")
    
    # Search Bar
    symbol = st.text_input("Hisse Kodu Giriniz (Örn: THYAO, ASELS, GARAN)", "THYAO").upper()
    
    with st.expander("🔍 Hisse Tarama (Screener)"):
        st.caption("Detaylı filtreleme için kriterleri belirleyin")
        c_s1, c_s2 = st.columns(2)
        idx_filter = c_s1.selectbox("Endeks", ["XU100", "XU030", "Tümü"], index=0)
        sector = c_s2.selectbox("Sektör", ["Tümü", "Bankacılık", "Sanayi", "Teknoloji"])
        
        if st.button("Hisseleri Tara"):
            try:
                # Basic wrapper for screen_stocks if available
                # Since borsapy screen_stocks arguments might vary, we simulate or use library
                # Assuming library has screen_stocks(index=..., sector=...)
                res = bp.screen_stocks(index=idx_filter if idx_filter != "Tümü" else None)
                st.dataframe(res)
            except Exception as e:
                st.info("Screener modülü şu an aktif değil veya kütüphane desteği sınırlı.")
    
    if symbol:
        if "btn_analyze" not in st.session_state:
            st.session_state.btn_analyze = False
        
        # We auto load to be reactive
        ticker = get_ticker_info(symbol)
        
        if ticker:
            # Top Info Bar
            info = ticker.fast_info
            
            try:
                last_price = getattr(info, 'last_price', 0)
                prev_close = getattr(info, 'previous_close', 0)
                change = ((last_price - prev_close) / prev_close * 100) if prev_close else 0
                color = "green" if change >= 0 else "red"
            except:
                last_price = 0
                change = 0
                color = "grey"

            # Header Metrics
            c1, c2, c3, c4 = st.columns(4)
            with c1: metric_card("Son Fiyat", f"{last_price} ₺", f"{change:.2f}%", icon="💰")
            with c2: metric_card("Hacim", f"{getattr(info, 'volume', 0):,.0f}", icon="📊")
            with c3: metric_card("Piyasa Değeri", f"{getattr(info, 'market_cap', 0):,.0f}", icon="🏢")
            with c4: metric_card("F/K", f"{getattr(info, 'pe_ratio', '-')}", icon="📉")

            # Tabs
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📈 Grafik", "📊 Mali Tablolar", "🏢 Kurumsal", "📰 Haberler", "🎯 Analist", "🌏 ETF Sahipliği"])
            
            with tab1:
                st.subheader(f"{symbol} Fiyat Grafiği")
                period = st.select_slider("Periyot", options=["1ay", "3ay", "6ay", "1y", "5y", "max"], value="1y")
                
                df = get_stock_history(symbol, period=period)
                if not df.empty:
                    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                    open=df['Open'],
                                    high=df['High'],
                                    low=df['Low'],
                                    close=df['Close'])])
                    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=500)
                    st.plotly_chart(fig)
                else:
                    st.warning("Grafik verisi alınamadı.")

            with tab2:
                st.subheader("Finansal Tablolar")
                fs_type = st.radio("Tablo Seçimi", ["Bilanço", "Gelir Tablosu", "Nakit Akış"], horizontal=True)
                
                try:
                    if fs_type == "Bilanço":
                        st.dataframe(ticker.balance_sheet)
                    elif fs_type == "Gelir Tablosu":
                        st.dataframe(ticker.income_stmt)
                    else:
                        st.dataframe(ticker.cashflow)
                except:
                    st.info("Bu finansal tablo verisi mevcut değil.")

            with tab3:
                c_1, c_2 = st.columns(2)
                with c_1:
                    st.markdown("##### Temettüler")
                    try:
                        st.dataframe(ticker.dividends)
                    except:
                        st.write("Veri yok.")
                with c_2:
                    st.markdown("##### Sermaye Artırımları")
                    try:
                        st.dataframe(ticker.splits)
                    except:
                        st.write("Veri yok.")

            with tab4:
                st.subheader("KAP Bildirimleri")
                try:
                    news = ticker.news
                    for n in news[:5]:
                        st.write(f"**{n.get('date', '')}** - {n.get('title', '')}")
                        st.markdown("---")
                except:
                    st.info("Haber akışı alınamadı.")

            with tab5:
                st.subheader("Analist Tahminleri")
                try:
                    st.dataframe(ticker.recommendations_summary)
                except:
                    st.info("Analist verisi bulunamadı.")

            with tab6:
                st.subheader("ETF Sahipliği")
                try:
                    etfs = ticker.etf_holders
                    if etfs is not None and not etfs.empty:
                        st.dataframe(etfs)
                        
                        top_etf = etfs.iloc[0]['name'] if not etfs.empty else "-"
                        total_weight = etfs['holding_weight_pct'].sum() if 'holding_weight_pct' in etfs.columns else 0
                        
                        c_e1, c_e2 = st.columns(2)
                        c_e1.metric("En Büyük Tutucu", top_etf)
                        c_e2.metric("Toplam ETF Ağırlığı", f"%{total_weight:.2f}")
                    else:
                        st.info("Bu hisse için ETF verisi bulunamadı.")
                except Exception as e:
                    st.warning(f"ETF verisi çekilemedi: {e}")

        else:
            st.error("Hisse bulunamadı. Lütfen kodu kontrol edin.")
