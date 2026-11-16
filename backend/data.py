from __future__ import annotations

portfolio = [
    {
        "ticker": "RELIANCE.NS",
        "name": "Reliance Industries",
        "sector": "Energy, Retail & Telecom",
        "price": 2885.4,
        "change_pct": 1.8,
        "market_cap": "₹18.7T",
        "signal": "Core platform exposure; earnings volatility is offset by scale."
    },
    {
        "ticker": "TCS.NS",
        "name": "TCS",
        "sector": "IT Services",
        "price": 3815.2,
        "change_pct": 0.9,
        "market_cap": "₹13.8T",
        "signal": "Defensive enterprise demand and margin discipline."
    },
    {
        "ticker": "HDFCBANK.NS",
        "name": "HDFC Bank",
        "sector": "Banking",
        "price": 1716.1,
        "change_pct": -0.3,
        "market_cap": "₹12.2T",
        "signal": "Strong liability franchise, rate sensitivity remains key."
    },
    {
        "ticker": "ICICIBANK.NS",
        "name": "ICICI Bank",
        "sector": "Banking",
        "price": 1287.8,
        "change_pct": 1.6,
        "market_cap": "₹9.1T",
        "signal": "Credit growth remains the main operating lever."
    },
    {
        "ticker": "INFY.NS",
        "name": "Infosys",
        "sector": "IT Services",
        "price": 1604.5,
        "change_pct": 1.1,
        "market_cap": "₹7.9T",
        "signal": "AI-led deal wins are increasingly relevant to margin outlook."
    },
    {
        "ticker": "ITC.NS",
        "name": "ITC",
        "sector": "Consumer & Tobacco",
        "price": 465.7,
        "change_pct": 0.7,
        "market_cap": "₹6.4T",
        "signal": "Diversification and cigarette pricing still matter."
    },
    {
        "ticker": "SBI.NS",
        "name": "State Bank of India",
        "sector": "Banking",
        "price": 889.4,
        "change_pct": 2.3,
        "market_cap": "₹7.5T",
        "signal": "Provisioning discipline and loan growth are key."
    },
    {
        "ticker": "M&M.NS",
        "name": "Mahindra & Mahindra",
        "sector": "Automotive",
        "price": 3058.2,
        "change_pct": 2.1,
        "market_cap": "₹4.4T",
        "signal": "Vehicle demand and SUV mix remain the central story."
    },
    {
        "ticker": "MARUTI.NS",
        "name": "Maruti Suzuki",
        "sector": "Automotive",
        "price": 12418.0,
        "change_pct": -1.2,
        "market_cap": "₹4.0T",
        "signal": "Volume recovery is now balancing margin pressure."
    },
    {
        "ticker": "SUNPHARMA.NS",
        "name": "Sun Pharmaceutical",
        "sector": "Pharma",
        "price": 1710.3,
        "change_pct": 0.6,
        "market_cap": "₹4.7T",
        "signal": "US generics and specialty pipeline remain the focus."
    },
    {
        "ticker": "CIPLA.NS",
        "name": "Cipla",
        "sector": "Pharma",
        "price": 1620.9,
        "change_pct": 1.3,
        "market_cap": "₹1.2T",
        "signal": "Respiratory and complex generics deserve attention."
    },
    {
        "ticker": "BHARTIARTL.NS",
        "name": "Bharti Airtel",
        "sector": "Telecom",
        "price": 1748.5,
        "change_pct": 1.1,
        "market_cap": "₹9.3T",
        "signal": "ARPU expansion and capital discipline are the drivers."
    },
    {
        "ticker": "LTIM.NS",
        "name": "LTIMindtree",
        "sector": "IT Services",
        "price": 6056.1,
        "change_pct": -0.5,
        "market_cap": "₹1.7T",
        "signal": "Large deal conversion still matters more than short-term volume."
    },
    {
        "ticker": "ULTRACEMCO.NS",
        "name": "UltraTech Cement",
        "sector": "Construction Materials",
        "price": 11630.0,
        "change_pct": 1.9,
        "market_cap": "₹3.8T",
        "signal": "Growth and capacity spend are key to margin resilience."
    },
    {
        "ticker": "TITAN.NS",
        "name": "Titan Company",
        "sector": "Consumer & Retail",
        "price": 3658.2,
        "change_pct": 1.3,
        "market_cap": "₹3.6T",
        "signal": "Jewellery demand remains the main throughput engine."
    },
    {
        "ticker": "NTPC.NS",
        "name": "NTPC",
        "sector": "Power & Utilities",
        "price": 430.2,
        "change_pct": 1.4,
        "market_cap": "₹4.0T",
        "signal": "Power demand and capex intensity continue to matter."
    },
    {
        "ticker": "APOLLOHOSP.NS",
        "name": "Apollo Hospitals",
        "sector": "Healthcare",
        "price": 6705.0,
        "change_pct": 0.8,
        "market_cap": "₹1.0T",
        "signal": "Hospital occupancy and expansion pipeline are central."
    },
]

