from __future__ import annotations

from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from typing import Any, Dict, List, Optional

from backend.data import announcements, companies, network_people, portfolio, research_watchlist
from backend.market_data import MarketDataError, get_market_snapshot

DEMO_VOLUME_MULTIPLES = {
    "RELIANCE.NS": 1.1,
    "TCS.NS": 1.2,
    "HDFCBANK.NS": 0.9,
    "ICICIBANK.NS": 1.0,
    "INFY.NS": 2.4,
    "ITC.NS": 0.8,
    "SBI.NS": 1.1,
    "M&M.NS": 2.2,
    "MARUTI.NS": 1.3,
    "SUNPHARMA.NS": 1.0,
    "CIPLA.NS": 1.6,
    "BHARTIARTL.NS": 1.2,
    "LTIM.NS": 1.1,
    "ULTRACEMCO.NS": 2.1,
    "TITAN.NS": 1.0,
    "NTPC.NS": 1.4,
    "APOLLOHOSP.NS": 0.9,
}


def build_overview() -> Dict[str, Any]:
    push = build_push_digest(24)
    return {
        "portfolio_count": len(portfolio),
        "watchlist_count": len(research_watchlist),
        "network_size": len(network_people),
        "portfolio": portfolio,
        "data_notice": "Portfolio card figures, illustrative research profiles, and network profiles are demo fixtures. Push can load official NSE filings; live Yahoo EOD quotes are fetched on demand. Not investment advice.",
        "watchlist": [
            {"ticker": ticker, "name": companies.get(ticker, {}).get("name", ticker), "sector": companies.get(ticker, {}).get("sector", "")}
            for ticker in research_watchlist
        ],
        "network_summary": {
            "people": [person["name"] for person in network_people],
            "strongest_match": max(network_people, key=lambda p: p["strength"])["name"]
        },
        "push_preview": push["items"][:3],
        "signal": "Need to surface only the few things that matter and put the network in the right moment."
    }


