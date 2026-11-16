from __future__ import annotations

import unittest
from datetime import datetime
from unittest.mock import patch

from backend.exchange_data import build_nse_digest, classify_announcement


class ExchangeDataTests(unittest.TestCase):
    def test_classifies_common_exchange_announcements(self) -> None:
        self.assertEqual(classify_announcement("Quarterly financial results"), "results")
        self.assertEqual(classify_announcement("Appointment of Chief Financial Officer"), "management_change")
        self.assertEqual(classify_announcement("Capacity expansion capex plan"), "capex")
        self.assertEqual(classify_announcement("Action(s) taken or orders passed"), "litigation")
        self.assertEqual(classify_announcement("ESOP allotment filing"), "unclassified")

    def test_nse_digest_filters_to_portfolio_and_keeps_source_citation(self) -> None:
        rows = [
            {
                "symbol": "RELIANCE",
                "sm_name": "Reliance Industries Limited",
                "sort_date": "2026-11-16 18:30:00",
                "desc": "Updates",
                "attchmntText": "The company announces an investor meeting.",
                "attchmntFile": "https://nsearchives.nseindia.in/corporate/example.pdf",
                "seq_id": "12345",
            },
            {
                "symbol": "NOTINPORTFOLIO",
                "sort_date": "2026-11-16 18:30:00",
                "desc": "Results",
                "attchmntText": "Financial results",
                "attchmntFile": "https://nsearchives.nseindia.in/corporate/other.pdf",
            },
            {
                "symbol": "TCS",
                "sort_date": "2026-11-15 10:00:00",
                "desc": "Results",
                "attchmntText": "Financial results",
                "attchmntFile": "https://nsearchives.nseindia.in/corporate/old.pdf",
            },
        ]
        now = datetime.fromisoformat("2026-11-16T19:00:00+05:30")

        with patch("backend.exchange_data._fetch_rows", return_value=rows):
            digest = build_nse_digest(window_hours=24, now=now)

        self.assertEqual(digest["data_mode"], "nse_live")
        self.assertEqual(len(digest["items"]), 1)
        filing = digest["items"][0]
        self.assertEqual(filing["ticker"], "RELIANCE.NS")
        self.assertEqual(filing["category"], "investor_meetings")
        self.assertEqual(filing["source"], "NSE")
        self.assertEqual(filing["source_id"], "12345")
        self.assertTrue(filing["source_url"].endswith("example.pdf"))


if __name__ == "__main__":
    unittest.main()
