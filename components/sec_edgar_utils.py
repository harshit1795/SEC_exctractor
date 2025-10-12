import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
import os
import streamlit as st

# IMPORTANT: Replace with your actual email address for SEC EDGAR API compliance
# SEC requires a valid User-Agent. Failure to provide one will result in 403 errors.
# Example: "Your Name YourEmail@example.com"
USER_AGENT = "YourName YourEmail@example.com" # <--- UPDATE THIS WITH YOUR EMAIL

SEC_DATA_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov"
}

SEC_ARCHIVE_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
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
        response = requests.get(url, headers=SEC_DATA_HEADERS) # Use SEC_DATA_HEADERS
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
        response = requests.get(doc_url, headers=SEC_ARCHIVE_HEADERS) # Use SEC_ARCHIVE_HEADERS
        response.raise_for_status()
        return response.content.decode("utf-8")
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading 10-K HTML from {doc_url}: {e}")
        return None

def parse_10k_sections(html_content):
    """Parses 10-K HTML content to extract specific sections (Item 1, 1A, 7)."""
    if not html_content:
        return "", "", ""
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    text = unicodedata.normalize("NFKD", text).encode('ascii', 'ignore').decode('utf8')
    text = " ".join(text.split("\n")) # Join by newline, not all whitespace

    def extract_section_text(full_text, start_pattern, end_pattern):
        starts = [i.start() for i in start_pattern.finditer(full_text)]
        ends = [i.start() for i in end_pattern.finditer(full_text)]
        
        # Find the best matching start and end for the section
        best_start = -1
        best_end = -1
        max_len = 0
        for s in starts:
            for e in ends:
                if s < e:
                    current_len = e - s
                    if current_len > max_len:
                        max_len = current_len
                        best_start = s
                        best_end = e
        
        if best_start != -1 and best_end != -1:
            return full_text[best_start:best_end].strip()
        return "Section not found or empty."

    # Regex patterns from the notebook, slightly adapted for robustness
    item1_start_pattern = re.compile(r"item\s*[1][\.\;\:\-\_]*\s*\b", re.IGNORECASE)
    item1_end_pattern = re.compile(r"item\s*1a[\.\;\:\-\_]\s*Risk|item\s*2[\.\,\;\:\-\_]\s*Prop", re.IGNORECASE)
    item1a_start_pattern = re.compile(r"(?<!,\s)item\s*1a[\.\;\:\-\_]\s*Risk", re.IGNORECASE)
    item1a_end_pattern = re.compile(r"item\s*2[\.\;\:\-\_]\s*Prop|item\s*[1][\.\;\:\-\_]*\s*\b", re.IGNORECASE)
    item7_start_pattern = re.compile(r"item\s*[7][\.\;\:\-\_]*\s*\bM", re.IGNORECASE)
    item7_end_pattern = re.compile(r"item\s*7a[\.\;\:\-\_]\sQuanti|item\s*8[\.\,\;\:\-\_]\s*", re.IGNORECASE)

    business_text = extract_section_text(text, item1_start_pattern, item1_end_pattern)
    risk_text = extract_section_text(text, item1a_start_pattern, item1a_end_pattern)
    mda_text = extract_section_text(text, item7_start_pattern, item7_end_pattern)
    
    return business_text, risk_text, mda_text