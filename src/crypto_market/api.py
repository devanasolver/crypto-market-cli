"""Free market data from CoinGecko (no API key) and alternative.me (fear & greed)."""

from __future__ import annotations

import requests

COINGECKO = "https://api.coingecko.com/api/v3"
FEAR_GREED = "https://api.alternative.me/fng/"
HEADERS = {"User-Agent": "crypto-market-cli/0.1", "Accept": "application/json"}
TIMEOUT = 20


def _get(url: str, params: dict | None = None):
    resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def top_coins(limit: int = 25) -> list[dict]:
    data = _get(f"{COINGECKO}/coins/markets", params={
        "vs_currency": "usd", "order": "market_cap_desc",
        "per_page": min(limit, 250), "page": 1, "price_change_percentage": "24h,7d",
    })
    return [
        {
            "rank": c.get("market_cap_rank"),
            "name": c.get("name"),
            "symbol": (c.get("symbol") or "").upper(),
            "price_usd": c.get("current_price"),
            "change_24h_pct": c.get("price_change_percentage_24h"),
            "change_7d_pct": c.get("price_change_percentage_7d_in_currency"),
            "market_cap_usd": c.get("market_cap"),
        }
        for c in data
    ]


def movers(limit: int = 10) -> dict:
    coins = top_coins(250)
    valid = [c for c in coins if c["change_24h_pct"] is not None]
    ordered = sorted(valid, key=lambda c: c["change_24h_pct"])
    return {"gainers": ordered[-limit:][::-1], "losers": ordered[:limit]}


def narratives(limit: int = 20, min_market_cap: float = 100_000_000) -> list[dict]:
    """CoinGecko coin categories ranked by 24h market-cap change - what the market calls narratives."""
    data = _get(f"{COINGECKO}/coins/categories")
    rows = [
        {
            "category": c.get("name"),
            "change_24h_pct": c.get("market_cap_change_24h"),
            "market_cap_usd": c.get("market_cap"),
            "volume_24h_usd": c.get("volume_24h"),
        }
        for c in data
        if c.get("market_cap_change_24h") is not None and (c.get("market_cap") or 0) >= min_market_cap
    ]
    return sorted(rows, key=lambda r: r["change_24h_pct"], reverse=True)[:limit]


def sentiment() -> dict:
    data = _get(FEAR_GREED, params={"limit": 1})
    row = (data.get("data") or [{}])[0]
    return {
        "value": int(row.get("value", 0)),
        "label": row.get("value_classification"),
        "timestamp": row.get("timestamp"),
    }
