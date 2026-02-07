import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path.cwd()))

from app.services.data_source_manager import DataSourceManager

async def test_sec_filings(ticker="AAPL"):
    print(f"\n--- Testing SEC Filings for {ticker} ---")
    manager = DataSourceManager()
    
    # Test Filing Metadata
    print("Fetching filing metadata...")
    data = await manager.get_sec_filing_data(ticker)
    if 'filings' in data and data['filings']:
        print("✅ Metadata fetched successfully")
        print(f"Latest 10-K: {data['filings'].get('10-k', {}).get('filingDate')}")
        print(f"Latest 10-Q: {data['filings'].get('10-q', {}).get('filingDate')}")
    else:
        print("❌ Failed to fetch metadata or no filings found")
        print(data)

    # Test 10-K Sections
    print("\nFetching 10-K Sections (Business, Risk)...")
    sections_10k = await manager.get_10k_section_data(ticker, ["business", "risk"])
    if sections_10k:
        print("✅ 10-K Sections fetched")
        for key, value in sections_10k.items():
            print(f"  - {key}: {len(value)} chars")
    else:
        print("❌ Failed to fetch 10-K sections")

async def test_earnings(ticker="AAPL"):
    print(f"\n--- Testing Earnings Data for {ticker} ---")
    manager = DataSourceManager()
    
    print("Fetching Yahoo Finance data...")
    data = await manager.get_yahoo_finance_data(ticker)
    
    earnings = data.get('earnings_dates')
    if earnings:
        print(f"✅ Earnings data found: {len(earnings)} records")
        print(f"Sample: {earnings[0]}")
    else:
        print("❌ No earnings data found")

async def main():
    await test_sec_filings()
    await test_earnings()

if __name__ == "__main__":
    asyncio.run(main())
