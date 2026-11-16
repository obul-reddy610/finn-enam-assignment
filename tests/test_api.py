from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_and_frontend_are_served(self) -> None:
        self.assertEqual(self.client.get("/health").json()["status"], "ok")
        page = self.client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn("FINN", page.text)

    def test_push_defaults_to_24_hours_and_accepts_custom_window(self) -> None:
        nse_digest = {"window_hours": 24, "data_mode": "nse_live", "items": []}
        with patch("backend.main.build_nse_digest", return_value=nse_digest) as runner:
            default = self.client.get("/api/push")
            custom = self.client.get("/api/push?window_hours=72")

        self.assertEqual(default.status_code, 200)
        self.assertEqual(default.json()["data_mode"], "nse_live")
        self.assertEqual(custom.status_code, 200)
        runner.assert_any_call(24)
        runner.assert_any_call(72)
        self.assertEqual(self.client.get("/api/push?window_hours=0").status_code, 422)

    def test_push_can_select_synthetic_fixture_feed(self) -> None:
        response = self.client.get("/api/push?source=demo")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data_mode"], "synthetic_demo")

    def test_alert_thresholds_are_validated(self) -> None:
        response = self.client.get(
            "/api/alerts?price_change_pct=3.5&volume_multiple=1.5"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["thresholds"]["price_change_pct"], 3.5)
        self.assertEqual(self.client.get("/api/alerts?volume_multiple=0").status_code, 422)

    def test_live_alert_endpoint_passes_configurable_thresholds(self) -> None:
        expected = {"data_mode": "yahoo_finance_eod", "items": [], "errors": []}
        with patch("backend.main.build_live_alerts", return_value=expected) as runner:
            response = self.client.get(
                "/api/alerts/live?price_change_pct=4&volume_multiple=1.8"
            )

        self.assertEqual(response.status_code, 200)
        runner.assert_called_once_with(4.0, 1.8)

    def test_company_endpoint_handles_portfolio_and_uningested_tickers(self) -> None:
        known = self.client.get("/api/company/RELIANCE.NS")
        unknown = self.client.get("/api/company/XYZ.NS")

        self.assertEqual(known.status_code, 200)
        self.assertEqual(known.json()["report_status"], "illustrative_demo_only")
        self.assertEqual(unknown.status_code, 200)
        self.assertEqual(unknown.json()["report_status"], "primary_sources_not_loaded")
        self.assertEqual(unknown.json()["financial_snapshot"], {})

    def test_market_endpoint_uses_adapter_and_surfaces_source(self) -> None:
        snapshot = {
            "ticker": "RELIANCE.NS",
            "price": 100.0,
            "source": "Yahoo Finance via yfinance",
        }
        with patch("backend.main.get_market_snapshot", return_value=snapshot) as provider:
            response = self.client.get("/api/market/reliance.ns")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["source"], "Yahoo Finance via yfinance")
        provider.assert_called_once_with("RELIANCE.NS")

    def test_primary_source_pdf_upload_records_citation(self) -> None:
        document = {
            "id": "source-id",
            "ticker": "RELIANCE.NS",
            "doc_type": "annual_report",
            "title": "Annual report",
            "source_url": "https://www.example.com/report.pdf",
            "page_count": 1,
        }
        with patch("backend.main.add_pdf_source", return_value=document) as ingest:
            response = self.client.post(
                "/api/research/reliance.ns/sources",
                data={
                    "doc_type": "annual_report",
                    "title": "Annual report",
                    "source_url": "https://www.example.com/report.pdf",
                },
                files={"file": ("report.pdf", b"%PDF-1.7", "application/pdf")},
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["source_url"], document["source_url"])
        ingest.assert_called_once()

    def test_quarterly_results_endpoint_returns_page_cited_filing_data(self) -> None:
        expected = {
            "ticker": "RELIANCE.NS",
            "available": True,
            "data_mode": "exchange_filing",
            "source": {"source_url": "https://www.example.com/results.pdf", "page": 17},
        }
        with patch("backend.main.extract_latest_quarterly_results", return_value=expected):
            response = self.client.get("/api/research/RELIANCE.NS/results")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data_mode"], "exchange_filing")
        self.assertEqual(response.json()["source"]["page"], 17)

    def test_quarterly_results_endpoint_reports_missing_sources(self) -> None:
        with patch("backend.main.extract_latest_quarterly_results", return_value=None):
            response = self.client.get("/api/research/RELIANCE.NS/results")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["available"])


if __name__ == "__main__":
    unittest.main()
