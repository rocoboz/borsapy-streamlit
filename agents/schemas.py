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
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_warrant_expert",
            "description": "Call this to transfer the conversation to the Warrant (Varant) & Derivatives Expert. Use this when the user explicitly asks for warrants (varant), leveraged trades, or options for a specific stock/index/commodity.",
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
            "description": "BIST hisselerini tarar ve en iyi/ucuz/kârlı hisseleri getirir. Kullanıcı 'hisse öner', 'alınabilir hisse', 'ucuz hisse bul' dediğinde ÖNCELİKLE bu aracı kullan. Tek tek hisse sormak yerine bu tarayıcıyı kullan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {"type": "string", "description": "Endeks: 'BIST30', 'BIST100', 'BIST_ALL'. Varsayılan: 'BIST100'"},
                    "max_pe": {"type": "number", "description": "Maksimum F/K oranı (opsiyonel, ör: 10.0)"},
                    "min_roe": {"type": "number", "description": "Minimum Özsermaye Karlılığı % (opsiyonel, ör: 20.0)"},
                    "min_upside": {"type": "number", "description": "Minimum analist hedef yükseliş potansiyeli % (opsiyonel, ör: 20.0)"},
                    "top_n": {"type": "integer", "description": "Kaç hisse dönsün (varsayılan: 8)"}
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
            "description": "TRT, Bloomberg HT, Investing.com, MarketWatch, CNBC ve Yahoo Finance gibi birden fazla kaynaktan guncel ekonomi ve piyasa haberlerini toplar. category ile konu filtreleyebilirsin: 'all' (varsayilan), 'crypto' (kripto), 'commodity' (emtia/altin), 'macro' (genel makro), 'turkey' (yerel Turkiye).",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Haber kategorisi: 'all' | 'crypto' | 'commodity' | 'macro' | 'turkey'. Varsayilan: 'all'"
                    }
                }
            }
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
            "description": "Kripto için özellikle 'crypto' kategorisiyle çağır. Investing Kripto, MarketWatch, CNBC, Yahoo Finance kaynaklarindan haber çeker. category: 'crypto' | 'macro' | 'all'",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Haber kategorisi: 'crypto' | 'macro' | 'all'. Kripto sorularinda 'crypto' kullan."
                    }
                }
            }
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
            "name": "screen_top_funds",
            "description": "TEFAS fonlarını performansa göre sıralayarak en iyi fonları getirir. Kullanıcı 'en iyi fonları getir', 'fon öner', 'hangi fonu alsam' dediğinde ÖNCELİKLE bu aracı kullan. Tek tek fon sormak yerine bu toplu tarayıcıyı kullan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "period": {"type": "string", "description": "Sıralama dönemi: '1m', '3m', '6m', 'ytd', '1y', '3y'. Varsayılan: '1y'"},
                    "fund_type": {"type": "string", "description": "Fon tipi: 'YAT' (yatırım fonu, varsayılan), 'EME' (emeklilik)"},
                    "top_n": {"type": "integer", "description": "Kaç fon dönsün (varsayılan: 8)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_fund_performance",
            "description": "Belirli bir TEFAS fonu için getiri bilgisi getirir (1A, 3A, 1Y, YTD). Kullanıcı spesifik bir fon kodu verdiğinde kullan (AFT, YAS gibi).",
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
            "description": "TRT, Bloomberg HT, Investing.com, MarketWatch, CNBC ve Yahoo Finance gibi birden fazla kaynaktan guncel ekonomi ve piyasa haberlerini toplar. category ile konu filtreleyebilirsin: 'all' (varsayilan), 'crypto' (kripto), 'commodity' (emtia/altin), 'macro' (genel makro), 'turkey' (yerel Turkiye).",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Haber kategorisi: 'all' | 'crypto' | 'commodity' | 'macro' | 'turkey'. Varsayilan: 'all'"
                    }
                }
            }
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
            "description": "TRT, Bloomberg HT, Investing.com, MarketWatch, CNBC ve Yahoo Finance gibi kaynaklardan haber çeker. Emtia/Altin analizlerinde 'commodity', genel makroda 'macro', Türkiye odaklı sorularda 'turkey' kategorisi kullan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Haber kategorisi: 'all' | 'commodity' | 'macro' | 'turkey'. Emtia/Altin sorularinda 'commodity' kullan."
                    }
                }
            }
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

WARRANT_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_technicals",
            "description": "Gets RSI, MACD, SMA50, SMA200, Supertrend for the underlying stock.",
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
            "name": "get_currency_and_gold_price",
            "description": "Gets live price for underlying commodities (e.g., 'ons-altin', 'USD').",
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
            "description": "Fetches the 5 most recent KAP news for a specific BIST stock symbol. News catalysts are critical for warrant direction.",
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
            "name": "get_macro_events",
            "description": "Fetches high-importance macroeconomic events that could affect the underlying asset.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]