research_watchlist = ["INFY.NS", "SUNPHARMA.NS", "LTIM.NS", "APOLLOHOSP.NS", "ULTRACEMCO.NS"]

companies = {
    "RELIANCE.NS": {
        "name": "Reliance Industries",
        "sector": "Energy, Retail & Telecom",
        "business_snapshot": "Integrated conglomerate with major businesses across industrial fuel, telecom, digital services, retail and petrochemicals.",
        "financial_snapshot": {
            "revenue": "₹2.98L Cr",
            "ebitda": "₹1.12L Cr",
            "pat": "₹23,760 Cr",
            "margins": "EBITDA margin ~38%",
            "debt_to_equity": "1.1x"
        },
        "trajectory": "Consumer and digital businesses are accelerating, while upstream energy remains a swing factor.",
        "balance_sheet": "Balance sheet is highly asset-heavy but comfortably funded; capital intensity remains elevated.",
        "cash_quality": "Cash generation is strong but large capex and working-capital swings keep the conversion story uneven.",
        "narrative_vs_numbers": "Management continues to talk up retail and telecom scale, while the actual numbers show the strongest growth from digital and consumer-led segments.",
        "guidance": [
            {"metric": "Revenue growth", "guidance": "Double-digit in digital and consumer", "actual": "High-teens in consumer/digital"},
            {"metric": "Capex", "guidance": "Large and sustained", "actual": "Consistent capex remains elevated"}
        ],
        "bull_case": "The scale across energy, telecom, retail and digital can compound operating leverage over time.",
        "bear_case": "Execution risk and huge capital intensity mean the market remains sensitive to margin compression."
    },
    "TCS.NS": {
        "name": "TCS",
        "sector": "IT Services",
        "business_snapshot": "Global IT services provider with scale in cloud, engineering and digital transformation work.",
        "financial_snapshot": {
            "revenue": "₹2.46L Cr",
            "ebitda": "₹60,400 Cr",
            "pat": "₹48,700 Cr",
            "margins": "EBITDA margin ~24.5%",
            "debt_to_equity": "0.2x"
        },
        "trajectory": "Large deal momentum has remained relatively stable, with discretionary spend still patchy.",
        "balance_sheet": "The balance sheet is conservative, giving a strong cushion against a softer demand cycle.",
        "cash_quality": "Profit conversion into cash remains excellent and supports buybacks and dividends.",
        "narrative_vs_numbers": "Management's narrative emphasises transformation-led demand, while the numbers reflect continued steady execution despite macro headwinds.",
        "guidance": [
            {"metric": "Revenue growth", "guidance": "Mid-single digit to high-single digit", "actual": "Near the upper end in strong quarters"},
            {"metric": "Margins", "guidance": "Stable to modestly improving", "actual": "Hold steady with operating leverage"}
        ],
        "bull_case": "Defensive IT exposure with scale, strong cash flows and long-duration contracts. ",
        "bear_case": "A weak enterprise spending backdrop can still compress deal conversion and sentiment."
    },
    "HDFCBANK.NS": {
        "name": "HDFC Bank",
        "sector": "Banking",
        "business_snapshot": "Large private-sector bank with a strong retail customer franchise and large corporate banking exposure.",
        "financial_snapshot": {
            "revenue": "₹1.64L Cr",
            "ebitda": "₹1.14L Cr",
            "pat": "₹67,000 Cr",
            "margins": "NIM ~3.4%",
            "debt_to_equity": "0.9x"
        },
        "trajectory": "Loan growth is healthy, though deposit growth and margin pressure continue to shape the earnings profile.",
        "balance_sheet": "Strong capital base supports growth and risk absorption.",
        "cash_quality": "Capital generation remains solid, with asset quality staying manageable.",
        "narrative_vs_numbers": "Management stresses deposit mobilisation and balance-sheet discipline; the numbers support this with stable credit costs and healthy franchise earnings.",
        "guidance": [
            {"metric": "Credit growth", "guidance": "Healthy double-digit", "actual": "Growth remains in line"},
            {"metric": "Margin", "guidance": "Stable with some pressure", "actual": "Stable-to-slightly compressed"}
        ],
        "bull_case": "Best-in-class franchise and deposit growth should keep profitability intact.",
        "bear_case": "Rate moves and funding costs could pressure asset yields and net interest margin."
    },
    "INFY.NS": {
        "name": "Infosys",
        "sector": "IT Services",
        "business_snapshot": "Large digital and consulting company with strong presence in enterprise transformation, cloud and AI work.",
        "financial_snapshot": {
            "revenue": "₹1.61L Cr",
            "ebitda": "₹42,600 Cr",
            "pat": "₹27,200 Cr",
            "margins": "EBITDA margin ~26.4%",
            "debt_to_equity": "0.1x"
        },
        "trajectory": "Deal wins have improved, while margin conversion is being tested by AI investments and wage inflation.",
        "balance_sheet": "Balance sheet remains strong, with low leverage and high cash generation.",
        "cash_quality": "Cash conversion remains superior to many peers, which helps in valuation support.",
        "narrative_vs_numbers": "The company has been telling a story of AI-led growth and productivity, but the real question is whether deal momentum translates into stable operating leverage.",
        "guidance": [
            {"metric": "Revenue growth", "guidance": "Low-to-mid single digit", "actual": "Within guidance band"},
            {"metric": "Operating margin", "guidance": "Stable", "actual": "Stable to slightly softer"}
        ],
        "bull_case": "Strong enterprise relationships and AI-led consulting opportunities can support next leg of growth.",
        "bear_case": "The AI and cost-to-serve story remains early, and large-scale transformation projects are uneven."
    },
    "SUNPHARMA.NS": {
        "name": "Sun Pharmaceutical",
        "sector": "Pharma",
        "business_snapshot": "Global pharma company led by specialty and generics franchises across the US, Europe and India.",
        "financial_snapshot": {
            "revenue": "₹48,100 Cr",
            "ebitda": "₹13,400 Cr",
            "pat": "₹9,900 Cr",
            "margins": "EBITDA margin ~27.8%",
            "debt_to_equity": "0.3x"
        },
        "trajectory": "The specialty pipeline and US market exposure remain the key swing factors.",
        "balance_sheet": "Leverage is manageable, with good operating cash generation.",
        "cash_quality": "Profits convert into free cash with a reasonable degree of predictability.",
        "narrative_vs_numbers": "Management emphasises specialty growth, while the numbers show that generic mix and approval timing remain important variables.",
        "guidance": [
            {"metric": "US growth", "guidance": "Double-digit for specialty push", "actual": "Improving but still uneven"},
            {"metric": "Margin", "guidance": "Stable", "actual": "Generally stable"}
        ],
        "bull_case": "A diversified pharma model and improved specialty portfolio can sustain higher growth rates.",
        "bear_case": "Regulatory and pricing volatility in the US can move earnings materially."
    },
    "LTIM.NS": {
        "name": "LTIMindtree",
        "sector": "IT Services",
        "business_snapshot": "Mid-cap IT services company focused on a mix of digital transformation, data and analytics, and engineering services.",
        "financial_snapshot": {
            "revenue": "₹17,400 Cr",
            "ebitda": "₹3,960 Cr",
            "pat": "₹2,650 Cr",
            "margins": "EBITDA margin ~22.7%",
            "debt_to_equity": "0.2x"
        },
        "trajectory": "The company remains reliant on large deal conversion and digital project execution quality.",
        "balance_sheet": "Balance sheet is lean and efficient.",
        "cash_quality": "Cash generation is healthy and supports capital allocation flexibility.",
        "narrative_vs_numbers": "Management has kept the story focused on digital enterprise work; the numbers show that execution quality still matters more than broad macro comments.",
        "guidance": [
            {"metric": "Revenue growth", "guidance": "Double-digit in selected verticals", "actual": "Selective growth remains visible"},
            {"metric": "Margin", "guidance": "Expansion cadence", "actual": "Operating leverage remains moderate"}
        ],
        "bull_case": "Selective deal wins in digital and data services can meaningfully accelerate growth.",
        "bear_case": "The model remains more exposed to specific client concentration and project timing."
    },
    "ULTRACEMCO.NS": {
        "name": "UltraTech Cement",
        "sector": "Construction Materials",
        "business_snapshot": "India's leading cement producer with a large efficiency and capacity expansion footprint.",
        "financial_snapshot": {
            "revenue": "₹64,300 Cr",
            "ebitda": "₹14,900 Cr",
            "pat": "₹6,900 Cr",
            "margins": "EBITDA margin ~23.2%",
            "debt_to_equity": "0.5x"
        },
        "trajectory": "Capacity and pricing discipline are the determinant of margin profile in a commodity cycle.",
        "balance_sheet": "Leverage is manageable, but large capex plans can pressure balance sheet flexibility.",
        "cash_quality": "Cash conversion is decent, with profit translating into real cash when demand remains firm.",
        "narrative_vs_numbers": "Management's capex story makes sense only if demand remains resilient and plant utilisation is strong.",
        "guidance": [
            {"metric": "Volume growth", "guidance": "Mid-single digit to high-single digit", "actual": "Volume trends align with guidance"},
            {"metric": "Capex", "guidance": "Large but phased", "actual": "Execution remains disciplined"}
        ],
        "bull_case": "Margin expansion can be meaningful as capacity utilisation improves and cost discipline continues.",
        "bear_case": "Cement is a commodity; oversupply and slower infrastructure spend can hit margins."
    },
    "APOLLOHOSP.NS": {
        "name": "Apollo Hospitals",
        "sector": "Healthcare",
        "business_snapshot": "Large healthcare services company with strong hospital, diagnostics and digital health presence.",
        "financial_snapshot": {
            "revenue": "₹20,200 Cr",
            "ebitda": "₹4,600 Cr",
            "pat": "₹1,540 Cr",
            "margins": "EBITDA margin ~22.8%",
            "debt_to_equity": "0.4x"
        },
        "trajectory": "Expansion in premium healthcare capacity and diagnostics remains the operating growth engine.",
        "balance_sheet": "Expansion has been capital intensive, though earnings quality is improving.",
        "cash_quality": "Careful pricing and occupancy metrics support cash conversion.",
        "narrative_vs_numbers": "Management's narrative is about hospital expansion and premiumisation; the operating data has supported that story to a degree.",
        "guidance": [
            {"metric": "Bed expansion", "guidance": "Ongoing network expansion", "actual": "Expansion remains on track"},
            {"metric": "Occupancy", "guidance": "High-single-digit growth", "actual": "Stable to improving"}
        ],
        "bull_case": "Healthcare demand remains structurally solid and premiumisation can improve unit economics.",
        "bear_case": "Asset-heavy expansion can pressure returns unless occupancy and pricing hold."
    },
}

