import pandas as pd
import requests
import streamlit as st
import sec_parser as sp

# IMPORTANT: Replace with your actual email address for SEC EDGAR API compliance
SEC_HEADERS = {
    "User-Agent": "HarshitGola harshit.gola@gmail.com",
    "Accept-Encoding": "gzip, deflate"
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

def parse_10k_sections(html_content):
    """Parses 10-K HTML content to extract specific sections using sec-parser."""
    if not html_content:
        return "", "", ""

    try:
        parser = sp.Edgar10QParser()
        elements = parser.parse(html_content)
        tree_builder = sp.TreeBuilder()
        tree = tree_builder.build(elements)
        
        business_text = ""
        risk_text = ""
        mda_text = ""

        for node in tree.nodes:
            title = node.text.lower()
            if 'item 1.' in title and 'business' in title:
                business_text = "".join(desc.text for desc in node.get_descendants())
            elif 'item 1a.' in title and 'risk factors' in title:
                risk_text = "".join(desc.text for desc in node.get_descendants())
            elif 'item 7.' in title and 'management' in title and 'discussion' in title:
                mda_text = "".join(desc.text for desc in node.get_descendants())

        return business_text, risk_text, mda_text
    except Exception as e:
        st.error(f"Error parsing 10-K with sec-parser: {e}")
        return "", "", ""
