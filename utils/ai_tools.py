import json
import traceback
from utils.data_loader import get_ticker_info

def get_live_price(symbol: str) -> str:
    """Gets the live price and change percentage of a symbol."""
    ticker = get_ticker_info(symbol)
    if not ticker:
        return json.dumps({"error": f"Symbol {symbol} not found."})
    
    try:
        info = ticker.info
        price = info.get('last', info.get('currentPrice', info.get('regularMarketPrice', 'N/A')))
        chg = info.get('change_percent', info.get('regularMarketChangePercent', 'N/A'))
        return json.dumps({
            "symbol": symbol,
            "price_TRY": price,
            "daily_change_percent": chg
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_financial_metrics(symbol: str) -> str:
    """Gets fundamental financial metrics like P/E, P/B, ROE for a symbol."""
    ticker = get_ticker_info(symbol)
    if not ticker:
        return json.dumps({"error": f"Symbol {symbol} not found."})
    
    try:
        info = ticker.info
        pe = info.get('trailingPE', 'N/A')
        pb = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity', 'N/A')
        market_cap = info.get('marketCap', 'N/A')
        
        return json.dumps({
            "symbol": symbol,
            "PE_Ratio": pe,
            "Price_to_Book": pb,
            "ROE": roe,
            "Market_Cap_TRY": market_cap
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_technical_analysis(symbol: str) -> str:
    """Gets basic technical analysis indicators like RSI and MACD."""
    # To keep it fast, we will just fetch history and calculate RSI via borsapy
    try:
        import borsapy as bp
        ticker = bp.Ticker(symbol)
        df = ticker.history(period="1mo")
        if df.empty:
            return json.dumps({"error": "No historical data found for technical analysis."})
        
        # Calculate a simple RSI approximation if borsapy TechnicalAnalyzer is heavy
        # Actually borsapy has bp.calculate_rsi
        df = bp.calculate_rsi(df, period=14)
        latest_rsi = df['RSI_14'].iloc[-1] if 'RSI_14' in df.columns else 'N/A'
        
        df = bp.calculate_macd(df)
        latest_macd = df['MACD_12_26_9'].iloc[-1] if 'MACD_12_26_9' in df.columns else 'N/A'
        macdsignal = df['MACDs_12_26_9'].iloc[-1] if 'MACDs_12_26_9' in df.columns else 'N/A'
        
        return json.dumps({
            "symbol": symbol,
            "RSI_14": float(latest_rsi) if latest_rsi != 'N/A' else 'N/A',
            "MACD": float(latest_macd) if latest_macd != 'N/A' else 'N/A',
            "MACD_Signal": float(macdsignal) if macdsignal != 'N/A' else 'N/A'
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_currency_and_gold_price(symbol: str) -> str:
    """Gets the live price of a currency or gold (e.g., 'USD', 'EUR', 'gram-altin')."""
    from utils.data_loader import get_fx_rate
    try:
        val, _ = get_fx_rate(symbol)
        if val:
            return json.dumps({
                "symbol": symbol,
                "price_TRY": val
            })
        else:
            return json.dumps({"error": f"Symbol {symbol} not found. Try 'USD', 'EUR', 'gram-altin' or 'ons-altin'."})
    except Exception as e:
        return json.dumps({"error": str(e)})

# Mapping dictionary for tool calling router
AI_TOOLS_MAP = {
    "get_live_price": get_live_price,
    "get_financial_metrics": get_financial_metrics,
    "get_technical_analysis": get_technical_analysis,
    "get_currency_and_gold_price": get_currency_and_gold_price
}

# OpenAI schema format
AI_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_live_price",
            "description": "Gets the live market price and daily change percentage for a stock or fund symbol in Borsa Istanbul.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock or fund symbol, e.g. 'THYAO', 'TUPRS', 'AFT'"
                    }
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_metrics",
            "description": "Gets fundamental financial metrics like P/E (F/K), P/B (PD/DD), ROE, and Market Cap for a company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock symbol, e.g. 'THYAO'"
                    }
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_technical_analysis",
            "description": "Calculates and returns technical indicators like RSI and MACD for a given stock symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock symbol, e.g. 'THYAO'"
                    }
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_currency_and_gold_price",
            "description": "Gets the live price of a currency or gold (e.g., 'USD', 'EUR', 'gram-altin', 'ons-altin'). Use this when the user asks for gold, dollar, euro, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The currency or gold symbol, e.g., 'USD', 'EUR', 'gram-altin', 'ons-altin'"
                    }
                },
                "required": ["symbol"]
            }
        }
    }
]
