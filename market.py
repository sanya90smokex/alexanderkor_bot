# market.py
import requests

BINANCE_BASE = "https://api.binance.com"

def get_price(symbol: str) -> float:
    """
    Текущая цена спота на Binance через публичный REST (без API ключей).
    """
    r = requests.get(f"{BINANCE_BASE}/api/v3/ticker/price", params={"symbol": symbol.upper()}, timeout=5)
    r.raise_for_status()
    data = r.json()
    return float(data["price"])
