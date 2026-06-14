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
    """Gets fundamental financial metrics like P/E, P/B, ROE, analyst targets, recommendations for a symbol."""
    ticker = get_ticker_info(symbol)
    if not ticker:
        return json.dumps({"error": f"Symbol {symbol} not found."})
    
    try:
        info = ticker.info
        pe = info.get('trailingPE', 'N/A')
        pb = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity', 'N/A')
        market_cap = info.get('marketCap', 'N/A')
        
        try:
            targets = ticker.analyst_price_targets
        except:
            targets = "N/A"
            
        try:
            recs = ticker.recommendations_summary
        except:
            recs = "N/A"
        
        return json.dumps({
            "symbol": symbol,
            "PE_Ratio": pe,
            "Price_to_Book": pb,
            "ROE": roe,
            "Market_Cap_TRY": market_cap,
            "Analyst_Price_Targets": targets,
            "Recommendations_Summary": recs
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_technical_analysis(symbol: str) -> str:
    """Gets basic technical analysis indicators like RSI, MACD, SMA, Bollinger, Supertrend."""
    try:
        import borsapy as bp
        ticker = bp.Ticker(symbol)
        df = ticker.history(period="1y") # Need more history for SMA200
        if df.empty:
            return json.dumps({"error": "No historical data found for technical analysis."})
        
        # Calculate RSI
        rsi = bp.calculate_rsi(df, period=14)
        latest_rsi = rsi.iloc[-1] if not rsi.empty else 'N/A'
        
        # Calculate MACD
        macd_df = bp.calculate_macd(df)
        latest_macd = macd_df['MACD'].iloc[-1] if 'MACD' in macd_df.columns else 'N/A'
        macdsignal = macd_df['Signal'].iloc[-1] if 'Signal' in macd_df.columns else 'N/A'
        
        # New Indicators
        try:
            sma50 = ticker.sma(sma_period=50)
            sma200 = ticker.sma(sma_period=200)
            bollinger = ticker.bollinger_bands()
            supertrend = ticker.supertrend()
        except:
            sma50, sma200, bollinger, supertrend = "N/A", "N/A", "N/A", "N/A"
            
        return json.dumps({
            "symbol": symbol,
            "RSI_14": float(latest_rsi) if latest_rsi != 'N/A' else 'N/A',
            "MACD": float(latest_macd) if latest_macd != 'N/A' else 'N/A',
            "MACD_Signal": float(macdsignal) if macdsignal != 'N/A' else 'N/A',
            "SMA50": sma50,
            "SMA200": sma200,
            "Bollinger_Bands": bollinger,
            "Supertrend": supertrend
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_currency_and_gold_price(symbol: str) -> str:
    """Gets the live price of a currency or gold (e.g., 'USD', 'EUR', 'gram-altin') and its 1-month and 3-month change."""
    import borsapy as bp
    import yfinance as yf
    try:
        symbol = symbol.upper()
        if symbol in ["XAU", "XAU/USD", "ONS", "GOLD"]:
            # Fallback to yfinance for Gold (XAUUSD=X) since bp.FX may not support it
            ticker = yf.Ticker("GC=F")
            hist = ticker.history(period="3mo")
            if hist.empty:
                return json.dumps({"error": "Gold data not found."})
            
            val = round(hist['Close'].iloc[-1], 2)
            past_1m_price = hist['Close'].iloc[-21] if len(hist) >= 21 else hist['Close'].iloc[0]
            change_1m = round(((val - past_1m_price) / past_1m_price) * 100, 2)
            past_3m_price = hist['Close'].iloc[0]
            change_3m = round(((val - past_3m_price) / past_3m_price) * 100, 2)
            
            return json.dumps({
                "symbol": "XAU/USD",
                "price_USD": val,
                "1_month_change_percent": change_1m,
                "3_month_change_percent": change_3m
            })
            
        fx = bp.FX(symbol)
        cur = fx.current
        val = cur.get('last') if isinstance(cur, dict) else cur
        
        if not val:
            return json.dumps({"error": f"Symbol {symbol} not found. Try 'USD', 'EUR', 'gram-altin'."})
            
        # Calculate history
        df_3m = fx.history(period="3mo")
        change_1m = "N/A"
        change_3m = "N/A"
        if not df_3m.empty and len(df_3m) >= 20: # Approx 1 month
            try:
                # ~21 trading days in a month
                past_1m_price = df_3m['Close'].iloc[-21] if len(df_3m) >= 21 else df_3m['Close'].iloc[0]
                change_1m = round(((val - past_1m_price) / past_1m_price) * 100, 2)
                
                past_3m_price = df_3m['Close'].iloc[0]
                change_3m = round(((val - past_3m_price) / past_3m_price) * 100, 2)
            except:
                pass
                
        return json.dumps({
            "symbol": symbol,
            "price_TRY": val,
            "1_month_change_percent": change_1m,
            "3_month_change_percent": change_3m
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_latest_news(symbol: str) -> str:
    """Gets the latest KAP (Public Disclosure) news for a specific BIST symbol."""
    import borsapy as bp
    import json
    
    try:
        ticker = bp.Ticker(symbol)
        news_df = ticker.news
        if news_df is not None and not news_df.empty:
            items = []
            for _, row in news_df.head(5).iterrows():
                items.append(f"- {row['Date']}: {row['Title']}")
            return json.dumps({
                "symbol": symbol,
                "latest_news": items
            })
        else:
            return json.dumps({"error": f"No recent news found for {symbol}."})
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_global_news(category: str = 'all') -> str:
    """
    Birden fazla kaynaktan ekonomi ve piyasa haberlerini toplar.
    category: 'all' | 'crypto' | 'commodity' | 'macro' | 'turkey'
    Kategoriye göre ilgili kaynaklar önceliklendirilir.
    """
    import requests
    import xml.etree.ElementTree as ET
    import json
    from concurrent.futures import ThreadPoolExecutor, as_completed

    # Kaynak tanımları: (isim, url, etiketler)
    ALL_SOURCES = [
        ("TRT Haber",        "https://www.trthaber.com/ekonomi_articles.rss",         ["turkey", "macro", "all"]),
        ("Bloomberg HT",     "https://www.bloomberght.com/rss",                        ["turkey", "macro", "all"]),
        ("Dunya Gazetesi",   "https://www.dunya.com/rss",                              ["turkey", "all"]),
        ("Investing Genel",  "https://www.investing.com/rss/news.rss",                 ["macro", "all"]),
        ("Investing Emtia",  "https://www.investing.com/rss/news_14.rss",              ["commodity", "macro", "all"]),
        ("Investing Kripto", "https://www.investing.com/rss/news_301.rss",             ["crypto", "all"]),
        ("MarketWatch",      "https://feeds.content.dowjones.io/public/rss/mw_topstories", ["macro", "all"]),
        ("CNBC Markets",     "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19836768", ["macro", "all"]),
        ("Yahoo Finance",    "https://finance.yahoo.com/news/rssindex",                ["macro", "all"]),
    ]

    # Kategori filtresi
    cat = category.lower().strip()
    sources = [(n, u) for n, u, tags in ALL_SOURCES if cat in tags]

    # Maksimum kaynak sayısı ve her kaynaktan alınacak haber sayısı
    MAX_SOURCES = 5 if cat == 'all' else 4
    PER_SOURCE = 3 if cat == 'all' else 5
    sources = sources[:MAX_SOURCES]

    headers = {'User-Agent': 'Mozilla/5.0'}

    def fetch_source(name, url):
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code != 200:
                return []
            root = ET.fromstring(r.text)
            items = []
            for item in root.findall('.//item')[:PER_SOURCE]:
                title_el = item.find('title')
                date_el = item.find('pubDate')
                title = title_el.text.strip() if title_el is not None and title_el.text else None
                date = date_el.text.strip() if date_el is not None and date_el.text else "Son"
                if title:
                    items.append(f"[{name}] {date[:16]}: {title}")
            return items
        except Exception:
            return []

    all_headlines = []
    with ThreadPoolExecutor(max_workers=len(sources)) as executor:
        futures = {executor.submit(fetch_source, n, u): n for n, u in sources}
        for future in as_completed(futures):
            all_headlines.extend(future.result())

    if not all_headlines:
        return json.dumps({"error": "Hiçbir haber kaynağına ulaşılamadı."})

    return json.dumps({
        "category": category,
        "sources_fetched": len(sources),
        "total_headlines": len(all_headlines),
        "news": all_headlines
    })


def get_macro_events(*args, **kwargs) -> str:
    """Gets past week and upcoming week high-importance macroeconomic events with expectations."""
    from utils.data_loader import get_real_policy_rate
    import borsapy as bp
    from datetime import datetime, timedelta
    import json
    import pandas as pd
    
    try:
        rate = get_real_policy_rate()
        today = datetime.now()
        start_dt = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_dt = (today + timedelta(days=7)).strftime('%Y-%m-%d')
        
        cal = bp.EconomicCalendar()
        cal_df = cal.events(start=start_dt, end=end_dt, importance='high')
        
        events = []
        if cal_df is not None and not cal_df.empty:
            for _, row in cal_df.iterrows():
                # Some events might have 'None' for actual/forecast, handle gracefully
                actual = row['Actual'] if pd.notna(row['Actual']) else "?"
                forecast = row['Forecast'] if pd.notna(row['Forecast']) else "?"
                previous = row['Previous'] if pd.notna(row['Previous']) else "?"
                events.append(f"[{row['Date']} {row['Time']}] {row['Country']} - {row['Event']} | Beklenti: {forecast}, Gerçekleşen: {actual}, Önceki: {previous}")
                
        return json.dumps({
            "TCMB_Policy_Rate": rate if rate else "N/A",
            "Context_Window": f"{start_dt} to {end_dt}",
            "Macro_Events": events if events else "Bu aralıkta yüksek önem dereceli kritik bir veri akışı bulunmuyor."
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

# Mapping dictionary for tool calling router
AI_TOOLS_MAP = {
    "get_live_price": get_live_price,
    "get_financial_metrics": get_financial_metrics,
    "get_technical_analysis": get_technical_analysis,
    "get_currency_and_gold_price": get_currency_and_gold_price,
    "get_latest_news": get_latest_news,
    "get_global_news": get_global_news,
    "get_macro_events": get_macro_events
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
            "description": "Gets fundamental metrics (P/E, P/B, ROE) and EXPERT data (Analyst Price Targets, Buy/Sell Recommendations) for a company.",
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
            "description": "Calculates technical indicators like RSI, MACD, SMA50, SMA200, Bollinger Bands, and Supertrend for a given stock.",
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
            "description": "Gets the live price and 1-month/3-month percentage changes of a currency or gold (e.g., 'USD', 'EUR', 'gram-altin', 'ons-altin'). Use this when the user asks for gold, dollar, euro, etc.",
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
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_news",
            "description": "Fetches the 5 most recent KAP (Public Disclosure) news for a specific BIST stock symbol. Crucial for understanding fundamental triggers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock symbol, e.g. 'THYAO', 'ASELS'"
                    }
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_global_news",
            "description": "Fetches the 10 most recent global economic and market news headlines. You MUST use this tool for EVERY specific stock analysis to understand the macro environment, as well as for general market questions.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_macro_events",
            "description": "Fetches the upcoming/today's high-importance macroeconomic events (Economic Calendar) and current TCMB policy rate. You MUST use this tool for EVERY specific stock analysis to understand the macro environment, as well as for general market questions.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]
