from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re
import threading
import time
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import requests

from backend.data import network_people, portfolio

IST = ZoneInfo("Asia/Kolkata")
NSE_ANNOUNCEMENTS_URL = "https://www.nseindia.com/api/corporate-announcements"
NSE_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nseindia.com/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
    ),
}

_CACHE_TTL_SECONDS = 300
_cache: Dict[Tuple[str, str], Tuple[float, List[Dict[str, Any]]]] = {}
_cache_lock = threading.Lock()


class ExchangeSourceError(Exception):
    pass


def classify_announcement(text: str) -> str:
    value = text.casefold()
    rules = [
        ("results", r"\b(financial results|quarterly results|audited results|unaudited results)\b"),
        ("management_change", r"\b(appoint(?:ment|ed)?|resign(?:ation|ed)?|retir(?:ement|ed)|ceo|cfo|managing director|whole[- ]time director)\b"),
        ("M&A", r"\b(acquisition|acquire|merger|amalgamation|demerger|joint venture|stake sale)\b"),
        ("fund_raise", r"\b(qip|qualified institutional placement|rights issue|preferential allotment|commercial paper|buyback|buy-back)\b"),
        ("litigation", r"\b(litigation|court|tribunal|penalty|fine|show cause|regulatory order|orders? passed|action(?:\(s\))? taken|insolvency)\b"),
        ("insider_trading", r"\b(pit disclosure|sast|insider trading|promoter.*(buy|sell)|acquisition of shares|disposal of shares)\b"),
        ("earnings_call", r"\b(earnings call|conference call|concall|transcript|audio recording)\b"),
        ("investor_meetings", r"\b(institutional investors?['’]?\s+meeting|investor meet|investor meeting|analyst meet|investor conference)\b"),
        ("credit_rating", r"\b(credit rating|rating rationale|rating upgrade|rating downgrade)\b"),
        ("dividend", r"\b(dividend)\b"),
        ("bonus_split", r"\b(bonus issue|stock split|sub-division of shares)\b"),
        ("capex", r"\b(capex|capital expenditure|capacity expansion|new plant)\b"),
        ("agm_egm", r"\b(annual general meeting|extraordinary general meeting|agm|egm)\b"),
        ("postal_ballot", r"\b(postal ballot|e-voting)\b"),
        ("pledging", r"\b(pledge|pledging|release of encumbrance)\b"),
    ]
    for category, pattern in rules:
        if re.search(pattern, value):
            return category
    if re.search(r"\b(esop|compliance certificate|secretarial audit|shareholding pattern)\b", value):
        return "unclassified"
    return "press_release"


def _nse_attachment_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.hostname not in {
        "nsearchives.nseindia.in",
        "www.nseindia.com",
        "nseindia.com",
    }:
        return None
    return value


