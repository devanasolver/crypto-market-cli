"""cryptomarket command line."""

from __future__ import annotations

import argparse
import json
import sys

from . import api


def _money(v):
    if v is None:
        return "-"
    if v >= 1_000_000_000:
        return f"${v/1_000_000_000:.1f}B"
    if v >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    return f"${v:,.0f}"


def _pct(v):
    return "-" if v is None else f"{v:+.1f}%"


def _price(v):
    if v is None:
        return "-"
    return f"${v:,.6f}".rstrip("0").rstrip(".") if v < 1 else f"${v:,.2f}"


def _print_coins(coins):
    for c in coins:
        print(f"  {str(c['rank']):>4} {c['symbol']:<8} {_price(c['price_usd']):>12}  "
              f"24h {_pct(c['change_24h_pct']):>7}  7d {_pct(c['change_7d_pct']):>7}  {_money(c['market_cap_usd']):>9}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="cryptomarket",
                                description="Free crypto market snapshot. No API key.")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("top", help="Top coins by market cap")
    t.add_argument("--limit", type=int, default=25)
    m = sub.add_parser("movers", help="Biggest 24h gainers and losers in the top 250")
    m.add_argument("--limit", type=int, default=10)
    n = sub.add_parser("narratives", help="Which crypto narratives are moving (24h)")
    n.add_argument("--limit", type=int, default=20)
    n.add_argument("--min-cap", type=float, default=100_000_000, help="Minimum narrative market cap in USD")
    sub.add_parser("sentiment", help="Fear & Greed index")
    for sp in (t, m, n):
        sp.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        if args.cmd == "top":
            data = api.top_coins(args.limit)
            if args.json:
                print(json.dumps(data, indent=2))
            else:
                print(f"\nTop {len(data)} coins by market cap:\n")
                _print_coins(data)
        elif args.cmd == "movers":
            data = api.movers(args.limit)
            if args.json:
                print(json.dumps(data, indent=2))
            else:
                print("\nBiggest gainers (24h, top 250):\n")
                _print_coins(data["gainers"])
                print("\nBiggest losers (24h, top 250):\n")
                _print_coins(data["losers"])
        elif args.cmd == "narratives":
            data = api.narratives(args.limit, args.min_cap)
            if args.json:
                print(json.dumps(data, indent=2))
            else:
                print(f"\nTop {len(data)} narratives by 24h market-cap change:\n")
                for r in data:
                    print(f"  {_pct(r['change_24h_pct']):>7}  {r['category']:<35} {_money(r['market_cap_usd']):>9}")
        elif args.cmd == "sentiment":
            data = api.sentiment()
            print(json.dumps(data, indent=2) if getattr(args, "json", False)
                  else f"\nFear & Greed: {data['value']}/100 - {data['label']}\n")
            return
        if not getattr(args, "json", False):
            print("\nDeeper intel (VC funding, narrative tracking): https://coinmarketlab.com")
    except Exception as exc:  # network or API issue: fail with a human message
        print(f"Could not reach the free market data API: {exc}", file=sys.stderr)
        print("The free CoinGecko API rate-limits heavy use. Wait a minute and try again.", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