announcements = [
    {
        "ticker": "TCS.NS",
        "name": "TCS",
        "category": "results",
        "date": "2026-11-16T13:15:00+05:30",
        "headline": "TCS reports strong deal momentum and stable margins",
        "summary": "Revenue and operating margin held firm despite a cautious enterprise environment. The company highlighted robust digital transformation bookings.",
        "priority": 92,
        "why_it_matters": "This is a quality check on enterprise software spending and near-term demand resilience.",
        "illustrative_results": {
            "period": "Illustrative quarter",
            "unit": "₹ crore",
            "metrics": {
                "Revenue": {"current": 65000, "previous_quarter": 64000, "year_ago_quarter": 59000},
                "EBITDA": {"current": 17000, "previous_quarter": 16600, "year_ago_quarter": 15300},
                "PBT": {"current": 16900, "previous_quarter": 16400, "year_ago_quarter": 15100},
                "PAT": {"current": 13000, "previous_quarter": 12800, "year_ago_quarter": 11800}
            }
        }
    },
    {
        "ticker": "RELIANCE.NS",
        "name": "Reliance",
        "category": "M&A",
        "date": "2026-11-16T12:45:00+05:30",
        "headline": "Reliance expands telecom and retail platform capacity",
        "summary": "Management approved a platform expansion spending plan linked to digital infrastructure and consumer operations footprint expansion.",
        "priority": 95,
        "why_it_matters": "The investment indicates continued commitment to consumer and digital scale, which can compound operating leverage over time."
    },
    {
        "ticker": "CIPLA.NS",
        "name": "Cipla",
        "category": "management_change",
        "date": "2026-11-16T11:30:00+05:30",
        "headline": "Cipla appoints new India business head after senior leadership change",
        "summary": "The company named a new leader for its domestic business, with the transition expected to sharpen execution in the formulation pipeline.",
        "priority": 78,
        "why_it_matters": "Leadership changes in pharma often matter because of execution and pipeline continuity."
    },
    {
        "ticker": "ULTRACEMCO.NS",
        "name": "UltraTech Cement",
        "category": "capex",
        "date": "2026-11-16T10:15:00+05:30",
        "headline": "UltraTech approves additional clinker and grinding capacity",
        "summary": "The company approved incremental capital expenditure to expand regional capacity and support demand growth across infrastructure markets.",
        "priority": 86,
        "why_it_matters": "Large capex matters because cement returns are sensitive to capacity utilisation and commodity cycles."
    },
    {
        "ticker": "SUNPHARMA.NS",
        "name": "Sun Pharma",
        "category": "litigation",
        "date": "2026-11-15T16:30:00+05:30",
        "headline": "US regulatory filing adds fresh compliance scrutiny for a key product line",
        "summary": "The company disclosed a regulatory action linked to a formulation product, increasing focus on compliance discipline.",
        "priority": 81,
        "why_it_matters": "Regulatory headlines can have a disproportionate effect on specialty and US pipeline earnings."
    },
    {
        "ticker": "INFY.NS",
        "name": "Infosys",
        "category": "earnings_call",
        "date": "2026-11-15T14:00:00+05:30",
        "headline": "Infosys earnings call highlights AI-led deal momentum",
        "summary": "Management framed the quarter around AI transformation projects and productivity gains, while noting a still-cautious enterprise spending backdrop.",
        "priority": 88,
        "why_it_matters": "This is an important signal for investors tracking the next phase of AI monetisation in services."
    },
    {
        "ticker": "ITC.NS",
        "name": "ITC",
        "category": "dividend",
        "date": "2026-11-15T12:00:00+05:30",
        "headline": "ITC declares dividend, with record date set for next week",
        "summary": "The board approved another cash payout, reinforcing the company’s cash generation and shareholder-friendly capital allocation.",
        "priority": 62,
        "why_it_matters": "This is more income-focused than high-conviction operating news, but still relevant to shareholder return tracking."
    },
    {
        "ticker": "BHARTIARTL.NS",
        "name": "Bharti Airtel",
        "category": "fund_raise",
        "date": "2026-11-14T15:00:00+05:30",
        "headline": "Bharti Airtel finalises funding through a strategic capital instrument",
        "summary": "The company confirmed a new strategic capital raise aimed at network expansion and balance-sheet flexibility.",
        "priority": 74,
        "why_it_matters": "Capital structure changes matter when networks are being scaled and tariff actions remain dynamic."
    },
]

