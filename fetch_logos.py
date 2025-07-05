import pandas as pd
import requests
import os
import time

def fetch_and_cache_logos(tickers_file="sp500_fundamentals.csv", output_dir="assets/logos"):
    """
    Fetches company logos for S&P 500 tickers using API-Ninja and caches them locally.
    """
    os.makedirs(output_dir, exist_ok=True)

    try:
        df = pd.read_csv(tickers_file)
        tickers = df["Ticker"].unique()
    except FileNotFoundError:
        print(f"Error: {tickers_file} not found. Please ensure it's in the correct directory.")
        return

    # IMPORTANT: Replace with your actual API-Ninja Key.
    # For a real application, use environment variables or Streamlit secrets for API keys.
    api_key = 'livTDbNkoOMN7yeNkNIhNA==4OpEMBaOVHwqOn8g' 

    for ticker in tickers:
        local_path = os.path.join(output_dir, f"{ticker}.png")
        if os.path.exists(local_path):
            print(f"Logo already exists for {ticker}. Skipping download.")
            continue

        try:
            api_url = f'https://api.api-ninjas.com/v1/logo?ticker={ticker}'
            
            print(f"Fetching logo for {ticker} from API-Ninja...")
            response = requests.get(api_url, headers={'X-Api-Key': api_key}, timeout=10)
            
            if response.status_code == requests.codes.ok:
                data = response.json()
                if data and len(data) > 0 and 'image' in data[0]:
                    logo_url = data[0]['image']
                    print(f"  Found logo URL for {ticker}: {logo_url}")
                    
                    img_resp = requests.get(logo_url, timeout=10)
                    if img_resp.status_code == 200:
                        with open(local_path, "wb") as f:
                            f.write(img_resp.content)
                        print(f"  Successfully saved logo for {ticker} to {local_path}")
                    else:
                        print(f"  Failed to download logo image from URL for {ticker}. Status code: {img_resp.status_code}")
                else:
                    print(f"  No logo image found in API-Ninja response for {ticker}")
            else:
                print(f"  API-Ninja Error for {ticker}: {response.status_code}, {response.text}")
        except requests.exceptions.Timeout:
            print(f"  Timeout fetching logo for {ticker}. Skipping.")
        except requests.exceptions.RequestException as e:
            print(f"  Network error fetching logo for {ticker}: {e}")
        except Exception as e:
            print(f"  An unexpected error occurred for {ticker}: {e}")
        
        time.sleep(0.1) # Be kind to the API

if __name__ == "__main__":
    fetch_and_cache_logos()
