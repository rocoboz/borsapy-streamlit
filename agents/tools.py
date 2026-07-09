import json
import math

import streamlit as st
import borsapy as bp
from utils.data_loader import get_ticker_info


def _json_sanitize(value):
    if isinstance(value, dict):
        return {str(k): _json_sanitize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_sanitize(v) for v in value]
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if hasattr(value, "item"):
        return _json_sanitize(value.item())
    return value


def _json_default(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _json_dumps(payload) -> str:
    return json.dumps(_json_sanitize(payload), default=_json_default, allow_nan=False, ensure_ascii=False)


# --- STOCK TOOLS (Similar to old utils/ai_tools.py) ---
def get_stock_financials(symbol: str) -> str:
    ticker = get_ticker_info(symbol)
    if not ticker: return _json_dumps({"error": f"Symbol {symbol} not found."})
    try:
        usd_rate = float(bp.FX('USD').current['last'])
        info = ticker.info
        targets = ticker.analyst_price_targets if hasattr(ticker, 'analyst_price_targets') else "N/A"
        if isinstance(targets, dict):
            for k in ['current', 'low', 'high', 'mean', 'median']:
                if k in targets and targets[k]:
                    targets[k] = round(targets[k] / usd_rate, 2)
                    
        pe_val = info.get('trailingPE')
        if pe_val is None:
            pe_val = info.get('forwardPE', 'N/A')
            
        return _json_dumps({
            "symbol": symbol,
            "Currency": "USD",
            "PE_Ratio": pe_val,
            "Price_to_Book": info.get('priceToBook', 'N/A'),
            "ROE": info.get('returnOnEquity', 'N/A'),
            "Analyst_Price_Targets_USD": targets,
            "Recommendations": ticker.recommendations_summary if hasattr(ticker, 'recommendations_summary') else "N/A"
        })
    except Exception as e: return _json_dumps({"error": str(e)})

def get_multiple_stock_financials(symbols: str) -> str:
    """Gets P/E, P/B, ROE, and analyst targets for multiple BIST stocks (for peer comparison).
    Pass a comma-separated string of symbols (e.g. 'ASELS, OTKAR, SDTTR').
    """
    import borsapy as bp
    results = {}
    symbol_list = [s.strip() for s in symbols.split(',') if s.strip()]
    
    for sym in symbol_list:
        try:
            ticker = bp.Ticker(sym)
            info = ticker.info
            targets = ticker.analyst_price_targets if hasattr(ticker, 'analyst_price_targets') else None
            
            usd_rate = 1.0
            try:
                usd_rate = float(bp.FX('USD').current['last'])
            except: pass
            
            if isinstance(targets, dict) and "mean" in targets and targets["mean"]:
                targets["mean"] = round(targets["mean"] / usd_rate, 2)
            
            symbol_data = {
                "P/E_Ratio": info.get('trailingPE', 'N/A'),
                "Price_to_Book": info.get('priceToBook', 'N/A'),
                "ROE": info.get('returnOnEquity', 'N/A'),
                "Analyst_Mean_Target_USD": targets.get("mean", "N/A") if isinstance(targets, dict) else "N/A"
            }
            results[sym] = symbol_data
        except Exception as e:
            results[sym] = {"error": str(e)}
            
    return _json_dumps({"peer_comparison": results})

@st.cache_data(ttl=3600, show_spinner=False)
def screen_bist_stocks(index: str = 'BIST100', max_pe: float = None, min_roe: float = None,
                       min_upside: float = None, top_n: int = 8) -> str:
    """Tarayıcı (Screener) ile BIST hisselerini filtreler ve en iyi sonuçları döner.
    index: 'BIST30', 'BIST100', 'BIST_ALL' gibi endeks adı.
    Kriter verilmezse yalnızca endeksteki tüm hisselerin özet listesini döner.
    """
    import borsapy as bp
    try:
        # Map user-friendly AI index names to borsapy Native Screener formats
        idx_map = {"BIST100": "XU100", "BIST30": "XU030", "BIST_ALL": "Tümü"}
        mapped_index = idx_map.get(index.upper(), index)
        
        screener = bp.Screener()
        screener.set_index(mapped_index)
        if max_pe is not None:
            screener.add_filter('pe', max=float(max_pe))
        if min_roe is not None:
            screener.add_filter('roe', min=float(min_roe))
        if min_upside is not None:
            screener.add_filter('upside_potential', min=float(min_upside))
            
        df = screener.run()
        if df.empty:
            return _json_dumps({"message": "Kriterlere uyan hisse bulunamadı. Kriterleri gevşetin.",
                               "suggestion": "max_pe değerini artırın veya min_roe değerini düşürün."})
        
        df_top = df.head(top_n)
        result_list = df_top.to_dict(orient='records')
        return _json_dumps({"index": index, "total_matched": len(df), "top_results": result_list})
    except Exception as e:
        return _json_dumps({"error": f"Screener execution failed: {str(e)}"})


@st.cache_data(ttl=3600, show_spinner=False)
def screen_top_funds(period: str = '1y', fund_type: str = 'YAT', top_n: int = 8,
                     min_return_1m: float = None, min_return_1y: float = None) -> str:
    """TEFAS fonlarını belirtilen döneme göre sıralayarak en iyi performanslı fonları döner.
    period: '1m', '3m', '6m', 'ytd', '1y', '3y' (sıralama kriteri)
    fund_type: 'YAT' (yatırım fonu), 'EME' (emeklilik fonu), vb.
    top_n: Kaç fon dönsün.
    """
    import borsapy as bp
    import pandas as pd
    try:
        col_map = {
            '1m': 'return_1m', '3m': 'return_3m', '6m': 'return_6m',
            'ytd': 'return_ytd', '1y': 'return_1y', '3y': 'return_3y'
        }
        sort_col = col_map.get(period, 'return_1y')
        
        # Native borsapy screener (limit 1500 to catch all and sort)
        df = bp.screen_funds(limit=1500, fund_type=fund_type)
        
        if df is None or df.empty:
            return _json_dumps({"error": "TEFAS fon verisine ulaşılamadı. Sunucu veya ağ hatası."})
        
        df = df[df[sort_col].notna()]
        df_top = df.sort_values(by=sort_col, ascending=False).head(top_n)
        
        cols = ['fund_code', 'name', 'return_1m', 'return_3m', 'return_6m', 'return_1y']
        available_cols = [c for c in cols if c in df_top.columns]
        result = df_top[available_cols].round(2).to_dict(orient='records')
        return _json_dumps({"period_sorted_by": period, "fund_type": fund_type,
                           "total_scanned": len(df), "top_funds": result})
    except Exception as e:
        return _json_dumps({"error": f"Fund screener failed: {str(e)}"})

def get_stock_technicals(symbol: str) -> str:
    try:
        ticker = bp.Ticker(symbol)
        df = ticker.history(period="1y")
        if df.empty: return _json_dumps({"error": "No data"})
        
        # Convert historical prices to USD
        try:
            fx = bp.FX('USD').history(period="1y")
            fx.index = fx.index.tz_localize(None).normalize()
            df_temp = df.copy()
            df_temp.index = df_temp.index.tz_localize(None).normalize()
            fx_mapped = fx['Close'].reindex(df_temp.index).ffill().bfill()
            for col in ['Open', 'High', 'Low', 'Close']:
                df[col] = df[col] / fx_mapped.values
        except: pass
            
        rsi = bp.calculate_rsi(df, period=14)
        macd_df = bp.calculate_macd(df)
        try: sma50 = float(bp.calculate_sma(df, period=50).iloc[-1])
        except: sma50 = "N/A"
        try: sma200 = float(bp.calculate_sma(df, period=200).iloc[-1])
        except: sma200 = "N/A"
        try: supertrend = bp.calculate_supertrend(df).iloc[-1].to_dict()
        except: supertrend = "N/A"
        
        return _json_dumps({
            "symbol": symbol,
            "Currency": "USD",
            "Price_USD": float(df['Close'].iloc[-1]),
            "RSI_14": float(rsi.iloc[-1]) if not rsi.empty else 'N/A',
            "MACD": float(macd_df['MACD'].iloc[-1]) if 'MACD' in macd_df.columns else 'N/A',
            "SMA50_USD": sma50,
            "SMA200_USD": sma200,
            "Supertrend_USD": supertrend
        })
    except Exception as e: return _json_dumps({"error": str(e)})


# --- CRYPTO TOOLS ---
def get_crypto_technicals(symbol: str) -> str:
    """Gets crypto technicals using borsapy.Crypto"""
    try:
        # Normalize: 'BTC-USD' -> 'BTCUSDT', 'BTC' -> 'BTCUSDT'
        symbol = symbol.upper().replace("-", "")
        # Strip any trailing USD to avoid BTCUSDUSDT
        if symbol.endswith("USD") and not symbol.endswith("USDT"):
            symbol = symbol[:-3]
        if not symbol.endswith("USDT") and not symbol.endswith("TRY"):
            symbol += "USDT"
        crypto = bp.Crypto(symbol)
        df = crypto.history(period="6mo")
        if df.empty: return _json_dumps({"error": "No data"})
        rsi = bp.calculate_rsi(df, period=14)
        macd_df = bp.calculate_macd(df)
        return _json_dumps({
            "symbol": symbol,
            "Price": df['Close'].iloc[-1],
            "RSI_14": float(rsi.iloc[-1]) if not rsi.empty else 'N/A',
            "MACD": float(macd_df['MACD'].iloc[-1]) if 'MACD' in macd_df.columns else 'N/A',
        })
    except Exception as e: return _json_dumps({"error": str(e)})

def get_crypto_momentum(symbol: str) -> str:
    """Gets crypto recent performance"""
    try:
        # Normalize: 'BTC-USD' -> 'BTCUSDT', 'BTC' -> 'BTCUSDT'
        symbol = symbol.upper().replace("-", "")
        if symbol.endswith("USD") and not symbol.endswith("USDT"):
            symbol = symbol[:-3]
        if not symbol.endswith("USDT") and not symbol.endswith("TRY"):
            symbol += "USDT"
        crypto = bp.Crypto(symbol)
        df = crypto.history(period="1mo")
        if df.empty: return _json_dumps({"error": "No data"})
        p_now = df['Close'].iloc[-1]
        p_7d = df['Close'].iloc[-7] if len(df) >= 7 else df['Close'].iloc[0]
        p_30d = df['Close'].iloc[0]
        return _json_dumps({
            "symbol": symbol,
            "7_day_change_percent": round(((p_now - p_7d)/p_7d)*100, 2),
            "30_day_change_percent": round(((p_now - p_30d)/p_30d)*100, 2)
        })
    except Exception as e: return _json_dumps({"error": str(e)})

# --- FUND TOOLS ---
def get_fund_performance(symbol: str) -> str:
    try:
        fund = bp.Fund(symbol)
        perf = fund.performance
        return _json_dumps({"symbol": symbol, "performance": perf})
    except Exception as e: return _json_dumps({"error": str(e)})

def get_fund_allocation(symbol: str) -> str:
    try:
        fund = bp.Fund(symbol)
        alloc = fund.allocation
        if alloc is not None and hasattr(alloc, 'to_dict'):
            alloc = alloc.to_dict(orient='records')
        return _json_dumps({"symbol": symbol, "allocation": alloc})
    except Exception as e: return _json_dumps({"error": str(e)})

def get_fund_risk_metrics(symbol: str) -> str:
    try:
        fund = bp.Fund(symbol)
        
        risk = "N/A"
        if hasattr(fund, 'risk_metrics'):
            risk_val = fund.risk_metrics
            if callable(risk_val): risk_val = risk_val()
            if hasattr(risk_val, 'to_dict'): risk = risk_val.to_dict(orient='records')
            else: risk = str(risk_val)
            
        sharpe = "N/A"
        if hasattr(fund, 'sharpe_ratio'):
            sharpe_val = fund.sharpe_ratio
            if callable(sharpe_val): sharpe_val = sharpe_val()
            if hasattr(sharpe_val, 'to_dict'): sharpe = sharpe_val.to_dict(orient='records')
            else: sharpe = str(sharpe_val)
            
        return _json_dumps({"symbol": symbol, "Risk_Metrics": risk, "Sharpe_Ratio": sharpe})
    except Exception as e: return _json_dumps({"error": str(e)})

@st.cache_data(ttl=3600, show_spinner=False)
def get_tcmb_rates() -> str:
    """Gets Turkey's current Central Bank (TCMB) interest rates."""
    try:
        import borsapy as bp

        provider = bp._providers.tcmb_rates.TCMBRatesProvider()
        data = provider._fetch_and_parse_table(bp._providers.tcmb_rates.TCMB_URLS["policy"])
        if not data:
            return _json_dumps({"error": "TCMB policy rate data could not be fetched."})

        latest = data[-1]
        return _json_dumps({"tcmb_rates": latest})
    except Exception as e:
        return _json_dumps({"error": f"TCMB execution failed: {str(e)}"})

# --- NEW EXTERNAL & ADVANCED MACRO TOOLS ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_macro_overview() -> str:
    """Gets global markets indices overview (S&P 500, Nasdaq, VIX, DXY, DAX, FTSE 100, Nikkei 225) using global_markets provider."""
    try:
        from providers.global_markets import get_market_overview
        data = get_market_overview()
        return _json_dumps({"global_markets": data})
    except Exception as e:
        return _json_dumps({"error": str(e)})

@st.cache_data(ttl=3600, show_spinner=False)
def get_fear_greed_index() -> str:
    """Gets the current Crypto Fear & Greed Index (alternative.me API) which serves as sentiment indicator for crypto markets."""
    try:
        from providers.fear_greed import get_current
        data = get_current()
        if data:
            return _json_dumps({"fear_and_greed": data})
        return _json_dumps({"error": "Failed to fetch Fear & Greed Index."})
    except Exception as e:
        return _json_dumps({"error": str(e)})

@st.cache_data(ttl=3600, show_spinner=False)
def get_brent_oil_price() -> str:
    """Gets the current Brent Crude Oil price and its historical 1-month and 3-month performance using borsapy.FX."""
    try:
        import borsapy as bp
        fx = bp.FX("BRENT")
        cur = fx.current
        val = cur.get('last') if isinstance(cur, dict) else cur
        if not val:
            return _json_dumps({"error": "Brent oil price not found."})
        
        df_3m = fx.history(period="3mo")
        change_1m = "N/A"
        change_3m = "N/A"
        if not df_3m.empty and len(df_3m) >= 20:
            try:
                past_1m_price = df_3m['Close'].iloc[-21] if len(df_3m) >= 21 else df_3m['Close'].iloc[0]
                change_1m = round(((val - past_1m_price) / past_1m_price) * 100, 2)
                past_3m_price = df_3m['Close'].iloc[0]
                change_3m = round(((val - past_3m_price) / past_3m_price) * 100, 2)
            except:
                pass
        return _json_dumps({
            "symbol": "BRENT",
            "price_USD": val,
            "1_month_change_percent": change_1m,
            "3_month_change_percent": change_3m
        })
    except Exception as e:
        return _json_dumps({"error": str(e)})

@st.cache_data(ttl=3600, show_spinner=False)
def get_turkish_bond_yields() -> str:
    """Gets Turkish government bond yields (2Y, 5Y, 10Y) using borsapy.bonds() and Eurobonds list using borsapy.eurobonds()."""
    try:
        import borsapy as bp
        bonds_df = bp.bonds()
        eurobonds_df = bp.eurobonds()
        
        bonds_list = bonds_df.to_dict(orient='records') if bonds_df is not None and not bonds_df.empty else []
        # Return top 8 eurobonds sorted by yield to keep it compact
        eurobonds_list = []
        if eurobonds_df is not None and not eurobonds_df.empty:
            eurobonds_sorted = eurobonds_df.sort_values(by='ask_yield', ascending=False).head(8)
            eurobonds_list = eurobonds_sorted.to_dict(orient='records')
            
        return _json_dumps({
            "tr_bonds": bonds_list,
            "tr_eurobonds_top_yield": eurobonds_list
        })
    except Exception as e:
        return _json_dumps({"error": str(e)})

# --- ROUTER TRANSFER TOOLS (Mock tools that don't do much but signal intent) ---
def transfer_to_stock_expert() -> str:
    return _json_dumps({"status": "Transferred to Stock Expert. Agent changed."})

def transfer_to_crypto_expert() -> str:
    return _json_dumps({"status": "Transferred to Crypto Expert. Agent changed."})

def transfer_to_fund_expert() -> str:
    return _json_dumps({"status": "Transferred to Fund Expert. Agent changed."})

def transfer_to_macro_expert() -> str:
    return _json_dumps({"status": "Transferred to Macro Expert. Agent changed."})

def transfer_to_warrant_expert() -> str:
    return _json_dumps({"status": "Transferred to Warrant Expert. Agent changed."})