network_people = [
    {
        "id": "neha_singh",
        "name": "Neha Singh",
        "role": "Former Retail Strategy Lead, Reliance Retail",
        "relationship": "Strong overlap with Reliance and consumer businesses",
        "company_overlap": ["RELIANCE.NS", "TITAN.NS", "ITC.NS"],
        "why_helpful": "Can help explain retail execution, pricing power and consumer behaviour in the India market.",
        "strength": 92
    },
    {
        "id": "akshay_nair",
        "name": "Akshay Nair",
        "role": "Ex-Enterprise Transformation Partner, Infosys",
        "relationship": "Former team member and digital programme advisor",
        "company_overlap": ["INFY.NS", "TCS.NS", "LTIM.NS"],
        "why_helpful": "Best person to speak to about AI-driven service transformation and enterprise delivery quality.",
        "strength": 90
    },
    {
        "id": "meher_kaul",
        "name": "Meher Kaul",
        "role": "Former Product & Ops Head, Apollo Hospitals",
        "relationship": "Worked across hospital network and patient-flow optimisation",
        "company_overlap": ["APOLLOHOSP.NS", "TITAN.NS"],
        "why_helpful": "Useful for understanding margin quality, occupancy and premiumisation in healthcare services.",
        "strength": 87
    },
    {
        "id": "dev_bhatt",
        "name": "Dev Bhatt",
        "role": "Ex-Capital Projects Executive, UltraTech Cement",
        "relationship": "Built out capacity and plant expansion programs",
        "company_overlap": ["ULTRACEMCO.NS", "NTPC.NS", "M&M.NS"],
        "why_helpful": "Best contact for capex execution, cost discipline and utilisation questions in industrial assets.",
        "strength": 91
    },
    {
        "id": "sana_agarwal",
        "name": "Sana Agarwal",
        "role": "Former Pharma Commercial Lead, Sun Pharma",
        "relationship": "Worked in India and US portfolio execution",
        "company_overlap": ["SUNPHARMA.NS", "CIPLA.NS"],
        "why_helpful": "Useful for product-franchise and compliance risk context in pharma portfolios.",
        "strength": 85
    },
    {
        "id": "pranay_seth",
        "name": "Pranay Seth",
        "role": "Banking and debt markets advisor",
        "relationship": "Spent time with HDFC and SBI strategy teams",
        "company_overlap": ["HDFCBANK.NS", "SBI.NS", "ICICIBANK.NS"],
        "why_helpful": "Ideal for debt, liquidity and asset-quality conversations in Indian financials.",
        "strength": 83
    },
]
