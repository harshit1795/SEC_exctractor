import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
import os
import streamlit as st

# IMPORTANT: Replace with your actual email address for SEC EDGAR API compliance
SEC_HEADERS = {
    "User-Agent": "HarshitGola harshit.gola@gmail.com", 
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov"
}

@st.cache_data(ttl=3600) # Cache for 1 hour
def load_cik_ticker_map():
    """Loads the CIK-ticker mapping from company_tickers.json."""
    try:
        # Adjust path if necessary based on deployment
        cik_df = pd.read_json("company_tickers.json").T
        cik_df.rename(columns={'cik_str': 'cik', 'title': 'name'}, inplace=True)
        cik_df['cik'] = cik_df['cik'].astype(str).str.zfill(10) # Ensure CIK is 10 digits
        return cik_df
    except Exception as e:
        st.error(f"Error loading CIK-ticker map: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600) # Cache for 1 hour
def get_company_filings(cik):
    """Fetches a company's recent filing history from SEC EDGAR API."""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    try:
        response = requests.get(url, headers=SEC_HEADERS)
        response.raise_for_status() # Raise an exception for HTTP errors
        company_filings = response.json()
        filings_df = pd.DataFrame(company_filings["filings"]["recent"])
        return filings_df
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching filing history for CIK {cik}: {e}")
        return pd.DataFrame()
    except KeyError:
        st.error(f"Could not parse filing history for CIK {cik}. Data structure might have changed.")
        return pd.DataFrame()

@st.cache_data(ttl=3600) # Cache for 1 hour
def get_latest_10k_filing_info(ticker, cik, filings_df):
    """Identifies the latest 10-K filing from the filings DataFrame."""
    if filings_df.empty:
        return None
    
    # Filter for 10-K forms and sort by filingDate to get the latest
    latest_10k = filings_df[filings_df['form'] == '10-K']
    if latest_10k.empty:
        return None
    
    latest_10k = latest_10k.sort_values(by='filingDate', ascending=False).iloc[0]
    
    # Construct the URL to the actual HTML document
    accession_number = latest_10k['accessionNumber'].replace('-', '')
    primary_document = latest_10k['primaryDocument']
    
    # SEC archive URL structure
    doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_number}/{primary_document}"
    
    return {
        "ticker": ticker,
        "cik": cik,
        "accessionNumber": latest_10k['accessionNumber'],
        "filingDate": latest_10k['filingDate'],
        "primaryDocument": latest_10k['primaryDocument'],
        "doc_url": doc_url
    }

@st.cache_data(ttl=3600) # Cache for 1 hour
def download_10k_html(doc_url):
    """Downloads the HTML content of a 10-K filing."""
    try:
        response = requests.get(doc_url, headers=SEC_HEADERS)
        response.raise_for_status()
        return response.content.decode("utf-8")
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading 10-K HTML from {doc_url}: {e}")
        return None

def parse_10k_sections(html_content, section_type):
    """Parses 10-K HTML content to extract specific sections."""
    if not html_content:
        return "", "", ""

    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    text = unicodedata.normalize("NFKD", text).encode('ascii', 'ignore').decode('utf8')
    text = " ".join(text.split())

    business_text = ""
    risk_text = ""
    mda_text = ""

    # Regex patterns for Item 1 (Business), Item 1A (Risk Factors), Item 7 (MD&A)
    # These patterns are simplified and might need refinement for robustness
    item1_pattern = re.compile(r'item\s*1\.\s*business', re.IGNORECASE)
    item1a_pattern = re.compile(r'item\s*1a\.\s*risk\s*factors', re.IGNORECASE)
    item7_pattern = re.compile(r'item\s*7\.\s*management\s*'
                               r's\s*discussion\s*and\s*analysis\s*'
                               r'of\s*financial\s*condition\s*and\s*'
                               r'results\s*of\s*operations', re.IGNORECASE)
    
    # Find start and end of sections
    item1_match = item1_pattern.search(text)
    item1a_match = item1a_pattern.search(text)
    item7_match = item7_pattern.search(text)

    # Extract Business (Item 1)
    if item1_match:
        start = item1_match.end()
        end = item1a_match.start() if item1a_match else (item7_match.start() if item7_match else len(text))
        business_text = text[start:end].strip()

    # Extract Risk Factors (Item 1A)
    if item1a_match:
        start = item1a_match.end()
        end = item7_match.start() if item7_match else len(text)
        risk_text = text[start:end].strip()

    # Extract MD&A (Item 7)
    if item7_match:
        start = item7_match.end()
        # MD&A usually ends before Item 7A or Item 8
        item7a_pattern = re.compile(r'item\s*7a\.\s*quantitative\s*and\s*qualitative', re.IGNORECASE)
        item8_pattern = re.compile(r'item\s*8\.\s*financial\s*statements', re.IGNORECASE)
        end = item7a_pattern.search(text).start() if item7a_pattern.search(text) else \
              (item8_pattern.search(text).start() if item8_pattern.search(text) else len(text))
        mda_text = text[start:end].strip()

    return business_text, risk_text, mda_text
