from __future__ import annotations

import unittest
from unittest.mock import patch

import pandas as pd

from backend import market_data
from backend.market_data import MarketDataError, get_market_snapshot


class MarketDataTests(unittest.TestCase):
    def setUp(self) -> None:
        with market_data._cache_lock:
            market_data._cache.clear()

    def test_snapshot_calculates_change_and_volume_multiple(self) -> None:
        history = pd.DataFrame(
            {
                "Close": [100.0, 102.0, 101.0, 110.0],
                "Volume": [1000, 1200, 1100, 3000],
            },
            index=pd.to_datetime(
                ["2026-11-10", "2026-11-11", "2026-11-12", "2026-11-13"]
            ),
        )
        ticker = unittest.mock.Mock()
        ticker.history.return_value = history

        with patch.object(market_data.yf, "Ticker", return_value=ticker):
            snapshot = get_market_snapshot("RELIANCE.NS")

        self.assertEqual(snapshot["price"], 110.0)
        self.assertEqual(snapshot["change_pct"], 8.91)
        self.assertEqual(snapshot["average_volume_20d"], 1100.0)
        self.assertEqual(snapshot["volume_multiple"], 2.73)
        self.assertEqual(snapshot["source"], "Yahoo Finance via yfinance")

    def test_empty_history_fails_explicitly(self) -> None:
        ticker = unittest.mock.Mock()
        ticker.history.return_value = pd.DataFrame()

        with patch.object(market_data.yf, "Ticker", return_value=ticker):
            with self.assertRaises(MarketDataError):
                get_market_snapshot("RELIANCE.NS")

    def test_invalid_ticker_is_rejected_before_provider_call(self) -> None:
        with patch.object(market_data.yf, "Ticker") as provider:
            with self.assertRaises(ValueError):
                get_market_snapshot("not a ticker")
        provider.assert_not_called()


if __name__ == "__main__":
    unittest.main()
