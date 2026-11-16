# FINN — Financial Investment Agent

FINN is a mobile-first prototype for the ENAM Founding AI Engineer Build Challenge. It demonstrates three connected workflows: Push, Pull, and Network.

## What works

- **Push digest:** choose a 24-hour, 3-day, 7-day, or 30-day window; fetches official NSE corporate announcements for portfolio tickers, ranks them with deterministic category rules, links original filing PDFs, and surfaces relevant synthetic network profiles. The UI also retains a clearly labelled demo feed.
- **Threshold alerts:** change daily price-move and volume-multiple thresholds and evaluate them against demo fixtures or request a live, on-demand EOD check across the portfolio. Failed ticker requests are reported rather than silently treated as clear.
- **Results comparison:** Pull can parse Revenue, segment EBITDA, PBT, and PAT from a supported consolidated quarterly-results table, calculate QoQ/YoY percentages, and cite the filing page. Unsupported table layouts are reported rather than guessed. The separate demo-feed example remains illustrative.
- **Pull research:** portfolio and ad-hoc NSE/BSE tickers have a research response. Upload annual reports, quarterly result filings, earnings-call transcripts, and investor presentations as PDFs with their source URLs; FINN extracts page text and returns page-cited search passages. The Reliance seed includes an official annual report, BSE-hosted concall transcript, and NSE quarterly-results filing. For tickers without ingested sources, it deliberately withholds unsupported financial claims.
- **Live EOD market lookup:** on a company research view, the user can request Yahoo Finance price and volume history for an `.NS` or `.BO` ticker. The adapter reports the market date and source and caches results for 15 minutes.
- **Network:** synthetic people are matched to events and companies. No real professional profiles or personal contacts are included.

## Important data limitations

Portfolio card prices, the demo-feed quarterly results, detailed company research profiles, and network relationships are synthetic fixtures. They are explicitly labelled in the UI and API. The Reliance Pull results comparison is parsed from its NSE filing; the shown EBITDA is the filing's total segment EBITDA. Live providers are official NSE announcements and on-demand Yahoo Finance EOD market data. The opt-in seed command downloads three public Reliance primary-source PDFs and stores extracted text and metadata locally; other documents must be uploaded by the user.

The prototype does not automatically ingest BSE announcements or crawl for documents, and it does not calculate a full investment analysis from PDFs. The quarterly-results parser supports a narrow consolidated table layout and returns no figures when that layout is not recognized. The source library provides cited evidence retrieval, not a fully source-grounded investment thesis.

## Architecture

- `backend/main.py`: FastAPI routes and static frontend serving.
- `backend/data.py`: isolated synthetic portfolio, filing, company, results, and network fixtures.
- `backend/exchange_data.py`: on-demand NSE announcements API client, deterministic classification, portfolio filtering, five-minute cache, and source-link validation.
- `backend/services.py`: digest filtering/ranking, threshold evaluation, Pull response construction, and network matching.
- `backend/market_data.py`: on-demand Yahoo Finance EOD adapter with validation and a 15-minute in-process cache.
- `backend/source_store.py`: bounded PDF text extraction, private local SQLite storage/search, page citations, deletion, and supported quarterly-results parsing.
- `scripts/ingest_demo_sources.py`: opt-in ingestion of the Reliance annual report, concall transcript, and NSE quarterly-results filing; stores extracted text locally and does not retain PDF binaries.
- `static/`: responsive HTML, CSS, and JavaScript frontend.
- `tests/`: focused service, API, and market-adapter tests.

## Data flow and privacy

The prototype runs locally. The browser requests data from FastAPI; NSE and Yahoo Finance are contacted for Push or explicit market requests. Uploaded PDF text/metadata is stored in SQLite under `%LOCALAPPDATA%\\FINN` (override with `FINN_DATA_DIR`) rather than in the repository, and users can delete documents. No uploaded PDF binary is retained. There is no account system, tenant isolation, consent workflow, or production access-control implementation. Do not use this prototype with confidential data.

There is no LLM or autonomous agent in the current implementation. Push ranking and network matching are deterministic rules so their behavior is inspectable and costs are zero. A production version would require authenticated, tenant-isolated storage, encryption, consent and deletion workflows, source citations, provider terms review, monitoring, and a documented model/data-retention policy.

## Run locally on Windows

```powershell
cd C:\Users\obulr\Desktop\Enam_holdings_assignment
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/`. Stop the local server with `Ctrl+C` when finished.

To populate the cited Reliance sources (requires internet access), run this once from the project root:

```powershell
python -m scripts.ingest_demo_sources
```

The command skips already indexed source links and duplicate PDF hashes. It downloads sources from Reliance's investor site and NSE/BSE document endpoints, extracts text into the local SQLite store, and does not save the PDF files.

## Container deployment

```powershell
docker build -t finn .
docker run --rm -p 8000:8000 -v finn-data:/app/data finn
```

The named volume keeps uploaded source-document text between container restarts. Configure a persistent volume at `/app/data` on a hosting provider if the source library must survive redeployments.

## Validation

```powershell
python -m unittest discover -s tests -v
python -m compileall backend tests
node --check static\app.js
```

API routes:

- `GET /health`
- `GET /api/overview`
- `GET /api/push?window_hours=24`
- `GET /api/push?window_hours=24&source=demo`
- `GET /api/alerts?price_change_pct=5&volume_multiple=2`
- `GET /api/alerts/live?price_change_pct=5&volume_multiple=2`
- `GET /api/company/RELIANCE.NS`
- `GET /api/research/RELIANCE.NS/results`
- `GET /api/market/RELIANCE.NS`
- `GET /api/network`
- `POST /api/research/RELIANCE.NS/sources` (multipart PDF, document type, title, source URL)
- `GET /api/research/RELIANCE.NS/sources`
- `GET /api/research/RELIANCE.NS/evidence?query=revenue%20guidance`
- `DELETE /api/research/RELIANCE.NS/sources/{source_id}`

## Submission checklist

- Create and publish a public GitHub repository; this folder is not connected to a remote repository.
- Deploy the responsive app using the included Dockerfile or provide a phone-friendly way to run it.
- Include the actual AI build-history share/export links requested by ENAM; [AI_BUILD_HISTORY.md](./AI_BUILD_HISTORY.md) is only a handoff summary, not those records.
- Upload and verify primary-source PDFs for the demo companies before describing company analysis as source-grounded.
- Review and personalize `COVERING_NOTE.md` before emailing the submission.
