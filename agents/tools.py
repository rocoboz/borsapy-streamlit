import json
import borsapy as bp
from utils.data_loader import get_ticker_info

# --- STOCK TOOLS (Similar to old utils/ai_tools.py) ---
def get_stock_financials(symbol: str) -> str:
    ticker = get_ticker_info(symbol)
    if not ticker: return json.dumps({"error": f"Symbol {symbol} not found."})
    try:
        info = ticker.info
        targets = ticker.analyst_price_targets if hasattr(ticker, 'analyst_price_targets') else "N/A"
        recs = ticker.recommendations_summary if hasattr(ticker, 'recommendations_summary') else "N/A"
        return json.dumps({
            "symbol": symbol,
            "PE_Ratio": info.get('trailingPE', 'N/A'),
            "Price_to_Book": info.get('priceToBook', 'N/A'),
            "ROE": info.get('returnOnEquity', 'N/A'),
            "Analyst_Price_Targets": targets,
            "Recommendations": recs
        })
    except Exception as e: return json.dumps({"error": str(e)})

def get_stock_technicals(symbol: str) -> str:
    try:
        ticker = bp.Ticker(symbol)
        df = ticker.history(period="1y")
        if df.empty: return json.dumps({"error": "No data"})
        rsi = bp.calculate_rsi(df, period=14)
        macd_df = bp.calculate_macd(df)
        try: sma50 = ticker.sma(sma_period=50)
        except: sma50 = "N/A"
        try: sma200 = ticker.sma(sma_period=200)
        except: sma200 = "N/A"
        try: supertrend = ticker.supertrend()
        except: supertrend = "N/A"
        
        return json.dumps({
            "symbol": symbol,
            "Price": df['Close'].iloc[-1],
            "RSI_14": float(rsi.iloc[-1]) if not rsi.empty else 'N/A',
            "MACD": float(macd_df['MACD'].iloc[-1]) if 'MACD' in macd_df.columns else 'N/A',
            "SMA50": sma50,
            "SMA200": sma200,
            "Supertrend": supertrend
        })
    except Exception as e: return json.dumps({"error": str(e)})


# --- CRYPTO TOOLS ---
def get_crypto_technicals(symbol: str) -> str:
    """Gets crypto technicals using borsapy.Crypto"""
    try:
        if not symbol.endswith("-USD"): symbol += "-USD"
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
        if not symbol.endswith("-USD"): symbol += "-USD"
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
        return json.dumps({"symbol": symbol, "allocation": alloc})
    except Exception as e: return json.dumps({"error": str(e)})

def get_fund_risk_metrics(symbol: str) -> str:
    try:
        fund = bp.Fund(symbol)
        risk = fund.risk_metrics if hasattr(fund, 'risk_metrics') else "N/A"
        sharpe = fund.sharpe_ratio if hasattr(fund, 'sharpe_ratio') else "N/A"
        return json.dumps({"symbol": symbol, "Risk_Metrics": risk, "Sharpe_Ratio": sharpe})
    except Exception as e: return json.dumps({"error": str(e)})

# --- ROUTER TRANSFER TOOLS (Mock tools that don't do much but signal intent) ---
def transfer_to_stock_expert() -> str:
    return json.dumps({"status": "Transferred to Stock Expert. Ajan değişti."})

def transfer_to_crypto_expert() -> str:
    return json.dumps({"status": "Transferred to Crypto Expert. Ajan değişti."})

def transfer_to_fund_expert() -> str:
    return json.dumps({"status": "Transferred to Fund Expert. Ajan değişti."})
