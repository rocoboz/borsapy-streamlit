import streamlit as st
import borsapy as bp
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import get_ticker_info, get_stock_history, get_stock_list
from utils.ui import render_header, metric_card
from streamlit_searchbox import st_searchbox

def app():
    render_header("Hisse Senedi Analizi", "BIST Şirketleri Detaylı Analiz Platformu")
    
    # Search Function
    def search_stocks(searchterm: str):
        stock_list = get_stock_list()
        if not searchterm:
            return []
        
        # Simple case-insensitive match
        searchterm = searchterm.lower()
        return [s for s in stock_list if searchterm in s.lower()]

    # Use Searchbox
    selected_stock = st_searchbox(
        search_stocks,
        key="stock_searchbox",
        label="Hisse Ara",
        placeholder="Hisse kodu veya adı giriniz (örn: THYAO)",
        clear_on_submit=True,
    )
    
    # State management for selection
    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = "THYAO"
        
    if selected_stock:
        # Update session state if new selection
        symbol = selected_stock.split(" - ")[0]
        st.session_state.selected_symbol = symbol
        
    symbol = st.session_state.selected_symbol
    
    with st.expander("🔍 Hisse Tarama (Screener)"):
        st.caption("Detaylı filtreleme için kriterleri belirleyin")
        c_s1, c_s2 = st.columns(2)
        idx_filter = c_s1.selectbox("Endeks", ["XU100", "XU030", "Tümü"], index=0)
        sector = c_s2.selectbox("Sektör", ["Tümü", "Bankacılık", "Sanayi", "Teknoloji"])
        
        if st.button("Hisseleri Tara"):
            try:
                if sector == "Tümü" and idx_filter != "Tümü":
                    # Native Screener Usage
                    screener = bp.Screener()
                    screener.set_index(idx_filter)
                    res_df = screener.run()
                    st.success(f"{len(res_df)} hisse bulundu.")
                    st.dataframe(res_df)
                else:
                    # Hybrid / Intersection method for Sector Filtering
                    index_tickers = []
                    if idx_filter != "Tümü":
                        idx_comps = bp.Index(idx_filter).components
                        index_tickers = [c['symbol'] for c in idx_comps]
                    
                    sector_tickers = []
                    sector_map = {"Bankacılık": "XBANK", "Sanayi": "XUSIN", "Teknoloji": "XUTEK"}
                    if sector != "Tümü":
                        sec_code = sector_map.get(sector)
                        if sec_code:
                            sec_comps = bp.Index(sec_code).components
                            sector_tickers = [c['symbol'] for c in sec_comps]
                    
                    final_tickers = []
                    if idx_filter == "Tümü" and sector == "Tümü":
                        all_comps = bp.Index('XUTUM').components
                        final_tickers = all_comps
                    elif idx_filter != "Tümü" and sector == "Tümü":
                        final_tickers = idx_comps
                    elif idx_filter == "Tümü" and sector != "Tümü":
                        final_tickers = sec_comps
                    else:
                        set_idx = set(index_tickers)
                        set_sec = set(sector_tickers)
                        common = set_idx.intersection(set_sec)
                        final_tickers = [c for c in idx_comps if c['symbol'] in common]
                    
                    if final_tickers:
                        res_df = pd.DataFrame(final_tickers)
                        st.success(f"{len(res_df)} hisse bulundu.")
                        st.dataframe(res_df)
                    else:
                        st.warning("Kriterlere uygun hisse bulunamadı.")
            except Exception as e:
                st.error(f"Screener hatası: {str(e)}")
    
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
                st.subheader(f"{symbol} İnteraktif Grafik & Teknik Analiz")
                
                c_g1, c_g2 = st.columns([1, 2])
                with c_g1:
                    period = st.select_slider("Periyot", options=["1ay", "3ay", "6ay", "1y", "5y", "max"], value="1y")
                with c_g2:
                    indicators = st.multiselect("Göstergeler", ["SMA 20", "SMA 50", "Bollinger Bantları", "Hacim (Volume)"], default=["SMA 20", "Hacim (Volume)"])
                
                df = get_stock_history(symbol, period=period)
                if not df.empty:
                    from plotly.subplots import make_subplots
                    
                    show_volume = "Hacim (Volume)" in indicators and 'Volume' in df.columns
                    
                    if show_volume:
                        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
                    else:
                        fig = go.Figure()
                    
                    # Candlestick
                    candlestick = go.Candlestick(
                        x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'],
                        name="Fiyat (OHLC)"
                    )
                    
                    if show_volume:
                        fig.add_trace(candlestick, row=1, col=1)
                    else:
                        fig.add_trace(candlestick)
                    
                    # SMA 20
                    if "SMA 20" in indicators and len(df) >= 20:
                        sma20 = df['Close'].rolling(window=20).mean()
                        trace_sma20 = go.Scatter(x=df.index, y=sma20, mode='lines', name='SMA 20', line=dict(color='#00d2ff', width=1.5))
                        if show_volume: fig.add_trace(trace_sma20, row=1, col=1)
                        else: fig.add_trace(trace_sma20)

                    # SMA 50
                    if "SMA 50" in indicators and len(df) >= 50:
                        sma50 = df['Close'].rolling(window=50).mean()
                        trace_sma50 = go.Scatter(x=df.index, y=sma50, mode='lines', name='SMA 50', line=dict(color='#ff9900', width=1.5))
                        if show_volume: fig.add_trace(trace_sma50, row=1, col=1)
                        else: fig.add_trace(trace_sma50)

                    # Bollinger Bands
                    if "Bollinger Bantları" in indicators and len(df) >= 20:
                        sma = df['Close'].rolling(window=20).mean()
                        std = df['Close'].rolling(window=20).std()
                        upper_band = sma + (std * 2)
                        lower_band = sma - (std * 2)
                        
                        trace_upper = go.Scatter(x=df.index, y=upper_band, mode='lines', name='Bollinger Üst', line=dict(color='rgba(173, 216, 230, 0.4)', width=1, dash='dash'))
                        trace_lower = go.Scatter(x=df.index, y=lower_band, mode='lines', name='Bollinger Alt', line=dict(color='rgba(173, 216, 230, 0.4)', width=1, dash='dash'))
                        
                        if show_volume:
                            fig.add_trace(trace_upper, row=1, col=1)
                            fig.add_trace(trace_lower, row=1, col=1)
                        else:
                            fig.add_trace(trace_upper)
                            fig.add_trace(trace_lower)

                    # Volume Subplot
                    if show_volume:
                        colors = ['#00ff9d' if c >= o else '#ff0055' for c, o in zip(df['Close'], df['Open'])]
                        vol_bar = go.Bar(x=df.index, y=df['Volume'], name='Hacim', marker_color=colors)
                        fig.add_trace(vol_bar, row=2, col=1)
                        fig.update_yaxes(title_text="Hacim", row=2, col=1)
                    
                    fig.update_layout(
                        template="plotly_dark",
                        height=550,
                        margin=dict(l=20, r=20, t=30, b=20),
                        xaxis_rangeslider_visible=False,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig, use_container_width=True)
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
