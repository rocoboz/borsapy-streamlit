"""
Global piyasa verileri — Yahoo Finance üzerinden (key gerektirmez).

Desteklenen veriler:
  - S&P 500, Nasdaq, VIX, DXY, DAX, FTSE 100, Nikkei 225

Kaynak: Yahoo Finance Chart API (v8)
"""

from __future__ import annotations
import requests

# Sembol haritası: kullanıcı dostu isim -> Yahoo Finance sembolü
SYMBOLS: dict[str, str] = {
    "sp500":   "^GSPC",
    "nasdaq":  "^IXIC",
    "vix":     "^VIX",
    "dxy":     "DX-Y.NYB",
    "dax":     "^GDAXI",
    "ftse100": "^FTSE",
    "nikkei":  "^N225",
}

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"


def _fetch_quote(yahoo_symbol: str) -> dict | None:
    """Yahoo Finance'ten tek bir sembolün fiyatını çeker. None döner başarısızlıkta."""
    try:
        url = _BASE_URL.format(symbol=yahoo_symbol)
        r = requests.get(url, headers=_HEADERS, timeout=6)
        if r.status_code != 200:
            return None
        result = r.json()["chart"]["result"]
        if not result:
            return None
        meta = result[0]["meta"]
        price = meta.get("regularMarketPrice")
        prev = meta.get("previousClose") or meta.get("chartPreviousClose")
        change_pct = round(((price - prev) / prev) * 100, 2) if price and prev else None
        return {
            "price": round(price, 2) if price else None,
            "prev_close": round(prev, 2) if prev else None,
            "change_pct": change_pct,
        }
    except Exception:
        return None


def get_market_overview() -> dict[str, dict | None]:
    """
    Tüm desteklenen global piyasaların anlık fiyatlarını döner.

    Returns:
        {
          "sp500":   {"price": 5250.13, "prev_close": 5200.0, "change_pct": 0.96},
          "vix":     {"price": 19.0, ...},
          ...
          "<key>":  None   ← başarısız olan semboller
        }
    """
    result = {}
    for name, yahoo_sym in SYMBOLS.items():
        result[name] = _fetch_quote(yahoo_sym)
    return result


def get_quote(key: str) -> dict | None:
    """
    Tek bir sembolün fiyatını döner.

    Args:
        key: SYMBOLS sözlüğündeki anahtar (örn. 'sp500', 'vix', 'dxy')

    Returns:
        {"price": ..., "prev_close": ..., "change_pct": ...}  veya  None
    """
    key = key.lower().strip()
    if key not in SYMBOLS:
        raise ValueError(f"Desteklenmeyen sembol: '{key}'. Geçerli seçenekler: {list(SYMBOLS)}")
    return _fetch_quote(SYMBOLS[key])


def available_symbols() -> list[str]:
    """Desteklenen sembol anahtarlarını döner."""
    return list(SYMBOLS.keys())
