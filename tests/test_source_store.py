from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from backend import source_store
from backend.source_store import (
    add_pdf_source,
    delete_source,
    extract_latest_quarterly_results,
    list_sources,
    search_source_evidence,
)


class SourceStoreTests(unittest.TestCase):
    def test_pdf_source_is_stored_searchable_cited_and_deletable(self) -> None:
        page = Mock()
        page.extract_text.return_value = (
            "Management expects revenue growth to improve. EBITDA margin guidance "
            "is stable, while cash flow conversion remains a priority."
        )
        reader = Mock()
        reader.is_encrypted = False
        reader.pages = [page]

        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "sources.sqlite3"
            with patch.object(source_store, "DATABASE_PATH", database):
                with patch("backend.source_store.PdfReader", return_value=reader):
                    document = add_pdf_source(
                        "TCS.NS",
                        "earnings_call_transcript",
                        "Q2 earnings call transcript",
                        "https://www.example.com/investors/q2-call.pdf",
                        b"%PDF-1.7 synthetic test bytes",
                    )

                self.assertEqual(len(list_sources("TCS.NS")), 1)
                matches = search_source_evidence("TCS.NS", "revenue EBITDA margin")
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0]["document_id"], document["id"])
                self.assertEqual(matches[0]["page"], 1)
                self.assertIn("revenue growth", matches[0]["excerpt"])
                self.assertTrue(delete_source("TCS.NS", document["id"]))
                self.assertEqual(list_sources("TCS.NS"), [])
                self.assertEqual(search_source_evidence("TCS.NS", "revenue"), [])

    def test_source_upload_rejects_non_https_citation_and_non_pdf(self) -> None:
        with self.assertRaises(ValueError):
            add_pdf_source(
                "RELIANCE.NS",
                "annual_report",
                "Annual report",
                "http://example.com/report.pdf",
                b"%PDF-1.7 content",
            )
        with self.assertRaises(ValueError):
            add_pdf_source(
                "RELIANCE.NS",
                "annual_report",
                "Annual report",
                "https://example.com/report.pdf",
                b"not a pdf",
            )

    def test_search_rejects_empty_or_unbounded_queries(self) -> None:
        with self.assertRaises(ValueError):
            search_source_evidence("RELIANCE.NS", "  ")
        with self.assertRaises(ValueError):
            search_source_evidence("RELIANCE.NS", "x" * 501)

    def test_quarterly_results_extract_comparison_metrics_with_page_citation(self) -> None:
        page = Mock()
        page.extract_text.return_value = "\n".join(
            [
                "Quarter Ended 30th Sep '26 30th Jun '26 30th Sep '25",
                "Revenue from Operations 332,861 311,850 258,898",
                "Total Segment Profit before Interest, Tax and 61,224 51,403 48,480",
                "Profit Before Tax 38,613 30,630 29,124",
                "Profit After Tax 29,250 23,001 22,146",
            ]
        )
        reader = Mock()
        reader.is_encrypted = False
        reader.pages = [page]

        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "sources.sqlite3"
            with patch.object(source_store, "DATABASE_PATH", database):
                with patch("backend.source_store.PdfReader", return_value=reader):
                    add_pdf_source(
                        "RELIANCE.NS",
                        "quarterly_results",
                        "Quarter ended 30 September 2026",
                        "https://www.example.com/results.pdf",
                        b"%PDF-1.7 synthetic test bytes",
                    )

                results = extract_latest_quarterly_results("RELIANCE.NS")

        self.assertIsNotNone(results)
        assert results is not None
        self.assertTrue(results["available"])
        self.assertEqual(results["source"]["page"], 1)
        self.assertEqual(results["metrics"]["Revenue"]["current"], 332861)
        self.assertEqual(results["metrics"]["Revenue"]["qoq_pct"], 6.7)
        self.assertEqual(results["metrics"]["Revenue"]["yoy_pct"], 28.6)
        self.assertEqual(results["metrics"]["EBITDA"]["current"], 61224)
        self.assertEqual(results["metrics"]["PAT"]["current"], 29250)


if __name__ == "__main__":
    unittest.main()
