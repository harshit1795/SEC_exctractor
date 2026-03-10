import sys
import pandas as pd
from typing import Dict, Any

sys.path.append('.')
from app.api.health_scores import _load_fundamentals, _get_metric_value, _get_prev_metric_value, _safe_div, _load_ticker_sectors

all_fundamentals = _load_fundamentals()
print(f"Loaded {len(all_fundamentals)} rows")

ticker_col = next((c for c in ["Ticker", "ticker", "TICKER"] if c in all_fundamentals.columns), None)
period_col = next((c for c in ["FiscalPeriod", "fiscalPeriod", "Period", "period"] if c in all_fundamentals.columns), None)
metric_col = next((c for c in ["Metric", "metric"] if c in all_fundamentals.columns), None)
value_col  = next((c for c in ["Value", "value"] if c in all_fundamentals.columns), None)

filtered = all_fundamentals
filtered["_Ticker_UPPER"] = filtered[ticker_col].str.upper()
agg_fund = filtered.groupby(["_Ticker_UPPER", period_col, metric_col], as_index=False)[value_col].first()
wide_all = agg_fund.pivot(
    index=["_Ticker_UPPER", period_col], columns=metric_col, values=value_col
).sort_index()

metric_list = ["Revenue Growth", "Net Margin", "FCF Margin", "Debt to Equity", "ROE", "P/E Ratio", "ROA", "Current Ratio", "Quick Ratio"]

t_upper = "AAPL"
if t_upper in wide_all.index.levels[0]:
    wide = wide_all.loc[t_upper]
    
    rev_latest = _get_metric_value(wide, "Total Revenue", "Operating Revenue")
    rev_prev   = _get_prev_metric_value(wide, "Total Revenue", "Operating Revenue")
    net_income = _get_metric_value(wide, "Net Income", "Net Income Common Stockholders", "Operating Income")
    fcf        = _get_metric_value(wide, "Free Cash Flow")
    total_debt = _get_metric_value(wide, "Total Debt", "Long Term Debt And Capital Lease Obligation", "Current Debt And Capital Lease Obligation")
    equity     = _get_metric_value(wide, "Stockholders Equity", "Common Stock Equity", "Total Equity Gross Minority Interest")
    assets     = _get_metric_value(wide, "Total Assets")

    print(f"rev_latest: {rev_latest}")
    print(f"rev_prev: {rev_prev}")
    print(f"net_income: {net_income}")
    print(f"fcf: {fcf}")
    print(f"total_debt: {total_debt}")
    print(f"equity: {equity}")
    print(f"assets: {assets}")

    row: Dict[str, Any] = {"Ticker": t_upper}
    any_valid = False
    for m in metric_list:
        val = None
        if m == "Revenue Growth":
            val = _safe_div((rev_latest - rev_prev) if rev_latest is not None and rev_prev is not None else None, rev_prev)
        elif m == "Net Margin":
            val = _safe_div(net_income, rev_latest)
        elif m == "FCF Margin":
            val = _safe_div(fcf, rev_latest)
        elif m == "Debt to Equity":
            val = _safe_div(total_debt, equity) if equity and equity > 0 else None
        elif m == "ROA":
            val = _safe_div(net_income, assets)
        elif m == "ROE":
            val = _safe_div(net_income, equity) if equity and equity > 0 else None
        elif m == "Current Ratio":
            ca = _get_metric_value(wide, "Current Assets")
            cl = _get_metric_value(wide, "Current Liabilities")
            val = _safe_div(ca, cl)
            print(f"CA: {ca}, CL: {cl}")
        elif m == "Quick Ratio":
            ca = _get_metric_value(wide, "Current Assets")
            inv = _get_metric_value(wide, "Inventory")
            cl = _get_metric_value(wide, "Current Liabilities")
            if ca is not None and inv is not None and cl is not None:
                val = _safe_div(ca - inv, cl)
            print(f"CA: {ca}, INV: {inv}, CL: {cl}")
        elif m == "P/E Ratio":
            val = None # Not available in simple fundamental data
        else:
            val = _get_metric_value(wide, m)

        row[m] = val
        print(f"{m} => {val}")
        if val is not None:
            any_valid = True
    
    print(f"any_valid = {any_valid}")
   
