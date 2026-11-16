from __future__ import annotations

from hashlib import sha256

import requests

from backend.source_store import add_pdf_source, list_sources, MAX_UPLOAD_BYTES

DOCUMENTS = [
    {
        "ticker": "RELIANCE.NS",
        "doc_type": "annual_report",
        "title": "Reliance Industries Integrated Annual Report 2025-26",
        "source_url": "https://www.ril.com/reports/RIL-Integrated-Annual-Report-2025-26.pdf",
    },
    {
        "ticker": "RELIANCE.NS",
        "doc_type": "earnings_call_transcript",
        "title": "Reliance Industries Concall Transcript - November 2026",
        "source_url": (
            "https://www.bseindia.com/stockinfo/AnnPdfOpen.aspx?"
            "Pname=8e997741-4d35-4188-933a-cf020fb9c816.pdf"
        ),
    },
    {
        "ticker": "RELIANCE.NS",
        "doc_type": "quarterly_results",
        "title": (
            "Reliance Industries Unaudited Consolidated Results - "
            "Quarter ended 30 September 2026"
        ),
        "source_url": (
            "https://nsearchives.nseindia.in/corporate/"
            "kavinavora_30102026193935_SE_30102026_Results.pdf"
        ),
    },
]

def main() -> None:
    existing = list_sources("RELIANCE.NS")
    existing_hashes = {source["sha256"] for source in existing}
    existing_sources = {
        (source["title"], source["source_url"])
        for source in existing
    }

    for document in DOCUMENTS:
        source_key = (document["title"], document["source_url"])
        if source_key in existing_sources:
            print(f"Already present: {document['title']}")
            continue

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
            )
        }
        if "bseindia.com" in document["source_url"]:
            headers["Referer"] = "https://www.bseindia.com/"
        response = requests.get(
            document["source_url"],
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        payload = response.content
        if len(payload) > MAX_UPLOAD_BYTES:
            raise RuntimeError(f"Source PDF exceeds the 25 MB limit: {document['title']}")
        if not payload.startswith(b"%PDF-"):
            raise RuntimeError(f"Source URL did not return a PDF: {document['source_url']}")

        digest = sha256(payload).hexdigest()
        if digest in existing_hashes:
            print(f"Already present: {document['title']}")
            existing_sources.add(source_key)
            continue

        stored = add_pdf_source(
            ticker=document["ticker"],
            doc_type=document["doc_type"],
            title=document["title"],
            source_url=document["source_url"],
            payload=payload,
        )
        existing_hashes.add(digest)
        existing_sources.add(source_key)
        print(
            f"Stored {stored['title']}: {stored['page_count']} pages, "
            f"source {stored['source_url']}"
        )


if __name__ == "__main__":
    main()
