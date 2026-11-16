from __future__ import annotations

from datetime import datetime, timezone
from contextlib import contextmanager
from hashlib import sha256
from io import BytesIO
import os
from pathlib import Path
import re
import sqlite3
import threading
from typing import Any, Dict, Iterator, List
from urllib.parse import urlparse
from uuid import uuid4

from pypdf import PdfReader
from pypdf.errors import FileNotDecryptedError, PdfReadError

DOC_TYPES = {
    "annual_report",
    "quarterly_results",
    "earnings_call_transcript",
    "investor_presentation",
}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_PDF_PAGES = 2000
MAX_EXTRACTED_CHARACTERS = 25_000_000
_store_lock = threading.Lock()

_data_root = Path(os.environ.get("FINN_DATA_DIR", Path.home() / "AppData" / "Local" / "FINN"))
DATABASE_PATH = _data_root / "primary_sources.sqlite3"


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS source_documents (
            id TEXT PRIMARY KEY,
            ticker TEXT NOT NULL,
            doc_type TEXT NOT NULL,
            title TEXT NOT NULL,
            source_url TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            page_count INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS source_documents_ticker_idx
            ON source_documents (ticker, uploaded_at);
        CREATE TABLE IF NOT EXISTS source_pages (
            source_id TEXT NOT NULL REFERENCES source_documents(id) ON DELETE CASCADE,
            page_number INTEGER NOT NULL,
            page_text TEXT NOT NULL,
            PRIMARY KEY (source_id, page_number)
        );
        """
    )
    try:
        yield connection
    except sqlite3.Error:
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        connection.close()


def _validate_ticker(ticker: str) -> str:
    normalized = ticker.upper()
    if not re.fullmatch(r"[A-Z0-9&-]{1,20}\.(NS|BO)", normalized):
        raise ValueError(f"Invalid ticker format: {ticker}")
    return normalized


def _validate_source_url(source_url: str) -> str:
    parsed = urlparse(source_url.strip())
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Source citation must be a valid HTTPS URL")
    return source_url.strip()


def add_pdf_source(
    ticker: str,
    doc_type: str,
    title: str,
    source_url: str,
    payload: bytes,
) -> Dict[str, Any]:
    ticker = _validate_ticker(ticker)
    if doc_type not in DOC_TYPES:
        raise ValueError(f"doc_type must be one of: {', '.join(sorted(DOC_TYPES))}")
    title = title.strip()
    if not title or len(title) > 250:
        raise ValueError("title must contain 1-250 characters")
    source_url = _validate_source_url(source_url)
    if not payload or len(payload) > MAX_UPLOAD_BYTES:
        raise ValueError("PDF must be non-empty and no larger than 25 MB")
    if not payload.startswith(b"%PDF-"):
        raise ValueError("Uploaded file is not a PDF")

    try:
        reader = PdfReader(BytesIO(payload), strict=False)
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported; upload an accessible PDF")
        if not 1 <= len(reader.pages) <= MAX_PDF_PAGES:
            raise ValueError(f"PDF must contain between 1 and {MAX_PDF_PAGES} pages")
        pages = [page.extract_text() or "" for page in reader.pages]
    except (PdfReadError, FileNotDecryptedError) as exc:
        raise ValueError(f"Unable to read PDF: {exc}") from exc

    extracted_size = sum(len(page) for page in pages)
    if extracted_size > MAX_EXTRACTED_CHARACTERS:
        raise ValueError("Extracted PDF text exceeds the supported size")
    if not any(page.strip() for page in pages):
        raise ValueError("PDF contains no extractable text; OCR is not supported")

    source_id = str(uuid4())
    uploaded_at = datetime.now(timezone.utc).isoformat()
    document = {
        "id": source_id,
        "ticker": ticker,
        "doc_type": doc_type,
        "title": title,
        "source_url": source_url,
        "uploaded_at": uploaded_at,
        "sha256": sha256(payload).hexdigest(),
        "page_count": len(pages),
    }

    with _store_lock, _connect() as connection:
        connection.execute(
            """INSERT INTO source_documents
               (id, ticker, doc_type, title, source_url, uploaded_at, sha256, page_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            tuple(document.values()),
        )
        connection.executemany(
            "INSERT INTO source_pages (source_id, page_number, page_text) VALUES (?, ?, ?)",
            [(source_id, page_number, text) for page_number, text in enumerate(pages, 1)],
        )
    return document


def list_sources(ticker: str) -> List[Dict[str, Any]]:
    ticker = _validate_ticker(ticker)
    with _store_lock, _connect() as connection:
        rows = connection.execute(
            """SELECT id, ticker, doc_type, title, source_url, uploaded_at, sha256, page_count
               FROM source_documents WHERE ticker = ? ORDER BY uploaded_at DESC""",
            (ticker,),
        ).fetchall()
    return [dict(row) for row in rows]


def search_source_evidence(
    ticker: str,
    query: str,
    limit: int = 8,
) -> List[Dict[str, Any]]:
    ticker = _validate_ticker(ticker)
    if not query.strip() or len(query) > 500:
        raise ValueError("query must contain 1-500 characters")
    terms = list(dict.fromkeys(re.findall(r"[\w-]{3,}", query.casefold())))
    if not terms:
        raise ValueError("Search query must contain at least one word of 3 or more characters")
    if limit < 1 or limit > 20:
        raise ValueError("limit must be between 1 and 20")

    with _store_lock, _connect() as connection:
        rows = connection.execute(
            """SELECT d.id, d.doc_type, d.title, d.source_url, p.page_number, p.page_text
               FROM source_documents d
               JOIN source_pages p ON p.source_id = d.id
               WHERE d.ticker = ?""",
            (ticker,),
        ).fetchall()

    matches = []
    for row in rows:
        text = row["page_text"]
        normalized = text.casefold()
        score = sum(normalized.count(term) for term in terms)
        if score == 0:
            continue
        first_position = min(
            (normalized.find(term) for term in terms if normalized.find(term) >= 0),
            default=0,
        )
        start = max(0, first_position - 220)
        end = min(len(text), first_position + 380)
        excerpt = re.sub(r"\s+", " ", text[start:end]).strip()
        matches.append({
            "document_id": row["id"],
            "doc_type": row["doc_type"],
            "title": row["title"],
            "source_url": row["source_url"],
            "page": row["page_number"],
            "excerpt": excerpt,
            "score": score,
        })

    matches.sort(key=lambda result: result["score"], reverse=True)
    return matches[:limit]


def extract_latest_quarterly_results(ticker: str) -> Dict[str, Any] | None:
    ticker = _validate_ticker(ticker)
    with _store_lock, _connect() as connection:
        document = connection.execute(
            """SELECT id, title, source_url
               FROM source_documents
               WHERE ticker = ? AND doc_type = 'quarterly_results'
               ORDER BY uploaded_at DESC
               LIMIT 1""",
            (ticker,),
        ).fetchone()
        if document is None:
            return None
        pages = connection.execute(
            """SELECT page_number, page_text FROM source_pages
               WHERE source_id = ? ORDER BY page_number""",
            (document["id"],),
        ).fetchall()

    for page in pages:
        lines = [re.sub(r"\s+", " ", line).strip() for line in page["page_text"].splitlines()]
        metrics = {}
        for metric, matcher in (
            ("Revenue", lambda line: "revenue from operations" in line),
            (
                "EBITDA",
                lambda line: "total segment profit before interest, tax and" in line,
            ),
            ("PBT", lambda line: line.startswith("profit before tax")),
            (
                "PAT",
                lambda line: line.startswith("profit after tax")
                and "share of profit" not in line
                and "associates" not in line,
            ),
        ):
            for line in lines:
                if not matcher(line.casefold()):
                    continue
                values = re.findall(r"(?<![A-Za-z])\(?-?\d[\d,]*(?:\.\d+)?\)?", line)
                if len(values) < 3:
                    break
                metrics[metric] = [
                    _parse_reported_number(value)
                    for value in values[:3]
                ]
                break

        if len(metrics) != 4:
            continue

        comparisons = {}
        for metric, (current, previous_quarter, year_ago_quarter) in metrics.items():
            if previous_quarter == 0 or year_ago_quarter == 0:
                break
            comparisons[metric] = {
                "current": current,
                "previous_quarter": previous_quarter,
                "year_ago_quarter": year_ago_quarter,
                "qoq_pct": round((current / previous_quarter - 1) * 100, 1),
                "yoy_pct": round((current / year_ago_quarter - 1) * 100, 1),
            }
        if len(comparisons) != 4:
            continue

        return {
            "ticker": ticker,
            "available": True,
            "data_mode": "exchange_filing",
            "period": document["title"],
            "unit": "₹ crore",
            "metrics": comparisons,
            "source": {
                "title": document["title"],
                "source_url": document["source_url"],
                "page": page["page_number"],
            },
            "notice": (
                "Reported values from the uploaded exchange filing. EBITDA is total "
                "segment EBITDA; QoQ and YoY percentages are calculated from the "
                "filing's adjacent quarter columns."
            ),
        }

    return {
        "ticker": ticker,
        "available": False,
        "data_mode": "exchange_filing",
        "reason": (
            "The latest quarterly-results PDF does not contain a supported "
            "consolidated comparison table with Revenue, segment EBITDA, PBT, "
            "and PAT on one page."
        ),
    }


def _parse_reported_number(value: str) -> float:
    normalized = value.replace(",", "")
    if normalized.startswith("(") and normalized.endswith(")"):
        normalized = f"-{normalized[1:-1]}"
    number = float(normalized)
    return int(number) if number.is_integer() else number


def delete_source(ticker: str, source_id: str) -> bool:
    ticker = _validate_ticker(ticker)
    with _store_lock, _connect() as connection:
        cursor = connection.execute(
            "DELETE FROM source_documents WHERE id = ? AND ticker = ?",
            (source_id, ticker),
        )
    return cursor.rowcount > 0