def build_push_digest(
    window_hours: int = 24,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    if window_hours < 1 or window_hours > 720:
        raise ValueError("window_hours must be between 1 and 720")

    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    filtered: List[Dict[str, Any]] = []

    for item in announcements:
        published_at = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
        age = now - published_at
        age_hours = age.total_seconds() / 3600
        if 0 <= age_hours <= window_hours:
            score = item["priority"] + max(0, 10 - int(age_hours))
            enriched = {
                **item,
                "age_hours": round(age_hours, 1),
                "priority_score": score,
                "related_people": find_relevant_people(item["ticker"]),
            }
            if "illustrative_results" in item:
                enriched["results_comparison"] = _compare_illustrative_results(
                    item["illustrative_results"]
                )
            filtered.append(enriched)

    filtered.sort(key=lambda x: x["priority_score"], reverse=True)
    return {
        "window_hours": window_hours,
        "data_mode": "synthetic_demo",
        "items": filtered,
        "summary": f"{len(filtered)} illustrative updates surfaced across the portfolio in the last {window_hours} hours."
    }


def _compare_illustrative_results(results: Dict[str, Any]) -> Dict[str, Any]:
    metrics = {}
    for metric, values in results["metrics"].items():
        current = values["current"]
        previous_quarter = values["previous_quarter"]
        year_ago_quarter = values["year_ago_quarter"]
        metrics[metric] = {
            **values,
            "qoq_pct": round((current / previous_quarter - 1) * 100, 1),
            "yoy_pct": round((current / year_ago_quarter - 1) * 100, 1),
        }
    return {
        "period": results["period"],
        "unit": results["unit"],
        "metrics": metrics,
        "notice": "Illustrative numbers only; not sourced from a company filing.",
    }


def build_alerts(
    price_change_pct: float = 5.0,
    volume_multiple: float = 2.0,
) -> Dict[str, Any]:
    if price_change_pct <= 0 or volume_multiple <= 0:
        raise ValueError("Alert thresholds must be greater than zero")

    triggered = []
    for item in portfolio:
        change = float(item["change_pct"])
        volume_ratio = DEMO_VOLUME_MULTIPLES.get(item["ticker"], 1.0)
        reasons = []
        if abs(change) >= price_change_pct:
            reasons.append(f"Daily price move {change:+.1f}% exceeds ±{price_change_pct:g}%")
        if volume_ratio >= volume_multiple:
            reasons.append(f"Volume is {volume_ratio:.1f}× the recent average (threshold {volume_multiple:g}×)")
        if reasons:
            triggered.append({
                "ticker": item["ticker"],
                "name": item["name"],
                "price_change_pct": change,
                "volume_multiple": volume_ratio,
                "reasons": reasons,
            })

    return {
        "data_mode": "synthetic_demo",
        "thresholds": {
            "price_change_pct": price_change_pct,
            "volume_multiple": volume_multiple,
        },
        "items": triggered,
        "summary": f"{len(triggered)} illustrative threshold alerts triggered across the portfolio.",
    }


def build_live_alerts(
    price_change_pct: float = 5.0,
    volume_multiple: float = 2.0,
) -> Dict[str, Any]:
    if price_change_pct <= 0 or volume_multiple <= 0:
        raise ValueError("Alert thresholds must be greater than zero")

    triggered = []
    errors = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        requests = {
            executor.submit(get_market_snapshot, item["ticker"]): item
            for item in portfolio
        }
        for request in as_completed(requests):
            item = requests[request]
            try:
                market = request.result()
            except MarketDataError as exc:
                errors.append({"ticker": item["ticker"], "error": str(exc)})
                continue

            change = market["change_pct"]
            volume_ratio = market["volume_multiple"]
            reasons = []
            if change is not None and abs(change) >= price_change_pct:
                reasons.append(f"Daily price move {change:+.2f}% exceeds ±{price_change_pct:g}%")
            if volume_ratio is not None and volume_ratio >= volume_multiple:
                reasons.append(f"Volume is {volume_ratio:.2f}× the recent average (threshold {volume_multiple:g}×)")
            if reasons:
                triggered.append({
                    "ticker": item["ticker"],
                    "name": item["name"],
                    "price_change_pct": change,
                    "volume_multiple": volume_ratio,
                    "reasons": reasons,
                    "market_date": market["market_date"],
                })

    return {
        "data_mode": "yahoo_finance_eod",
        "thresholds": {
            "price_change_pct": price_change_pct,
            "volume_multiple": volume_multiple,
        },
        "items": sorted(triggered, key=lambda item: item["ticker"]),
        "errors": errors,
        "summary": (
            f"{len(triggered)} live threshold alerts triggered; "
            f"{len(errors)} portfolio quote(s) could not be checked."
        ),
    }


def find_relevant_people(ticker: str) -> List[Dict[str, Any]]:
    matches = []
    for person in network_people:
        if ticker in person["company_overlap"]:
            matches.append({
                "name": person["name"],
                "role": person["role"],
                "strength": person["strength"],
                "why_helpful": person["why_helpful"],
                "relationship": person["relationship"],
            })
    return matches


def build_company_report(ticker: str) -> Dict[str, Any]:
    if not re.fullmatch(r"[A-Z0-9&-]{1,20}\.(NS|BO)", ticker):
        raise ValueError(f"Invalid ticker format: {ticker}")

    portfolio_company = next(
        (item for item in portfolio if item["ticker"] == ticker),
        None,
    )

    company = companies.get(ticker)

    overlap = [person for person in network_people if ticker in person["company_overlap"]]
    if company is None:
        company_name = portfolio_company["name"] if portfolio_company else ticker.rsplit(".", 1)[0]
        company_sector = portfolio_company["sector"] if portfolio_company else "Not classified"
        return {
            "ticker": ticker,
            "company": {
                "name": company_name,
                "sector": company_sector,
            },
            "report_status": "primary_sources_not_loaded",
            "data_mode": "synthetic_demo",
            "source_note": "No verified annual report or earnings-call transcript has been ingested for this company. FINN does not generate financial claims without those sources.",
            "primary_source_links": [
                {
                    "label": "Screener company page",
                    "url": f"https://www.screener.in/company/{ticker.rsplit('.', 1)[0]}/",
                },
                {
                    "label": "NSE corporate filings",
                    "url": "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
                },
            ],
            "financial_snapshot": {},
            "guidance": [],
            "network": [
                {
                    "name": person["name"],
                    "role": person["role"],
                    "strength": person["strength"],
                    "why_helpful": person["why_helpful"],
                }
                for person in overlap
            ],
        }

    return {
        "ticker": ticker,
        "company": {
            "name": company["name"],
            "sector": company["sector"],
        },
        "report_status": "illustrative_demo_only",
        "data_mode": "synthetic_demo",
        "source_note": "The following company analysis is illustrative demo content, not extracted from company filings or transcripts.",
        "primary_source_links": [
            {
                "label": "Screener company page",
                "url": f"https://www.screener.in/company/{ticker.removesuffix('.NS')}/",
            }
        ],
        "business_snapshot": company["business_snapshot"],
        "financial_snapshot": company["financial_snapshot"],
        "trajectory": company["trajectory"],
        "balance_sheet": company["balance_sheet"],
        "cash_quality": company["cash_quality"],
        "narrative_vs_numbers": company["narrative_vs_numbers"],
        "guidance": company["guidance"],
        "bull_case": company["bull_case"],
        "bear_case": company["bear_case"],
        "network": [
            {
                "name": person["name"],
                "role": person["role"],
                "strength": person["strength"],
                "why_helpful": person["why_helpful"],
            }
            for person in overlap
        ],
        "decision_note": f"The investment case is strongest when {company['name']} can convert strategy into repeatable operating leverage without over-investing in capacity or execution risk."
    }


def build_network_matches(company_ticker: Optional[str] = None) -> Dict[str, Any]:
    people = network_people
    if company_ticker:
        people = [person for person in people if company_ticker in person["company_overlap"]]

    if not people:
        return {"people": [], "strategy": "No direct network overlap yet. This is a good signal to broaden the map by sector or former employer."}

    return {
        "data_mode": "synthetic_demo",
        "people": [
            {
                "name": person["name"],
                "role": person["role"],
                "relationship": person["relationship"],
                "company_overlap": person["company_overlap"],
                "why_helpful": person["why_helpful"],
                "strength": person["strength"],
            }
            for person in people
        ],
        "strategy": "The network is most valuable when it connects event context to a real person who has lived the operating detail."
    }
