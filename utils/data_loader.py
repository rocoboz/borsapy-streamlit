import streamlit as st
import borsapy as bp
import pandas as pd

@st.cache_data(ttl=86400) # Hisse listesi günde 1 kez güncellenir
def get_stock_list():
    try:
        df = bp.companies()
        # Create "TICKER - Name" format
        if not df.empty:
            return [f"{row['ticker']} - {row['name']}" for _, row in df.iterrows()]
        return []
    except:
        return []

@st.cache_data(ttl=86400)
def get_fund_list():
    try:
        # Fetch all funds (using a high limit)
        funds = bp.search_funds('', limit=2000)
        if funds:
            # Sort for better UX
            funds_sorted = sorted(funds, key=lambda x: x['fund_code'])
            return [f"{f['fund_code']} - {f['name']}" for f in funds_sorted]
        return []
    except:
        return []

@st.cache_data(ttl=86400)
def get_crypto_list():
    try:
        return bp.crypto_pairs()
    except:
        return []

@st.cache_resource(ttl=900)  # Hisse fiyatları 15 dakikada bir (900 sn)
def get_ticker_info(symbol):
    try:
        ticker = bp.Ticker(symbol)
        # Force load fast_info to ensure validity
        _ = ticker.fast_info
        return ticker
    except Exception as e:
        return None

@st.cache_data(ttl=900) # Hisse geçmiş verileri 15 dakikada bir
def get_stock_history(symbol, period="1y", interval="1d"):
    try:
        ticker = bp.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=86400) # Endeks listesi günde 1 kez
def get_all_indices():
    return bp.all_indices()

@st.cache_resource(ttl=900) # Endeks değerleri 15 dakikada bir
def get_index_info(symbol):
    try:
        idx = bp.Index(symbol)
        # Force fetch
        _ = idx.info
        return idx
    except:
        return None

@st.cache_data(ttl=300)
def get_fx_rate(symbol):
    try:
        fx = bp.FX(symbol)
        cur = fx.current
        val = cur.get('last') if isinstance(cur, dict) else cur
        return val, fx.history(period="1mo")
    except:
        return None, pd.DataFrame()

@st.cache_data(ttl=300)
def get_crypto_price(symbol):
    try:
        c = bp.Crypto(symbol)
        cur = c.current
        val = cur.get('last') if isinstance(cur, dict) else cur
        return val, c.history(period="1mo")
    except:
        return None, pd.DataFrame()

@st.cache_resource(ttl=7200) # Fon detayları: TEFAS sabah 9-12 arası günceller, 2 saatte bir tazelemek (7200 sn) en sağlıklısı
def get_fund_info(code):
    try:
        fund = bp.Fund(code)
        _ = fund.info # trigger fetch to catch exceptions
        return fund
    except:
        return None

@st.cache_data(ttl=3600)
def get_real_policy_rate():
    try:
        import borsapy as bp
        provider = bp._providers.tcmb_rates.TCMBRatesProvider()
        data = provider._fetch_and_parse_table(bp._providers.tcmb_rates.TCMB_URLS['policy'])
        if data:
            return data[-1]['lending']
    except:
        pass
    return None


@st.cache_data(ttl=3600)
def get_economic_calendar():
    try:
        import borsapy as bp
        return bp.economic_calendar()
    except:
        return None

@st.cache_data(ttl=300)
def get_market_update_time():
    try:
        import borsapy as bp
        ts = bp.FX("USD").current.get("update_time")
        if ts:
            return ts.strftime("%d.%m.%Y %H:%M:%S")
        return None
    except:
        return None


