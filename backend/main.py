from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.exchange_data import ExchangeSourceError, build_nse_digest
from backend.market_data import MarketDataError, get_market_snapshot
from backend.services import (
    build_alerts,
    build_company_report,
    build_live_alerts,
    build_network_matches,
    build_overview,
    build_push_digest,
)
from backend.source_store import (
    MAX_UPLOAD_BYTES,
    add_pdf_source,
    delete_source,
    extract_latest_quarterly_results,
    list_sources,
    search_source_evidence,
)

BASE_DIR = Path(__file__).resolve().parent.parent
ENABLE_SOURCE_WRITES = os.environ.get("FINN_ENABLE_SOURCE_WRITES", "true").strip().lower() not in {
    "0",
    "false",
    "no",
    "off",
}

app = FastAPI(title="FINN — Financial Investment Agent")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/")
def serve_index() -> FileResponse:
    return FileResponse(str(BASE_DIR / "static" / "index.html"))


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "FINN"}


@app.get("/api/overview")
def get_overview() -> dict:
    return build_overview()


@app.get("/api/push")
def get_push(
    window_hours: int = Query(default=24, ge=1, le=720),
    source: str = Query(default="nse", pattern="^(nse|demo)$"),
) -> dict:
    if source == "demo":
        return build_push_digest(window_hours)
    try:
        return build_nse_digest(window_hours)
    except ExchangeSourceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/alerts")
def get_alerts(
    price_change_pct: float = Query(default=5.0, gt=0, le=100),
    volume_multiple: float = Query(default=2.0, gt=0, le=100),
) -> dict:
    return build_alerts(price_change_pct, volume_multiple)


@app.get("/api/alerts/live")
def get_live_alerts(
    price_change_pct: float = Query(default=5.0, gt=0, le=100),
    volume_multiple: float = Query(default=2.0, gt=0, le=100),
) -> dict:
    return build_live_alerts(price_change_pct, volume_multiple)


@app.get("/api/company/{ticker}")
def get_company(ticker: str) -> dict:
    try:
        return build_company_report(ticker.upper())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/research/{ticker}/sources", status_code=201)
async def upload_primary_source(
    ticker: str,
    doc_type: str = Form(...),
    title: str = Form(...),
    source_url: str = Form(...),
    file: UploadFile = File(...),
) -> dict:
    if not ENABLE_SOURCE_WRITES:
        raise HTTPException(
            status_code=403,
            detail="Source uploads are disabled on this deployment.",
        )
    payload = await file.read(MAX_UPLOAD_BYTES + 1)
    await file.close()
    try:
        return add_pdf_source(
            ticker.upper(),
            doc_type,
            title,
            source_url,
            payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/research/{ticker}/sources")
def get_primary_sources(ticker: str) -> dict:
    try:
        sources = list_sources(ticker.upper())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "ticker": ticker.upper(),
        "sources": sources,
        "writes_enabled": ENABLE_SOURCE_WRITES,
    }


@app.get("/api/research/{ticker}/evidence")
def get_source_evidence(
    ticker: str,
    query: str = Query(..., min_length=1, max_length=500),
    limit: int = Query(default=8, ge=1, le=20),
) -> dict:
    try:
        matches = search_source_evidence(ticker.upper(), query, limit)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "ticker": ticker.upper(),
        "query": query,
        "data_mode": "uploaded_primary_documents",
        "matches": matches,
    }


@app.get("/api/research/{ticker}/results")
def get_quarterly_results(ticker: str) -> dict:
    try:
        results = extract_latest_quarterly_results(ticker.upper())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return results or {
        "ticker": ticker.upper(),
        "available": False,
        "data_mode": "exchange_filing",
        "reason": "No quarterly-results filing has been added for this ticker.",
    }


@app.delete("/api/research/{ticker}/sources/{source_id}", status_code=204)
def remove_primary_source(ticker: str, source_id: str) -> None:
    if not ENABLE_SOURCE_WRITES:
        raise HTTPException(
            status_code=403,
            detail="Source deletion is disabled on this deployment.",
        )
    try:
        deleted = delete_source(ticker.upper(), source_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Source document not found")


@app.get("/api/market/{ticker}")
def get_market(ticker: str) -> dict:
    try:
        return get_market_snapshot(ticker.upper())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except MarketDataError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/network")
def get_network(company: str | None = None) -> dict:
    return build_network_matches(company)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
