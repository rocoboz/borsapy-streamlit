"""
Fear & Greed Index verisi — alternative.me API (key gerektirmez).

Kripto piyasası duygu göstergesi:
  0-24   → Extreme Fear (Aşırı Korku)
  25-49  → Fear (Korku)
  50     → Neutral (Nötr)
  51-74  → Greed (Açgözlülük)
  75-100 → Extreme Greed (Aşırı Açgözlülük)

Kaynak: https://api.alternative.me/fng/
"""

from __future__ import annotations
import requests

_API_URL = "https://api.alternative.me/fng/?limit={limit}&format=json"

# Türkçe etiket haritası
_TR_LABELS: dict[str, str] = {
    "Extreme Fear": "Aşırı Korku",
    "Fear": "Korku",
    "Neutral": "Nötr",
    "Greed": "Açgözlülük",
    "Extreme Greed": "Aşırı Açgözlülük",
}


def get_fear_greed(limit: int = 1) -> list[dict] | None:
    """
    Fear & Greed Index'ini döner.

    Args:
        limit: Kaç günlük veri dönsün (1 = sadece bugün)

    Returns:
        [
          {
            "value": 42,
            "classification": "Fear",
            "classification_tr": "Korku",
            "timestamp": "2024-06-12"
          },
          ...
        ]
        veya None (API erişilemezse)
    """
    try:
        r = requests.get(_API_URL.format(limit=limit), timeout=5)
        if r.status_code != 200:
            return None
        data = r.json().get("data", [])
        results = []
        for item in data:
            label_en = item.get("value_classification", "")
            results.append({
                "value": int(item["value"]),
                "classification": label_en,
                "classification_tr": _TR_LABELS.get(label_en, label_en),
                "timestamp": item.get("timestamp", ""),
            })
        return results if results else None
    except Exception:
        return None


def get_current() -> dict | None:
    """Bugünkü Fear & Greed değerini döner (tek kayıt)."""
    result = get_fear_greed(limit=1)
    return result[0] if result else None
