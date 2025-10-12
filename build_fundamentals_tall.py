import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

OUTPUT_PARQUET = "fundamentals_tall.parquet"
BATCH_SLEEP = 0.5  # seconds between API calls to be polite


def get_sp500_tickers() -> pd.DataFrame:
    """Scrape S&P-500 constituents from Wikipedia and return basic metadata."""
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    df = pd.read_html(str(table))[0]
    df.rename(columns={'Symbol': 'Ticker', 'Security': 'Name', 'GICS Sector': 'Sector',
                       'GICS Sub-Industry': 'Industry'}, inplace=True)
    return df[['Ticker', 'Name', 'Sector', 'Industry']]


def quarter_label(dt: pd.Timestamp) -> str:
    """Convert a date to fiscal period label e.g. 2023Q4."""
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year}Q{q}"


def melt_quarterly(df: pd.DataFrame, ticker: str, category: str) -> pd.DataFrame:
    """Convert yfinance quarterly DF (metrics x periods) to tall format."""
    if df is None or df.empty:
        return pd.DataFrame()
    # yfinance sometimes returns columns as str, ensure datetime
    cols = []
    for c in df.columns:
        try:
            cols.append(pd.to_datetime(c))
        except ValueError:
            # skip non-date columns
            cols.append(pd.NaT)
    df.columns = cols
    df = df.dropna(axis=1, how='all')
    records = []
    for metric, row in df.iterrows():
        for period_end, value in row.items():
            if pd.isna(period_end):
                continue
            records.append({
                'Ticker': ticker,
                'PeriodEnd': period_end.date(),
                'FiscalPeriod': quarter_label(period_end),
                'Metric': metric,
                'Category': category,
                'Value': float(value) if pd.notna(value) else None,
            })
    return pd.DataFrame(records)


def fetch_ticker_quarterly(ticker: str) -> pd.DataFrame:
    """Fetch income statement, balance sheet, cash flow quarterly data and return tall DF."""
    try:
        tkr = yf.Ticker(ticker)
        income = melt_quarterly(tkr.quarterly_financials, ticker, 'IncomeStatement')
        balance = melt_quarterly(tkr.quarterly_balance_sheet, ticker, 'BalanceSheet')
        cash = melt_quarterly(tkr.quarterly_cashflow, ticker, 'CashFlow')
        return pd.concat([income, balance, cash], ignore_index=True)
    except Exception as e:
        print(f"Failed {ticker}: {e}")
        return pd.DataFrame()


def main():
    print("Loading S&P 500 tickers…")
    meta_df = get_sp500_tickers()
    tickers = meta_df['Ticker'].tolist()
    print(f"Found {len(tickers)} tickers.")

    all_records = []
    for idx, tkr in enumerate(tickers, 1):
        print(f"[{idx}/{len(tickers)}] {tkr}")
        df_tkr = fetch_ticker_quarterly(tkr)
        if not df_tkr.empty:
            all_records.append(df_tkr)
        time.sleep(BATCH_SLEEP)

    if not all_records:
        print("No data fetched – exiting.")
        return

    final_df = pd.concat(all_records, ignore_index=True)
    print(f"Writing {len(final_df):,} rows to {OUTPUT_PARQUET}…")
    final_df.to_parquet(OUTPUT_PARQUET, index=False)
    print("Done.")


if __name__ == "__main__":
    main() 