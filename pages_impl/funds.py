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
            st.session_state.selected_fund_code = "MAC"
            
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
                
                ftab1, ftab2, ftab3, ftab4 = st.tabs(["Genel Bakış", "Performans & Risk", "Ücret & Vergi", "Teknik Analiz"])
                
                with ftab1:
                    st.subheader("Fiyat Geçmişi (1 Yıl)")
                    hist = fund.history(period="1y")
                    st.line_chart(hist['Price'])
                    
                    st.subheader("Varlık Dağılımı")
                    try:
                        alloc = fund.allocation
                        if not alloc.empty:
                            fig = px.pie(alloc, values='weight', names='asset_name', hole=0.4)
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.info("Varlık dağılımı verisi (Sunucu kısıtlamaları/TEFAS koruması nedeniyle) bu ortamda çekilemiyor.")
                        
                with ftab2:
                    st.subheader("Getiri Performansı")
                    try:
                        perf = fund.performance
                        p1, p2, p3, p4 = st.columns(4)
                        p1.metric("1 Ay", f"%{perf.get('return_1m', 0):.2f}" if perf.get('return_1m') is not None else "-")
                        p2.metric("3 Ay", f"%{perf.get('return_3m', 0):.2f}" if perf.get('return_3m') is not None else "-")
                        p3.metric("Yılbaşı (YTD)", f"%{perf.get('return_ytd', 0):.2f}" if perf.get('return_ytd') is not None else "-")
                        p4.metric("1 Yıl", f"%{perf.get('return_1y', 0):.2f}" if perf.get('return_1y') is not None else "-")
                    except Exception as e:
                        st.info("Performans verisi bulunamadı.")
                        
                    st.subheader("Risk Metrikleri")
                    try:
                        rm = fund.risk_metrics()
                        if rm:
                            r1, r2, r3, r4 = st.columns(4)
                            r1.metric("Sharpe Oranı", f"{rm.get('sharpe_ratio', 0):.2f}")
                            r2.metric("Sortino Oranı", f"{rm.get('sortino_ratio', 0):.2f}")
                            r3.metric("Yıllık Volatilite", f"%{rm.get('annualized_volatility', 0):.2f}")
                            r4.metric("Maks. Düşüş", f"%{rm.get('max_drawdown', 0):.2f}")
                    except Exception as e:
                        st.info("Risk metrikleri alınamadı.")
                        
                with ftab3:
                    st.subheader("Yönetim Ücretleri ve Giderler")
                    try:
                        mf = fund.management_fee
                        c_mf1, c_mf2 = st.columns(2)
                        c_mf1.metric("Uygulanan Yönetim Ücreti", f"%{mf.get('applied_fee', 0)}")
                        c_mf2.metric("İzahname Azami Gider Oranı", f"%{mf.get('max_expense_ratio', 0)}")
                    except Exception as e:
                        st.info("Ücret bilgileri bulunamadı.")
                        
                    st.subheader("Vergilendirme (Stopaj)")
                    try:
                        tax = fund.withholding_tax_rate()
                        st.metric("Stopaj Oranı", f"%{tax}")
                        st.caption("Not: Bireysel yatırımcılar için geçerli standart stopaj oranıdır.")
                    except:
                        pass
                        
                with ftab4:
                    st.subheader("Teknik Sinyaller")
                    try:
                        signals = fund.ta_signals()
                        if signals is not None and not signals.empty:
                            st.dataframe(signals, use_container_width=True)
                        else:
                            st.info("Teknik sinyal bulunamadı.")
                    except:
                        st.info("Teknik sinyal verisine ulaşılamadı.")
                        
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
        st.subheader("🏆 TEFAS Akıllı Algoritmik Fon Sıralaması (Ranking)")
        st.caption("Gelişmiş finansal rasyolar ve kümülatif getiri değerlerini harmanlayan akıllı puanlama motoru.")
        
        c1, c2, c3 = st.columns(3)
        period = c1.selectbox("Sıralama Dönemi", ["1 Ay", "3 Ay", "6 Ay", "Yılbaşı", "1 Yıl", "3 Yıl", "5 Yıl"], index=4)
        ftype = c2.selectbox("Fon Tipi", ["Tümü", "YAT (Yatırım Fonları)", "EMK (Emeklilik Fonları)"], index=0)
        algo_focus = c3.selectbox("Sıralama Algoritması Odağı", ["🏆 Akıllı Puan (5 Faktörlü Risk/Getiri/İstikrar)", "📈 Sadece Getiri (%)", "🛡️ Muhafazakar & Düşük Kayıp Odağı"])
        
        if st.button("Algoritmik Sıralamayı Başlat", use_container_width=True, type="primary"):
            with st.spinner("2000+ Fon taranıyor ve 5 faktörlü akıllı modelle puanlanıyor..."):
                try:
                    ft_codes = ["YAT"] if "YAT" in ftype else ["EMK"] if "EMK" in ftype else ["YAT", "EMK"]
                    
                    df_list = []
                    for code in ft_codes:
                        res = bp.screen_funds(fund_type=code, limit=5000)
                        if isinstance(res, pd.DataFrame):
                            df_list.append(res)
                        elif isinstance(res, list) and res:
                            df_list.append(pd.DataFrame(res))
                            
                    if df_list:
                        df = pd.concat(df_list, ignore_index=True)
                    else:
                        df = pd.DataFrame()
                    
                    # Map periods
                    p_map = {
                        "1 Ay": "return_1m", "3 Ay": "return_3m", "6 Ay": "return_6m",
                        "Yılbaşı": "return_ytd", "1 Yıl": "return_1y", "3 Yıl": "return_3y", "5 Yıl": "return_5y"
                    }
                    target_col = p_map[period]
                    
                    if df.empty or target_col not in df.columns:
                        st.error(f"Seçilen dönem ({period}) veya kategori için veri bulunamadı.")
                    else:
                        # Drop nulls for target
                        df = df.dropna(subset=[target_col])
                        
                        if algo_focus == "Sadece Getiri (%)":
                            df['Smart Score'] = df[target_col]
                            df = df.sort_values(by=target_col, ascending=False)
                        else:
                            # 1. Kategori İçi Göreli Getiri Yüzdesi (%35)
                            if 'category' in df.columns:
                                df['cat_ret_pct'] = df.groupby('category')[target_col].transform(lambda x: x.rank(pct=True) * 100)
                            else:
                                df['cat_ret_pct'] = df[target_col].rank(pct=True) * 100

                            # 2. Risk-Adjusted Return (Sharpe & Volatility Proxy - %25)
                            periods = ['return_1m', 'return_3m', 'return_6m', 'return_1y']
                            avail_periods = [p for p in periods if p in df.columns]

                            sharpe_proxies = []
                            for idx, row in df.iterrows():
                                vals = [row[p] for p in avail_periods if pd.notnull(row[p])]
                                if len(vals) >= 2:
                                    mean_v = pd.Series(vals).mean()
                                    std_v = pd.Series(vals).std()
                                    sharpe = (mean_v / (std_v + 0.5)) if std_v > 0 else (mean_v / 0.5)
                                else:
                                    sharpe = (row[target_col] / 10.0) if pd.notnull(row[target_col]) else 0
                                sharpe_proxies.append(sharpe)

                            df['sharpe_proxy'] = sharpe_proxies
                            df['sharpe_pct'] = df['sharpe_proxy'].rank(pct=True) * 100

                            # 3. Kayıp Koruması & Düşüş Risk Puanı (%20)
                            drawdown_scores = []
                            for idx, row in df.iterrows():
                                vals = [row[p] for p in avail_periods if pd.notnull(row[p])]
                                neg_vals = [v for v in vals if v < 0]
                                worst_drop = min(neg_vals) if neg_vals else 0
                                drawdown_scores.append(worst_drop)

                            df['drawdown_proxy'] = drawdown_scores
                            df['drawdown_pct'] = df['drawdown_proxy'].rank(pct=True, ascending=True) * 100

                            # 4. Çoklu Dönem Tutarlılığı (%15)
                            consistency_scores = []
                            for idx, row in df.iterrows():
                                vals = [row[p] for p in avail_periods if pd.notnull(row[p])]
                                if vals:
                                    pos_ratio = sum(1 for v in vals if v > 0) / len(vals)
                                    consistency_scores.append(pos_ratio * 100)
                                else:
                                    consistency_scores.append(50)

                            df['consistency_pct'] = consistency_scores

                            # 5. Ücret Verimliliği (%5)
                            if 'applied_fee' in df.columns:
                                df['fee_pct'] = df['applied_fee'].rank(pct=True, ascending=False) * 100
                            else:
                                df['fee_pct'] = 50.0

                            # Modeller
                            if "Muhafazakar" in algo_focus:
                                # Prioritize Drawdown Protection and Sharpe
                                df['Smart Score'] = (
                                    (df['cat_ret_pct'] * 0.20) +
                                    (df['sharpe_pct'] * 0.35) +
                                    (df['drawdown_pct'] * 0.30) +
                                    (df['consistency_pct'] * 0.10) +
                                    (df['fee_pct'] * 0.05)
                                )
                            else:
                                # Standard 5-Factor Smart Score
                                df['Smart Score'] = (
                                    (df['cat_ret_pct'] * 0.35) +
                                    (df['sharpe_pct'] * 0.25) +
                                    (df['drawdown_pct'] * 0.20) +
                                    (df['consistency_pct'] * 0.15) +
                                    (df['fee_pct'] * 0.05)
                                )
                            
                            df = df.sort_values(by='Smart Score', ascending=False)
                            
                        # Format output
                        df['Sıra'] = range(1, len(df) + 1)
                        display_cols = ['Sıra', 'fund_code', 'name', 'fund_type', target_col, 'Smart Score']
                        
                        # Add a nicely formatted dataframe
                        out_df = df[display_cols].copy()
                        out_df.columns = ['Derece', 'Fon Kodu', 'Fon Adı', 'Kategori', f'{period} Getiri (%)', 'Smart Score']
                        
                        # Format floats
                        out_df[f'{period} Getiri (%)'] = out_df[f'{period} Getiri (%)'].map('{:.2f}'.format)
                        out_df['Smart Score'] = out_df['Smart Score'].map('{:.1f}'.format)
                        
                        st.success(f"Algoritmik Sıralama Süzgecinden Geçen: **{len(out_df)}** Fon Saptanmıştır.")
                        st.dataframe(out_df, use_container_width=True, hide_index=True)
                        
                except Exception as e:
                    st.error(f"Sıralama hatası: {str(e)}")
