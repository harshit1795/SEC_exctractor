import pandas as pd
import os

def create_data_directories():
    """
    Reads the sp500_fundamentals.csv file and creates a directory for each ticker
    in the 'data' directory.
    """
    try:
        df = pd.read_csv("sp500_fundamentals.csv")
    except FileNotFoundError:
        print("Error: sp500_fundamentals.csv not found. Please run sp500_fundamentals.py first.")
        return

    if 'Ticker' not in df.columns:
        print("Error: 'Ticker' column not found in sp500_fundamentals.csv.")
        return

    tickers = df['Ticker'].tolist()
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    for ticker in tickers:
        # Replace characters that are invalid in directory names
        safe_ticker = str(ticker).replace('.', '-')
        ticker_dir = os.path.join(data_dir, safe_ticker)
        if not os.path.exists(ticker_dir):
            os.makedirs(ticker_dir)
    
    print(f"Created directories for all tickers in '{data_dir}'.")

if __name__ == "__main__":
    create_data_directories()
