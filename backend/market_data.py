from __future__ import annotations

import re
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

import yfinance as yf
from yfinance.exceptions import YFException


class MarketDataError(Exception):
    pass


_CACHE_TTL_SECONDS = 900
_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
_cache_lock = threading.Lock()


def get_market_snapshot(ticker: str) -> Dict[str, Any]:
    if not re.fullmatch(r"[A-Z0-9&-]{1,20}\.(NS|BO)", ticker):
        raise ValueError(f"Invalid ticker format: {ticker}")

    now = time.monotonic()
    with _cache_lock:
        cached = _cache.get(ticker)
        if cached and now - cached[0] < _CACHE_TTL_SECONDS:
            return {**cached[1], "cache": "hit"}

    try:
        history = yf.Ticker(ticker).history(
            period="2mo",
            interval="1d",
            auto_adjust=False,
            actions=False,
        )
    except YFException as exc:
        raise MarketDataError(f"Yahoo Finance request failed for {ticker}: {exc}") from exc

    if history.empty or "Close" not in history or "Volume" not in history:
        raise MarketDataError(f"No end-of-day price and volume history found for {ticker}")

    valid = history.dropna(subset=["Close", "Volume"])
    if valid.empty:
        raise MarketDataError(f"No complete price and volume rows found for {ticker}")

    latest = valid.iloc[-1]
    previous_close = float(valid.iloc[-2]["Close"]) if len(valid) > 1 else None
    close = float(latest["Close"])
    volume = int(latest["Volume"])
    prior_volumes = valid.iloc[:-1]["Volume"].tail(20)
    average_volume = float(prior_volumes.mean()) if not prior_volumes.empty else None

    result = {
        "ticker": ticker,
        "price": close,
        "previous_close": previous_close,
        "change_pct": (
            round((close / previous_close - 1) * 100, 2)
            if previous_close
            else None
        ),
        "volume": volume,
        "average_volume_20d": round(average_volume, 0) if average_volume is not None else None,
        "volume_multiple": (
            round(volume / average_volume, 2)
            if average_volume
            else None
        ),
        "market_date": valid.index[-1].date().isoformat(),
        "source": "Yahoo Finance via yfinance",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "cache": "miss",
    }

    with _cache_lock:
        _cache[ticker] = (now, result)
    return result
