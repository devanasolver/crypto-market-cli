# Changelog

## Unreleased

- Repo hygiene: removed the accidentally committed `.venv/` virtualenv plus `*.egg-info` and `__pycache__` build artifacts, and added a `.gitignore` (`.venv`, `__pycache__`, `*.egg-info`, `dist`, `.env`, `client_secrets.json`, `token*.json`). Git history was squashed so the virtualenv is gone from history too.

## 0.1.0 — 2026-10-17

First release.
- `cryptomarket top|movers|narratives|sentiment` over free public APIs (CoinGecko, alternative.me). No API key.
- Narratives filtered by minimum market cap (default $100M) to skip noise.
- `--json` on list commands. 4 offline tests.