def _fetch_rows(from_date: str, to_date: str) -> List[Dict[str, Any]]:
    cache_key = (from_date, to_date)
    now = time.monotonic()
    with _cache_lock:
        cached = _cache.get(cache_key)
        if cached and now - cached[0] < _CACHE_TTL_SECONDS:
            return cached[1]

    try:
        response = requests.get(
            NSE_ANNOUNCEMENTS_URL,
            params={
                "index": "equities",
                "from_date": from_date,
                "to_date": to_date,
            },
            headers=NSE_HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        rows = response.json()
    except requests.RequestException as exc:
        raise ExchangeSourceError(f"NSE announcements request failed: {exc}") from exc
    except ValueError as exc:
        raise ExchangeSourceError("NSE returned invalid JSON for announcements") from exc

    if not isinstance(rows, list):
        raise ExchangeSourceError("NSE returned an unexpected announcements response")

    normalized_rows = [row for row in rows if isinstance(row, dict)]
    with _cache_lock:
        _cache[cache_key] = (now, normalized_rows)
    return normalized_rows


def build_nse_digest(
    window_hours: int = 24,
    now: datetime | None = None,
) -> Dict[str, Any]:
    if window_hours < 1 or window_hours > 720:
        raise ValueError("window_hours must be between 1 and 720")
    current = now or datetime.now(IST)
    if current.tzinfo is None:
        current = current.replace(tzinfo=IST)
    current = current.astimezone(IST)
    start = current - timedelta(hours=window_hours)
    from_date = start.strftime("%d-%m-%Y")
    to_date = current.strftime("%d-%m-%Y")

    symbols = {item["ticker"].removesuffix(".NS"): item for item in portfolio}
    rows = _fetch_rows(from_date, to_date)
    items = []

    for row in rows:
        symbol = str(row.get("symbol") or "").upper()
        portfolio_company = symbols.get(symbol)
        if portfolio_company is None:
            continue

        published_text = str(row.get("sort_date") or row.get("an_dt") or "")
        if not published_text:
            continue
        try:
            published = datetime.strptime(
                published_text,
                "%Y-%m-%d %H:%M:%S" if "-" in published_text[:10] else "%d-%b-%Y %H:%M:%S",
            ).replace(tzinfo=IST)
        except ValueError:
            continue
        age_hours = (current - published).total_seconds() / 3600
        if not 0 <= age_hours <= window_hours:
            continue

        description = " ".join(
            str(row.get(field) or "")
            for field in ("desc", "attchmntText")
        ).replace("\ufffd", "").strip()
        filing_text = str(row.get("attchmntText") or row.get("desc") or "Exchange filing")
        filing_text = re.sub(r"\s+", " ", filing_text.replace("\ufffd", "")).strip()
        category = classify_announcement(description)
        headline_text = filing_text
        headline = headline_text[:150].rstrip()
        if len(headline_text) > 150:
            headline += "…"
        category_impact = {
            "results": "Check the reported numbers against prior periods and management commentary.",
            "management_change": "Assess leadership continuity, role scope, and any relevant network overlap.",
            "M&A": "Assess strategic fit, consideration, execution risk, and impact on capital allocation.",
            "litigation": "Review the original filing for potential financial and operating implications.",
            "capex": "Compare the investment plan with expected returns, funding, and capacity utilisation.",
            "investor_meetings": "Investor-meeting notices are usually routine; check whether the filing reports new or price-sensitive information.",
            "unclassified": "This filing appears routine; open it only if the underlying detail intersects with an active thesis.",
        }
        people = [
            {
                "name": person["name"],
                "role": person["role"],
                "strength": person["strength"],
                "why_helpful": person["why_helpful"],
                "relationship": person["relationship"],
            }
            for person in network_people
            if portfolio_company["ticker"] in person["company_overlap"]
        ]
        priority = {
            "results": 90,
            "M&A": 90,
            "management_change": 85,
            "litigation": 85,
            "capex": 82,
            "fund_raise": 78,
            "credit_rating": 76,
            "investor_meetings": 50,
            "postal_ballot": 45,
            "press_release": 60,
            "unclassified": 25,
        }.get(category, 55)

        items.append({
            "ticker": portfolio_company["ticker"],
            "name": row.get("sm_name") or portfolio_company["name"],
            "category": category,
            "date": published.isoformat(),
            "headline": headline or "Exchange filing",
            "summary": filing_text[:1200],
            "priority": priority,
            "priority_score": priority + max(0, 10 - int(age_hours)),
            "why_it_matters": category_impact.get(
                category,
                "Review the source filing and decide whether it changes the investment case.",
            ),
            "age_hours": round(age_hours, 1),
            "related_people": people,
            "source": "NSE",
            "source_url": _nse_attachment_url(row.get("attchmntFile")),
            "source_id": row.get("seq_id"),
        })

    items.sort(key=lambda item: item["priority_score"], reverse=True)
    return {
        "window_hours": window_hours,
        "data_mode": "nse_live",
        "items": items,
        "summary": f"{len(items)} NSE filings found for portfolio companies in the last {window_hours} hours.",
    }
