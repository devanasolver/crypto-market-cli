"""Offline tests: API layer is monkeypatched, no internet needed."""

from crypto_market import api


SAMPLE_COINS = [
    {"market_cap_rank": 1, "name": "Bitcoin", "symbol": "btc", "current_price": 67000.0,
     "price_change_percentage_24h": 2.5, "price_change_percentage_7d_in_currency": 5.0,
     "market_cap": 1_300_000_000_000},
    {"market_cap_rank": 2, "name": "Ethereum", "symbol": "eth", "current_price": 3200.0,
     "price_change_percentage_24h": -1.2, "price_change_percentage_7d_in_currency": 3.0,
     "market_cap": 390_000_000_000},
    {"market_cap_rank": 99, "name": "NoChange", "symbol": "nc", "current_price": 1.0,
     "price_change_percentage_24h": None, "price_change_percentage_7d_in_currency": None,
     "market_cap": 1_000_000},
]


def test_top_coins(monkeypatch):
    monkeypatch.setattr(api, "_get", lambda url, params=None: SAMPLE_COINS)
    coins = api.top_coins(10)
    assert coins[0]["symbol"] == "BTC"
    assert coins[0]["change_24h_pct"] == 2.5
    assert coins[1]["change_7d_pct"] == 3.0


def test_movers_skips_missing_change(monkeypatch):
    monkeypatch.setattr(api, "_get", lambda url, params=None: SAMPLE_COINS)
    m = api.movers(5)
    syms = [c["symbol"] for c in m["gainers"] + m["losers"]]
    assert "NC" not in syms
    assert m["gainers"][0]["symbol"] == "BTC"
    assert m["losers"][0]["symbol"] == "ETH"


def test_narratives_sorted(monkeypatch):
    cats = [
        {"name": "AI", "market_cap_change_24h": 8.0, "market_cap": 1e9, "volume_24h": 1e8},
        {"name": "Meme", "market_cap_change_24h": -3.0, "market_cap": 2e9, "volume_24h": 2e8},
        {"name": "Flat", "market_cap_change_24h": None, "market_cap": 1, "volume_24h": 1},
    ]
    monkeypatch.setattr(api, "_get", lambda url, params=None: cats)
    rows = api.narratives(10)
    assert [r["category"] for r in rows] == ["AI", "Meme"]


def test_sentiment(monkeypatch):
    monkeypatch.setattr(api, "_get", lambda url, params=None: {"data": [{"value": "25", "value_classification": "Extreme Fear", "timestamp": "1"}]})
    s = api.sentiment()
    assert s["value"] == 25 and s["label"] == "Extreme Fear"
