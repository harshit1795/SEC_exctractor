"""
Financial Health Score API endpoints
Calculates FinQ health scores for companies based on fundamentals parquet data.

Metrics used (all from fundamentals_tall.parquet):
  - Growth       : YoY Total Revenue growth
  - NetMargin    : Net Income / Total Revenue
  - FCFMargin    : Free Cash Flow / Total Revenue
  - DebtEquity   : Total Debt / Stockholders Equity

Each raw metric is percentile-ranked (0-1) across all scored tickers.
For Debt/Equity the score is inverted (lower D/E = healthier).
HealthScore = mean(GrowthScore, NetMarginScore, FCFMarginScore, DebtEquityScore)
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pathlib import Path
from app.database import get_db
from app.config import settings
import json
import pandas as pd
import numpy as np
import logging

# Flutter UI category name → Yahoo Finance sector names
CATEGORY_TO_YF_SECTORS: Dict[str, List[str]] = {
    "Technology":     ["Technology"],
    "Manufacturing":  ["Industrials", "Basic Materials"],
    "Finance":        ["Financial Services", "Real Estate"],
    "Energy":         ["Energy", "Utilities"],
    "Healthcare":     ["Healthcare"],
    "Consumer Goods": ["Consumer Defensive", "Consumer Cyclical"],
    "Other":          ["Communication Services"],
}

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health-scores", tags=["health-scores"])

# ─────────────────────────────────────────────
#  Internal helpers
# ─────────────────────────────────────────────

def _load_fundamentals() -> pd.DataFrame:
    """Load fundamentals_tall.parquet from known possible paths."""
    possible_paths = [
        Path("fundamentals_tall.parquet"),
        Path(settings.fundamentals_path),
        Path(__file__).parent.parent.parent.parent / settings.fundamentals_path,
        Path(__file__).parent.parent.parent.parent / "fundamentals_tall.parquet",
        Path("../fundamentals_tall.parquet"),
    ]
    for p in possible_paths:
        if p.exists():
            logger.info(f"Loading fundamentals from {p}")
            return pd.read_parquet(p)
    logger.error(f"fundamentals_tall.parquet not found. Tried: {possible_paths}")
    return pd.DataFrame()


_ticker_sectors_cache: Optional[Dict[str, str]] = None


def _load_ticker_sectors() -> Dict[str, str]:
    """Load ticker→sector mapping from ticker_sectors.json (built by scripts/build_ticker_sectors.py)."""
    global _ticker_sectors_cache
    if _ticker_sectors_cache is not None:
        return _ticker_sectors_cache

    possible_paths = [
        Path("ticker_sectors.json"),
        Path(__file__).parent.parent.parent / "ticker_sectors.json",
        Path(__file__).parent.parent.parent.parent / "ticker_sectors.json",
    ]
    for p in possible_paths:
        if p.exists():
            try:
                raw = json.loads(p.read_text())
                # {ticker: {sector: str, industry: str}} → {ticker: sector}
                _ticker_sectors_cache = {t: v.get("sector", "") for t, v in raw.items()}
                logger.info(f"Loaded {len(_ticker_sectors_cache)} ticker sectors from {p}")
                return _ticker_sectors_cache
            except Exception as e:
                logger.error(f"Failed to load ticker_sectors.json from {p}: {e}")

    logger.warning("ticker_sectors.json not found – category filtering will be skipped.")
    _ticker_sectors_cache = {}
    return _ticker_sectors_cache


def _tickers_for_category(category: Optional[str]) -> Optional[List[str]]:
    """
    Return the list of tickers that belong to the given Flutter UI category,
    or None if no filtering should be applied.
    """
    if not category:
        return None
    yf_sectors = CATEGORY_TO_YF_SECTORS.get(category)
    if yf_sectors is None:
        return None  # unknown category — no filter
    sector_map = _load_ticker_sectors()
    if not sector_map:
        return None  # mapping unavailable — no filter
    matched = [t for t, s in sector_map.items() if s in yf_sectors]
    logger.info(f"Category '{category}' → YF sectors {yf_sectors} → {len(matched)} tickers")
    return matched


def _get_metric_value(wide: pd.DataFrame, *names: str) -> Optional[float]:
    """Return the latest non-null value for the first matching metric column name."""
    for name in names:
        if name in wide.columns:
            val = wide[name].dropna()
            if not val.empty:
                return float(val.iloc[-1])
    return None


def _get_prev_metric_value(wide: pd.DataFrame, *names: str) -> Optional[float]:
    """Return the second-to-last non-null value for the first matching metric column name."""
    for name in names:
        if name in wide.columns:
            val = wide[name].dropna()
            if len(val) >= 2:
                return float(val.iloc[-2])
    return None


def _safe_div(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None or b == 0:
        return None
    return a / b


def _generate_text_insight(ticker: str, metrics: Dict[str, Any]) -> str:
    """Generate a concise human-readable insight string from metric scores."""
    parts = []
    gs = metrics.get("Growth_score")
    ns = metrics.get("NetMargin_score")
    fs = metrics.get("FCFMargin_score")
    ds = metrics.get("DebtEquity_score")

    if gs is not None and gs >= 0.7:
        g_pct = (metrics.get("Growth") or 0) * 100
        parts.append(f"Strong revenue growth ({g_pct:+.1f}%)")
    elif gs is not None and gs <= 0.3:
        g_pct = (metrics.get("Growth") or 0) * 100
        parts.append(f"Weak revenue growth ({g_pct:+.1f}%)")

    if ns is not None and ns >= 0.7:
        nm_pct = (metrics.get("NetMargin") or 0) * 100
        parts.append(f"high net margin ({nm_pct:.1f}%)")
    elif ns is not None and ns <= 0.3:
        nm_pct = (metrics.get("NetMargin") or 0) * 100
        parts.append(f"compressed margins ({nm_pct:.1f}%)")

    if fs is not None and fs >= 0.7:
        parts.append("excellent free cash flow conversion")
    
    if ds is not None and ds >= 0.7:
        parts.append("conservative balance sheet")
    elif ds is not None and ds <= 0.3:
        parts.append("elevated leverage")

    if not parts:
        hs = metrics.get("healthScore") or 0
        if hs >= 0.6:
            return f"{ticker} shows solid overall financial health."
        elif hs >= 0.4:
            return f"{ticker} shows moderate financial health across key metrics."
        else:
            return f"{ticker} shows below-average financial health based on available data."

    return f"{ticker}: " + "; ".join(parts) + "."


# ─────────────────────────────────────────────
#  Core computation functions
# ─────────────────────────────────────────────

async def compute_finq_health_scores(
    data_manager: Any = None,
    category: Optional[str] = None,
    ticker: Optional[str] = None,
    limit: int = 10,
) -> pd.DataFrame:
    """
    Compute FinQ health scores for all tickers (or filtered by category/ticker).

    Returns a DataFrame sorted by HealthScore descending.
    Columns: Ticker, Category, Growth, NetMargin, FCFMargin, DebtEquity,
             Growth_score, NetMargin_score, FCFMargin_score, DebtEquity_score,
             HealthScore, insight
    """
    all_fundamentals = _load_fundamentals()
    if all_fundamentals.empty:
        return pd.DataFrame()

    # Normalise column names
    ticker_col = next((c for c in ["Ticker", "ticker", "TICKER"] if c in all_fundamentals.columns), None)
    if ticker_col is None:
        logger.error("No Ticker column found in fundamentals data.")
        return pd.DataFrame()

    # Build the set of tickers to process
    allowed_tickers: Optional[List[str]] = None

    if ticker:
        # Multi-ticker support: split by comma
        allowed_tickers = [t.strip().upper() for t in ticker.split(",") if t.strip()]
    elif category:
        # Filter by sector using pre-built ticker_sectors.json
        allowed_tickers = _tickers_for_category(category)
        if allowed_tickers is not None and len(allowed_tickers) == 0:
            logger.warning(f"No tickers found for category '{category}'")
            return pd.DataFrame()

    if allowed_tickers is not None:
        t_mask = all_fundamentals[ticker_col].str.upper().isin([t.upper() for t in allowed_tickers])
        all_fundamentals = all_fundamentals[t_mask]
        if all_fundamentals.empty:
            logger.warning(f"No fundamentals data found after category/ticker filter")
            return pd.DataFrame()

    unique_tickers = all_fundamentals[ticker_col].unique().tolist()
    logger.info(f"Processing {len(unique_tickers)} tickers for health scores.")

    records = []
    for t in unique_tickers:
        try:
            t_df = all_fundamentals[all_fundamentals[ticker_col].str.upper() == t.upper()].copy()
            if t_df.empty:
                continue

            # Get category for this ticker from sector map
            t_category = _load_ticker_sectors().get(t.upper(), None)

            # Pivot to wide format: index=FiscalPeriod, columns=Metric, values=Value
            period_col = next((c for c in ["FiscalPeriod", "fiscalPeriod", "Period", "period"] if c in t_df.columns), None)
            metric_col = next((c for c in ["Metric", "metric"] if c in t_df.columns), None)
            value_col  = next((c for c in ["Value", "value"] if c in t_df.columns), None)

            if period_col is None or metric_col is None or value_col is None:
                continue

            wide = t_df.pivot_table(
                index=period_col, columns=metric_col, values=value_col, aggfunc="first"
            ).sort_index()

            if len(wide) < 2:
                logger.debug(f"Skipping {t}: need ≥2 periods, got {len(wide)}")
                continue

            # ── Raw metric extraction ─────────────────────────────
            rev_latest  = _get_metric_value(wide, "Total Revenue", "Operating Revenue")
            rev_prev    = _get_prev_metric_value(wide, "Total Revenue", "Operating Revenue")
            net_income  = _get_metric_value(wide, "Net Income", "Net Income Common Stockholders")
            fcf         = _get_metric_value(wide, "Free Cash Flow")
            total_debt  = _get_metric_value(wide, "Total Debt", "Long Term Debt And Capital Lease Obligation")
            equity      = _get_metric_value(wide, "Stockholders Equity", "Common Stock Equity")

            # ── Derived ratios ────────────────────────────────────
            growth      = _safe_div((rev_latest - rev_prev) if (rev_latest is not None and rev_prev is not None) else None, rev_prev)
            net_margin  = _safe_div(net_income, rev_latest)
            fcf_margin  = _safe_div(fcf, rev_latest)
            debt_equity = _safe_div(total_debt, equity) if (equity and equity > 0) else None

            # Skip if ALL four metrics are None
            if all(v is None for v in [growth, net_margin, fcf_margin, debt_equity]):
                continue

            records.append({
                "Ticker": t.upper(),
                "Category": t_category,
                "Growth": growth,
                "NetMargin": net_margin,
                "FCFMargin": fcf_margin,
                "DebtEquity": debt_equity,
            })
        except Exception as e:
            logger.error(f"Error processing ticker {t}: {e}")
            continue

    if not records:
        logger.warning("No records built — empty health scores result.")
        return pd.DataFrame()

    score_df = pd.DataFrame(records)
    n = len(score_df)
    logger.info(f"Built {n} ticker records. Computing percentile ranks …")

    # ── Percentile ranking (0.0 → 1.0, higher = better) ──────────
    for col in ["Growth", "NetMargin", "FCFMargin"]:
        valid_mask = score_df[col].notna()
        if valid_mask.sum() > 0:
            ranked = score_df.loc[valid_mask, col].rank(pct=True, method="average")
            score_df[f"{col}_score"] = np.nan
            score_df.loc[valid_mask, f"{col}_score"] = ranked
        else:
            score_df[f"{col}_score"] = np.nan

    # DebtEquity: lower D/E ratio → higher score (invert)
    valid_mask = score_df["DebtEquity"].notna()
    if valid_mask.sum() > 0:
        ranked = score_df.loc[valid_mask, "DebtEquity"].rank(pct=True, ascending=True, method="average")
        score_df["DebtEquity_score"] = np.nan
        score_df.loc[valid_mask, "DebtEquity_score"] = 1.0 - ranked  # invert
    else:
        score_df["DebtEquity_score"] = np.nan

    # ── Composite health score (mean of available metric scores) ──
    score_cols = ["Growth_score", "NetMargin_score", "FCFMargin_score", "DebtEquity_score"]
    score_df["HealthScore"] = score_df[score_cols].mean(axis=1, skipna=True)

    # ── Insight strings ───────────────────────────────────────────
    score_df["insight"] = score_df.apply(
        lambda row: _generate_text_insight(row["Ticker"], row.to_dict()), axis=1
    )

    result = score_df.sort_values("HealthScore", ascending=False).head(limit)
    logger.info(f"Returning {len(result)} health score records.")
    return result


def _df_to_scores_list(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert health score DataFrame rows to JSON-serialisable dicts."""
    records = []
    for _, row in df.iterrows():
        d: Dict[str, Any] = {"ticker": row["Ticker"]}
        for col in df.columns:
            if col == "Ticker":
                continue
            val = row[col]
            if isinstance(val, float) and np.isnan(val):
                d[col] = None
            elif isinstance(val, (np.floating, np.integer)):
                d[col] = float(val)
            elif pd.isna(val) if not isinstance(val, (list, dict)) else False:
                d[col] = None
            else:
                d[col] = val
        # Rename HealthScore → healthScore for Flutter model
        if "HealthScore" in d:
            d["healthScore"] = d.pop("HealthScore")
        records.append(d)
    return records


