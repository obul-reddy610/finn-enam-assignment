from __future__ import annotations

import unittest
from datetime import datetime

from backend.data import portfolio
from backend.market_data import MarketDataError
from backend.services import (
    build_alerts,
    build_company_report,
    build_live_alerts,
    build_push_digest,
)


class ServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime.fromisoformat("2026-11-16T19:00:00+05:30")

    def test_digest_defaults_to_last_24_hours_and_excludes_older_events(self) -> None:
        digest = build_push_digest(now=self.now)

        self.assertEqual(digest["window_hours"], 24)
        self.assertEqual(digest["data_mode"], "synthetic_demo")
        self.assertEqual(len(digest["items"]), 4)
        self.assertTrue(all(item["age_hours"] <= 24 for item in digest["items"]))

    def test_digest_adds_qoq_and_yoy_comparison_for_results(self) -> None:
        digest = build_push_digest(window_hours=24, now=self.now)
        results = next(item for item in digest["items"] if item["category"] == "results")
        revenue = results["results_comparison"]["metrics"]["Revenue"]

        self.assertEqual(revenue["qoq_pct"], 1.6)
        self.assertEqual(revenue["yoy_pct"], 10.2)
        self.assertIn("Illustrative", results["results_comparison"]["notice"])

    def test_alert_thresholds_are_applied_to_sample_data(self) -> None:
        alerts = build_alerts(price_change_pct=5, volume_multiple=2)

        self.assertEqual(alerts["data_mode"], "synthetic_demo")
        self.assertEqual(
            {item["ticker"] for item in alerts["items"]},
            {"INFY.NS", "M&M.NS", "ULTRACEMCO.NS"},
        )

    def test_live_alerts_use_quotes_and_report_failed_symbols(self) -> None:
        def fake_snapshot(ticker: str) -> dict:
            if ticker == "RELIANCE.NS":
                raise MarketDataError("provider unavailable")
            return {
                "change_pct": 6.0,
                "volume_multiple": 2.5,
                "market_date": "2026-11-13",
            }

        with unittest.mock.patch(
            "backend.services.get_market_snapshot",
            side_effect=fake_snapshot,
        ):
            alerts = build_live_alerts(price_change_pct=5, volume_multiple=2)

        self.assertEqual(alerts["data_mode"], "yahoo_finance_eod")
        self.assertEqual(len(alerts["errors"]), 1)
        self.assertEqual(alerts["errors"][0]["ticker"], "RELIANCE.NS")
        self.assertEqual(len(alerts["items"]), len(portfolio) - 1)

    def test_every_portfolio_ticker_has_a_safe_pull_response(self) -> None:
        for item in portfolio:
            with self.subTest(ticker=item["ticker"]):
                report = build_company_report(item["ticker"])
                self.assertEqual(report["ticker"], item["ticker"])
                self.assertIn("report_status", report)
                self.assertIn("primary_source_links", report)

    def test_unknown_valid_ticker_is_not_filled_with_invented_financials(self) -> None:
        report = build_company_report("XYZ.NS")

        self.assertEqual(report["report_status"], "primary_sources_not_loaded")
        self.assertEqual(report["financial_snapshot"], {})
        self.assertIn("No verified", report["source_note"])

    def test_invalid_ticker_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_company_report("not a ticker")

    def test_invalid_alert_threshold_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_alerts(price_change_pct=0)


if __name__ == "__main__":
    unittest.main()
