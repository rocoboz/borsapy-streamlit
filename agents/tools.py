import json
import borsapy as bp
from utils.data_loader import get_ticker_info

# --- STOCK TOOLS (Similar to old utils/ai_tools.py) ---
def get_stock_financials(symbol: str) -> str:
    ticker = get_ticker_info(symbol)
    if not ticker: return json.dumps({"error": f"Symbol {symbol} not found."})
    try:
        usd_rate = float(bp.FX('USD').current['last'])
        info = ticker.info
        targets = ticker.analyst_price_targets if hasattr(ticker, 'analyst_price_targets') else "N/A"
        if isinstance(targets, dict):
            for k in ['current', 'low', 'high', 'mean', 'median']:
                if k in targets and targets[k]:
                    targets[k] = round(targets[k] / usd_rate, 2)
                    
        return json.dumps({
            "symbol": symbol,
            "Currency": "USD",
            "PE_Ratio": info.get('trailingPE', 'N/A'),
            "Price_to_Book": info.get('priceToBook', 'N/A'),
            "ROE": info.get('returnOnEquity', 'N/A'),
            "Analyst_Price_Targets_USD": targets,
            "Recommendations": ticker.recommendations_summary if hasattr(ticker, 'recommendations_summary') else "N/A"
        })
    except Exception as e: return json.dumps({"error": str(e)})

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
            
    return json.dumps({"peer_comparison": results})

def screen_bist_stocks(max_pe: float = None, min_roe: float = None) -> str:
    """Tarayıcı (Screener) ile BIST30'da ucuz / kârlı hisseleri bulur."""
    import borsapy as bp
    try:
        screener = bp.Screener()
        screener.set_index('BIST30')
        if max_pe is not None:
            screener.add_filter('pe', max=float(max_pe))
        if min_roe is not None:
            screener.add_filter('roe', min=float(min_roe))
            
        df = screener.run()
        if df.empty:
            return json.dumps({"error": "No stocks matched the criteria."})
        
        # Sadece ilk 5 sonucu dönelim (Token tasarrufu)
        df_top = df.head(5)
        # Sadece sembol ve ismi dönelim (ve varsa kriterleri)
        result_list = df_top.to_dict(orient='records')
        return json.dumps({"screener_results": result_list})
    except Exception as e:
        return json.dumps({"error": f"Screener execution failed: {str(e)}"})

def get_stock_technicals(symbol: str) -> str:
    try:
        ticker = bp.Ticker(symbol)
        df = ticker.history(period="1y")
        if df.empty: return json.dumps({"error": "No data"})
        
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
        
        return json.dumps({
            "symbol": symbol,
            "Currency": "USD",
            "Price_USD": float(df['Close'].iloc[-1]),
            "RSI_14": float(rsi.iloc[-1]) if not rsi.empty else 'N/A',
            "MACD": float(macd_df['MACD'].iloc[-1]) if 'MACD' in macd_df.columns else 'N/A',
            "SMA50_USD": sma50,
            "SMA200_USD": sma200,
            "Supertrend_USD": supertrend
        })
    except Exception as e: return json.dumps({"error": str(e)})


# --- CRYPTO TOOLS ---
def get_crypto_technicals(symbol: str) -> str:
    """Gets crypto technicals using borsapy.Crypto"""
    try:
        symbol = symbol.replace("-", "").upper()
        if not symbol.endswith("USDT") and not symbol.endswith("TRY"): symbol += "USDT"
        crypto = bp.Crypto(symbol)
        df = crypto.history(period="6mo")
        if df.empty: return json.dumps({"error": "No data"})
        rsi = bp.calculate_rsi(df, period=14)
        macd_df = bp.calculate_macd(df)
        return json.dumps({
            "symbol": symbol,
            "Price": df['Close'].iloc[-1],
            "RSI_14": float(rsi.iloc[-1]) if not rsi.empty else 'N/A',
            "MACD": float(macd_df['MACD'].iloc[-1]) if 'MACD' in macd_df.columns else 'N/A',
        })
    except Exception as e: return json.dumps({"error": str(e)})

def get_crypto_momentum(symbol: str) -> str:
    """Gets crypto recent performance"""
    try:
        symbol = symbol.replace("-", "").upper()
        if not symbol.endswith("USDT") and not symbol.endswith("TRY"): symbol += "USDT"
        crypto = bp.Crypto(symbol)
        df = crypto.history(period="1mo")
        if df.empty: return json.dumps({"error": "No data"})
        p_now = df['Close'].iloc[-1]
        p_7d = df['Close'].iloc[-7] if len(df) >= 7 else df['Close'].iloc[0]
        p_30d = df['Close'].iloc[0]
        return json.dumps({
            "symbol": symbol,
            "7_day_change_percent": round(((p_now - p_7d)/p_7d)*100, 2),
            "30_day_change_percent": round(((p_now - p_30d)/p_30d)*100, 2)
        })
    except Exception as e: return json.dumps({"error": str(e)})

# --- FUND TOOLS ---
def get_fund_performance(symbol: str) -> str:
    try:
        fund = bp.Fund(symbol)
        perf = fund.performance
        return json.dumps({"symbol": symbol, "performance": perf})
    except Exception as e: return json.dumps({"error": str(e)})

def get_fund_allocation(symbol: str) -> str:
    try:
        fund = bp.Fund(symbol)
        alloc = fund.allocation
        if alloc is not None and hasattr(alloc, 'to_dict'):
            alloc = alloc.to_dict(orient='records')
        return json.dumps({"symbol": symbol, "allocation": alloc})
    except Exception as e: return json.dumps({"error": str(e)})

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
            
        return json.dumps({"symbol": symbol, "Risk_Metrics": risk, "Sharpe_Ratio": sharpe})
    except Exception as e: return json.dumps({"error": str(e)})

def get_tcmb_rates() -> str:
    """Gets Turkey's current Central Bank (TCMB) interest rates."""
    import borsapy as bp
    try:
        tcmb = bp.TCMB()
        # Ensure we convert pandas dataframe to dictionary correctly
        rates_df = tcmb.rates
        if rates_df is not None and not rates_df.empty:
            return json.dumps({"tcmb_rates": rates_df.to_dict(orient='records')})
        return json.dumps({"tcmb_rates": "No data"})
    except Exception as e:
        return json.dumps({"error": f"TCMB execution failed: {str(e)}"})

# --- ROUTER TRANSFER TOOLS (Mock tools that don't do much but signal intent) ---
def transfer_to_stock_expert() -> str:
    return json.dumps({"status": "Transferred to Stock Expert. Ajan değişti."})

def transfer_to_crypto_expert() -> str:
    return json.dumps({"status": "Transferred to Crypto Expert. Ajan değişti."})

def transfer_to_fund_expert() -> str:
    return json.dumps({"status": "Transferred to Fund Expert. Ajan değişti."})

def transfer_to_macro_expert() -> str:
    return json.dumps({"status": "Transferred to Macro Expert. Ajan değişti."})