# ─────────────────────────────────────────────
#  API route: GET /api/health-scores/finq
# ─────────────────────────────────────────────

@router.get("/finq")
async def get_finq_health_scores(
    category: Optional[str] = Query(None, description="Filter by sector category"),
    ticker: Optional[str] = Query(None, description="Filter to a single ticker or comma-separated list of tickers"),
    limit: int = Query(10, ge=1, le=100, description="Max number of results"),
):
    """
    Return top tickers ranked by FinQ composite health score.

    Health Score = mean(Growth_score, NetMargin_score, FCFMargin_score, DebtEquity_score)
    where each score is a 0-1 percentile rank across the universe.
    """
    try:
        df = await compute_finq_health_scores(category=category, ticker=ticker, limit=limit)
        if df.empty:
            return {"scores": [], "count": 0, "category": category}

        scores = _df_to_scores_list(df)
        return {"scores": scores, "count": len(scores), "category": category}

    except Exception as e:
        logger.error(f"Error in get_finq_health_scores: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Health score computation failed: {str(e)}")


# ─────────────────────────────────────────────
#  API route: GET /api/health-scores/custom
# ─────────────────────────────────────────────

@router.get("/custom")
async def get_custom_health_scores(
    metrics: str = Query(..., description="Comma-separated metric names from the parquet file"),
    weights: str = Query(..., description="Comma-separated weights (must sum ≤ 1, will be normalised)"),
    category: Optional[str] = Query(None, description="Filter by sector category"),
    ticker: Optional[str] = Query(None, description="Filter to a single ticker"),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Return tickers ranked by a custom weighted health score using any metrics
    available in the fundamentals parquet file.
    """
    try:
        metric_list = [m.strip() for m in metrics.split(",") if m.strip()]
        weight_list = [float(w.strip()) for w in weights.split(",") if w.strip()]

        if not metric_list:
            raise HTTPException(status_code=400, detail="No metrics provided.")
        if len(metric_list) != len(weight_list):
            raise HTTPException(status_code=400, detail="metrics and weights must have the same length.")

        # Normalise weights
        total_w = sum(weight_list)
        if total_w <= 0:
            raise HTTPException(status_code=400, detail="Weights must be positive.")
        weight_list = [w / total_w for w in weight_list]

        all_fundamentals = _load_fundamentals()
        if all_fundamentals.empty:
            return {"scores": [], "count": 0}

        ticker_col = next((c for c in ["Ticker", "ticker", "TICKER"] if c in all_fundamentals.columns), None)
        period_col = next((c for c in ["FiscalPeriod", "fiscalPeriod", "Period"] if c in all_fundamentals.columns), None)
        metric_col = next((c for c in ["Metric", "metric"] if c in all_fundamentals.columns), None)
        value_col  = next((c for c in ["Value", "value"] if c in all_fundamentals.columns), None)

        if not all([ticker_col, period_col, metric_col, value_col]):
            raise HTTPException(status_code=500, detail="Unexpected parquet schema.")

        # Apply filters using sector-aware category mapping
        filtered = all_fundamentals
        if ticker:
            filtered = filtered[filtered[ticker_col].str.upper() == ticker.upper()]
        elif category:
            allowed = _tickers_for_category(category)
            if allowed is not None:
                filtered = filtered[filtered[ticker_col].str.upper().isin([t.upper() for t in allowed])]

        if filtered.empty:
            return {"scores": [], "count": 0}

        unique_tickers = filtered[ticker_col].unique()
        records = []

        for t in unique_tickers:
            try:
                t_df = filtered[filtered[ticker_col].str.upper() == t.upper()]
                t_category = _load_ticker_sectors().get(t.upper(), None)

                wide = t_df.pivot_table(
                    index=period_col, columns=metric_col, values=value_col, aggfunc="first"
                ).sort_index()

                if wide.empty:
                    continue

                row: Dict[str, Any] = {"Ticker": t.upper(), "Category": t_category}
                any_valid = False
                for m in metric_list:
                    val = _get_metric_value(wide, m)
                    row[m] = val
                    if val is not None:
                        any_valid = True

                if any_valid:
                    records.append(row)
            except Exception as e:
                logger.warning(f"Custom score error for {t}: {e}")
                continue

        if not records:
            return {"scores": [], "count": 0}

        score_df = pd.DataFrame(records)

        # Percentile rank each metric and compute weighted score
        score_df["HealthScore"] = 0.0
        for m, w in zip(metric_list, weight_list):
            if m not in score_df.columns:
                continue
            valid = score_df[m].notna()
            if valid.sum() > 0:
                ranked = score_df.loc[valid, m].rank(pct=True, method="average")
                score_df[f"{m}_score"] = np.nan
                score_df.loc[valid, f"{m}_score"] = ranked
                score_df["HealthScore"] += score_df[f"{m}_score"].fillna(0) * w

        score_df["insight"] = score_df.apply(
            lambda r: _generate_text_insight(r["Ticker"], r.to_dict()), axis=1
        )

        result = score_df.sort_values("HealthScore", ascending=False).head(limit)
        scores = _df_to_scores_list(result)
        return {"scores": scores, "count": len(scores)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_custom_health_scores: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Custom health score failed: {str(e)}")


# ─────────────────────────────────────────────
#  API route: POST /api/health-scores/report
# ─────────────────────────────────────────────

@router.post("/report")
async def generate_health_report(payload: Dict[str, Any]):
    """
    Generate an AI-powered HTML health report for one or multiple tickers.
    Accepts either a single ticker dict, or a dict with `tickers` list.
    """
    tickers_raw = payload.get("tickers")
    tickers_data = tickers_raw if isinstance(tickers_raw, list) else [payload]

    if not tickers_data:
        raise HTTPException(status_code=400, detail="No ticker data provided")
        
    def _fmt(v, pct=True):
        if v is None:
            return "N/A"
        if pct:
            return f"{v * 100:.1f}%"
        return f"{v:.2f}"
    
    # Build data string for prompt
    data_str = ""
    for t_data in tickers_data:
        t_name = t_data.get("ticker", "Unknown")
        t_cat = t_data.get("category", "")
        hs = t_data.get("healthScore")
        gr = t_data.get("growth")
        nm = t_data.get("netMargin")
        fm = t_data.get("fcfMargin")
        de = t_data.get("debtEquity")
        ins = t_data.get("insight", "")
        
        data_str += f"""
**Company:** {t_name}
**Sector:** {t_cat or 'N/A'}
**FinQ Health Score:** {_fmt(hs, pct=True) if hs is not None else 'N/A'}
- Revenue Growth (YoY): {_fmt(gr)}
- Net Margin: {_fmt(nm)}
- FCF Margin: {_fmt(fm)}
- Debt/Equity: {_fmt(de, pct=False)}
- AI Insight: {ins}
"""
    
    is_multi = len(tickers_data) > 1
    report_title = "Comparative Financial Health Report" if is_multi else f"{tickers_data[0]['ticker'] if isinstance(tickers_data[0], dict) else 'Unknown'} Financial Health Report"
    
    import datetime
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    
    prompt = f"""You are FinQ, an expert financial analyst. Write a professional, standalone HTML financial health report based purely on the metrics below.
    
{data_str}

REQUIREMENTS:
1. Output MUST be ONLY valid, self-contained HTML (no markdown wrappers like ```html).
2. Include inline CSS for a clean, professional PDF-ready styling (fonts, colors, tables).
3. Structure the report as follows:
   - Header (Report Title, and MUST include exactly: "Date of Generation: {current_date}" right-aligned or clearly visible at the top)
   - Executive Summary
   - Key Financial Ratios (A clean, styled HTML table comparing the provided metrics for all companies)
   - Strengths & Vulnerabilities (Bullet points for each company)
   - Investment Consideration & Conclusion
   - Sources & Citations (A dedicated section at the bottom listing the sources of this data, i.e., "Data provided by FinQ Financial Insights Engine", and mentioning SEC filings or standard market data as the origin)
   - Standard Disclaimer ("This report is for informational purposes only...")
4. Make the design pop by using FinQ brand colors (Green and Purple motifs) or a sleek modern palette.

Generate the HTML now:
"""

    try:
        from app.services.financial_analyzer import FinancialAnalyzer
        analyzer = FinancialAnalyzer()
        report = await analyzer.generate_text(prompt)
        # Strip potential markdown tick wrappers
        if report.startswith("```html"):
            report = report[7:]
        if report.endswith("```"):
            report = report[:-3]
            
        primary_ticker = tickers_data[0]['ticker'] if tickers_data and isinstance(tickers_data[0], dict) and 'ticker' in tickers_data[0] else 'Report'
        return {"report": report.strip(), "ticker": primary_ticker}
    except ValueError as e:
        # Gemini API key not configured
        raise HTTPException(status_code=500, detail=f"AI service not available: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating health report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")