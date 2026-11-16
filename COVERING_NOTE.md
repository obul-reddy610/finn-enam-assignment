# Covering note draft

**To:** assessment@enam.com  
**Subject:** IIT Kanpur – Founding AI Engineer - 2027

Dear ENAM team,

I built FINN, a mobile-first prototype exploring how an investor can move between a prioritised event digest, company research, and relevant people in their network.

The prototype includes a selectable Push time window, live NSE corporate announcements for portfolio tickers with original filing links, configurable price/volume threshold evaluation, and on-demand Yahoo Finance EOD quotes. In Pull, users can add annual-report, quarterly-results, earnings-call-transcript, and investor-presentation PDFs with source URLs, then search extracted text with page citations. The Reliance sample includes its official FY2025-26 annual report, a BSE-hosted concall transcript, and an NSE quarterly-results filing; the supported results table reports page-cited Revenue, segment EBITDA, PBT, and PAT with QoQ/YoY calculations. Network matches are woven into Push and Pull.

**Data and limitations:** NSE announcements and Yahoo EOD quotes are fetched live. Portfolio-card figures, detailed company profiles, demo-feed quarterly numbers, and network profiles are synthetic; the separate Reliance quarterly comparison is parsed from the cited exchange filing. Pull supports page-cited search, not a complete investment thesis, and the quarterly-results parser recognizes a narrow table format. The live Render app is running, but as of November 16, 2026 its hosted source library is empty and source-write controls are not yet disabled; the latest seeding and read-only configuration still needs to take effect there. Render's free storage is ephemeral. BSE announcement-feed ingestion is not connected. Threshold checks are user-triggered, not continuous background notifications. Network profiles are fictional; no real contact data was collected.

The current implementation uses no LLM or autonomous agent: prioritisation and network matching are deterministic. This keeps the demo explainable and avoids sending private network data to a model. A production design would require tenant-isolated storage, encryption, consent and deletion workflows, access control, source citations, and a reviewed policy for model use and data retention.

I would next expand structured results extraction across issuers and filing layouts, add a scheduled market/filing refresh with durable caching, and deploy the app behind authentication.

**Submission links:**

- Deployed prototype: https://finn-enam-assignment.onrender.com/
- Public GitHub repository: https://github.com/obul-reddy610/finn-enam-assignment
- AI build history / session export: [add the actual Copilot session share/export; it is not available yet]

Attach the actual coding-agent session export if you cannot provide a share link. `AI_BUILD_HISTORY.md` is only a summary and is not a substitute for the requested session history.

Regards,  
[Your name]
