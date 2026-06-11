ROUTER_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "transfer_to_stock_expert",
            "description": "Call this to transfer the conversation to the Stock/Macro Expert Agent. Use this when the user asks about BIST stocks (e.g. ASELS, THYAO), specific companies, or general macro economy.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_crypto_expert",
            "description": "Call this to transfer the conversation to the Crypto Expert Agent. Use this when the user asks about Bitcoin, Ethereum, crypto markets or altcoins.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_fund_expert",
            "description": "Call this to transfer the conversation to the Mutual Fund (Yatırım Fonu) Expert Agent. Use this when the user asks about TEFAS funds, mutual funds, or portfolio allocation.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

STOCK_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_financials",
            "description": "Gets P/E, P/B, ROE, analyst targets and recommendations for a BIST stock.",
            "parameters": {
                "type": "object",
                "properties": {"symbol": {"type": "string"}},
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_technicals",
            "description": "Gets RSI, MACD, SMA50, SMA200, Supertrend for a BIST stock.",
            "parameters": {
                "type": "object",
                "properties": {"symbol": {"type": "string"}},
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_news",
            "description": "Fetches the 5 most recent KAP (Public Disclosure) news for a specific BIST stock symbol.",
            "parameters": {
                "type": "object",
                "properties": {"symbol": {"type": "string"}},
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_global_news",
            "description": "Fetches the 10 most recent global economic and market news headlines.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_macro_events",
            "description": "Fetches the upcoming/today's high-importance macroeconomic events (Economic Calendar).",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

CRYPTO_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_crypto_technicals",
            "description": "Gets RSI, MACD, Price for a crypto symbol (e.g., BTC-USD, ETH-USD).",
            "parameters": {
                "type": "object",
                "properties": {"symbol": {"type": "string"}},
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_crypto_momentum",
            "description": "Gets 7-day and 30-day percentage changes for a crypto symbol.",
            "parameters": {
                "type": "object",
                "properties": {"symbol": {"type": "string"}},
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_global_news",
            "description": "Fetches global economic news. Important for crypto (e.g. FED news).",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

FUND_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_fund_performance",
            "description": "Gets historical returns (1M, 3M, 1Y, YTD) for a TEFAS mutual fund (e.g., 'AFT', 'YAS').",
            "parameters": {
                "type": "object",
                "properties": {"symbol": {"type": "string"}},
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_fund_allocation",
            "description": "Gets portfolio allocation (asset distribution like % Equity, % Gold) for a fund.",
            "parameters": {
                "type": "object",
                "properties": {"symbol": {"type": "string"}},
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_fund_risk_metrics",
            "description": "Gets Risk metrics, Volatility, and Sharpe Ratio for a fund.",
            "parameters": {
                "type": "object",
                "properties": {"symbol": {"type": "string"}},
                "required": ["symbol"]
            }
        }
    }
]
