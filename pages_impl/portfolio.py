import streamlit as st
import borsapy as bp
import pandas as pd
import plotly.express as px
from utils.ui import render_header, metric_card

def app():
    render_header("Portföy Yönetimi", "Profesyonel Varlık ve Risk Yönetimi")
    
    # Initialize Portfolio in Session State
    if 'bp_portfolio' not in st.session_state:
        st.session_state.bp_portfolio = bp.Portfolio()
        # Set default benchmark
        try:
            st.session_state.bp_portfolio.set_benchmark("XU100")
        except: pass

    portfolio = st.session_state.bp_portfolio

    # --- Sidebar / Top Controls ---
    with st.expander("➕ Varlık Ekle / Güncelle", expanded=False):
        c1, c2, c3, c4, c5 = st.columns(5)
        
        asset_type = c1.selectbox("Varlık Tipi", ["stock", "fund", "fx", "crypto"], format_func=lambda x: x.upper())
        symbol = c2.text_input("Sembol", "THYAO").upper()
        shares = c3.number_input("Adet", min_value=0.0001, value=1.0, step=1.0)
        cost = c4.number_input("Maliyet (Birim)", min_value=0.0, value=0.0)
        
        # Add Button
        if c5.button("Ekle/Güncelle"):
            if symbol and shares > 0:
                try:
                    with st.spinner(f"{symbol} ekleniyor..."):
                        # If cost is 0, borsapy might use current price or 0. Let's explicitly pass cost if > 0
                        # README: portfolio.add("THYAO", shares=100, cost=280.0)
                        kwargs = {"shares": shares, "asset_type": asset_type}
                        if cost > 0:
                            kwargs["cost"] = cost
                            
                        portfolio.add(symbol, **kwargs)
                        st.success(f"{symbol} portföye eklendi!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Hata: {str(e)}")

    # --- Main Dashboard ---
    
    if not portfolio.holdings.empty:
        # Top Metrics
        # README: portfolio.value, portfolio.cost, portfolio.pnl, portfolio.pnl_pct
        try:
            val = portfolio.value
            cost_val = portfolio.cost
            pnl = portfolio.pnl
            pnl_pct = portfolio.pnl_pct
            
            m1, m2, m3, m4 = st.columns(4)
            with m1: metric_card("Toplam Değer", f"{val:,.2f} ₺", icon="💰")
            with m2: metric_card("Toplam Maliyet", f"{cost_val:,.2f} ₺", icon="🧾")
            with m3: metric_card("Kar/Zarar (TL)", f"{pnl:,.2f} ₺", icon="📊")
            with m4: metric_card("Kar/Zarar (%)", f"%{pnl_pct:.2f}", icon="📈")
        except Exception as e:
            st.error(f"Metrik hesaplama hatası: {e}")

        # Holdings Table
        st.subheader("Varlıklarım")
        st.dataframe(portfolio.holdings, width="stretch")

        # Charts & Analysis
        c_left, c_right = st.columns(2)
        
        with c_left:
            st.subheader("Varlık Dağılımı")
            # portfolio.weights is a dict
            weights = portfolio.weights
            if weights:
                df_w = pd.DataFrame(list(weights.items()), columns=['Symbol', 'Weight'])
                fig = px.pie(df_w, values='Weight', names='Symbol', hole=0.4)
                st.plotly_chart(fig)
                
        with c_right:
            st.subheader("Risk Metrikleri (1 Yıl)")
            try:
                metrics = portfolio.risk_metrics(period="1y")
                # Format metrics for display
                disp_metrics = {
                    "Yıllık Getiri": f"%{metrics.get('annualized_return', 0):.2f}",
                    "Volatilite": f"%{metrics.get('annualized_volatility', 0):.2f}",
                    "Sharpe Oranı": f"{metrics.get('sharpe_ratio', 0):.2f}",
                    "Max Drawdown": f"%{metrics.get('max_drawdown', 0):.2f}",
                    "Beta": f"{metrics.get('beta', 0):.2f}"
                }
                st.json(disp_metrics)
            except Exception as e:
                st.info("Risk metrikleri hesaplanması için daha fazla veriye ihtiyaç olabilir veya API hatası.")

        # Management Actions
        with st.expander("Yönetim İşlemleri"):
            options = portfolio.holdings['symbol'].tolist() if not portfolio.holdings.empty else []
            rem_sym = st.selectbox("Silinecek Varlık", options)
            
            if st.button("Seçileni Sil"):
                if rem_sym:
                    portfolio.remove(rem_sym)
                    st.rerun()
                
            if st.button("Portföyü Tamamen Sıfırla", type="primary"):
                portfolio.clear()
                st.rerun()

    else:
        st.info("Portföyünüz boş. Yukarıdaki panelden varlık ekleyerek başlayın.")
        st.markdown("""
        **Desteklenen Varlıklar:**
        * **Hisse:** THYAO, GARAN, ASELS...
        * **Fon:** AAK, TTE, YAY...
        * **Kripto:** BTCTRY, ETHTRY...
        * **Döviz/Emtia:** USD, EUR, gram-altin, BRENT...
        """)
