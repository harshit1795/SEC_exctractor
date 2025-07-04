import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import time

# Step 1: Get S&P 500 tickers from Wikipedia

def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    df = pd.read_html(str(table))[0]
    return df[['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry']]

# Step 2: Fetch fundamentals using yfinance

def get_fundamentals(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        # Some fields may be missing, so use .get()
        return {
            'Ticker': ticker,
            'Name': info.get('shortName'),
            'Sector': info.get('sector'),
            'Industry': info.get('industry'),
            'Market Cap': info.get('marketCap'),
            'Revenue (ttm)': info.get('totalRevenue'),
            'Net Income (ttm)': info.get('netIncomeToCommon'),
            'EPS (ttm)': info.get('trailingEps'),
            'Total Assets': info.get('totalAssets'),
            'Total Liabilities': info.get('totalLiab'),
            'Shareholder Equity': info.get('totalStockholderEquity'),
            'Cash': info.get('totalCash'),
            'Operating Cash Flow': info.get('operatingCashflow'),
            'Free Cash Flow': info.get('freeCashflow'),
            'Gross Margin': info.get('grossMargins'),
            'Operating Margin': info.get('operatingMargins'),
            'Net Margin': info.get('netMargins'),
            'PE Ratio': info.get('trailingPE'),
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return {'Ticker': ticker}

if __name__ == "__main__":
    print("Fetching S&P 500 tickers...")
    tickers_df = get_sp500_tickers()
    tickers = tickers_df['Symbol'].tolist()
    print(f"Found {len(tickers)} tickers.")

    fundamentals = []
    for i, ticker in enumerate(tickers):
        print(f"[{i+1}/{len(tickers)}] Fetching fundamentals for {ticker}...")
        data = get_fundamentals(ticker)
        # Add sector/industry from Wikipedia if missing
        if not data.get('Sector'):
            data['Sector'] = tickers_df[tickers_df['Symbol'] == ticker]['GICS Sector'].values[0]
        if not data.get('Industry'):
            data['Industry'] = tickers_df[tickers_df['Symbol'] == ticker]['GICS Sub-Industry'].values[0]
        fundamentals.append(data)
        time.sleep(0.5)  # To avoid rate limits

    df = pd.DataFrame(fundamentals)
    df.to_csv('sp500_fundamentals.csv', index=False)
    print("Done! Output written to sp500_fundamentals.csv") 