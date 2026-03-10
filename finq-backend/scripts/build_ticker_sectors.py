"""
Script to pre-build ticker_sectors.json.
Reads all tickers from fundamentals_tall.parquet, fetches their sectors
from Yahoo Finance, and saves to ticker_sectors.json.

Run once:
    source venv/bin/activate
    python scripts/build_ticker_sectors.py
"""
import json
import time
from pathlib import Path
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed

PARQUET_PATH = Path("fundamentals_tall.parquet")
OUTPUT_PATH  = Path("ticker_sectors.json")

# Flutter UI category → Yahoo Finance sector names mapping
CATEGORY_TO_YF_SECTORS = {
    "Technology":     ["Technology"],
    "Manufacturing":  ["Industrials", "Basic Materials", "Consumer Cyclical"],
    "Finance":        ["Financial Services"],
    "Energy":         ["Energy", "Utilities"],
    "Healthcare":     ["Healthcare"],
    "Consumer Goods": ["Consumer Defensive", "Consumer Cyclical"],
    "Other":          [],  # catch-all
}


def fetch_sector(ticker: str):
    try:
        info = yf.Ticker(ticker).info
        sector   = info.get("sector") or ""
        industry = info.get("industry") or ""
        return ticker, sector, industry
    except Exception as e:
        return ticker, "", ""


def main():
    df = pd.read_parquet(PARQUET_PATH)
    tickers = sorted(df["Ticker"].unique().tolist())
    print(f"Fetching sectors for {len(tickers)} tickers …")

    results = {}
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(fetch_sector, t): t for t in tickers}
        done = 0
        for future in as_completed(futures):
            ticker, sector, industry = future.result()
            results[ticker] = {"sector": sector, "industry": industry}
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(tickers)} done …")

    OUTPUT_PATH.write_text(json.dumps(results, indent=2))
    print(f"\nSaved {len(results)} entries to {OUTPUT_PATH}")

    # Print sector distribution
    from collections import Counter
    sectors = Counter(v["sector"] for v in results.values() if v["sector"])
    print("\nSector distribution:")
    for s, n in sectors.most_common():
        print(f"  {s}: {n}")


if __name__ == "__main__":
    main()
