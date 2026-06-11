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
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_macro_expert",
            "description": "Call this to transfer the conversation to the Macro/Commodity Expert. Use this when the user asks about Interest Rates, Gold (Altın), USD (Dolar), Euro, Bonds, or broad global/geopolitical news (savaş vb).",
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
            "name": "get_multiple_stock_financials",
            "description": "Gets P/E, P/B, ROE, and analyst targets for multiple BIST stocks. Use this to do PEER COMPARISON (e.g. comparing ASELS to OTKAR).",
            "parameters": {
                "type": "object",
                "properties": {"symbols": {"type": "string", "description": "Comma-separated stock symbols (e.g. 'ASELS, OTKAR, SDTTR')"}},
                "required": ["symbols"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "screen_bist_stocks",
            "description": "Screens BIST30 stocks based on criteria like max PE (max_pe) or min ROE (min_roe). Returns top 5 cheap/profitable stocks. Call this when user asks 'Bana ucuz hisseleri bul' or 'Hisse öner'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_pe": {"type": "number", "description": "Maximum Price to Earnings ratio (e.g. 10.0)"},
                    "min_roe": {"type": "number", "description": "Minimum Return on Equity percentage (e.g. 20.0)"}
                }
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
    },
    {
        "type": "function",
        "function": {
            "name": "get_macro_events",
            "description": "Fetches the past and upcoming high-importance macroeconomic events with expectations vs actuals.",
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
            "description": "Fetches the past and upcoming high-importance macroeconomic events with expectations vs actuals.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

MACRO_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_macro_events",
            "description": "Fetches the past and upcoming high-importance macroeconomic events (Economic Calendar) to analyze rate expectations.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_global_news",
            "description": "Fetches the 10 most recent global economic, geopolitical, and market news headlines.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_currency_and_gold_price",
            "description": "Gets the live price and historical change of a currency or gold (e.g., 'USD', 'EUR', 'gram-altin', 'ons-altin').",
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
            "name": "get_tcmb_rates",
            "description": "Gets Turkey's current Central Bank (TCMB) interest rates (Policy Rate, Overnight Rate). Use this to analyze Turkey's monetary policy.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]
