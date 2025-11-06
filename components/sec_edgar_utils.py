import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup
import re

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
def get_latest_10q_filing_info(ticker, cik, filings_df):
    """Identifies the latest 10-Q filing from the filings DataFrame."""
    if filings_df.empty:
        return None
    
    # Filter for 10-Q forms and sort by filingDate to get the latest
    latest_10q = filings_df[filings_df['form'] == '10-Q']
    if latest_10q.empty:
        return None
    
    latest_10q = latest_10q.sort_values(by='filingDate', ascending=False).iloc[0]
    
    # Construct the URL to the actual HTML document
    accession_number = latest_10q['accessionNumber'].replace('-', '')
    primary_document = latest_10q['primaryDocument']
    
    # SEC archive URL structure
    doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_number}/{primary_document}"
    
    return {
        "ticker": ticker,
        "cik": cik,
        "accessionNumber": latest_10q['accessionNumber'],
        "filingDate": latest_10q['filingDate'],
        "primaryDocument": latest_10q['primaryDocument'],
        "doc_url": doc_url
    }

@st.cache_data(ttl=3600) # Cache for 1 hour
def download_filing_html(doc_url):
    """Downloads the HTML content of a filing."""
    try:
        response = requests.get(doc_url, headers=SEC_HEADERS)
        response.raise_for_status()
        return response.content.decode("utf-8")
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading filing HTML from {doc_url}: {e}")
        return None

def parse_10k_sections(html_content):
    """Parses 10-K HTML content to extract specific sections using BeautifulSoup."""
    if not html_content:
        return "", "", ""

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Create a set of all section anchors for quick lookups
        section_anchors = set()
        toc_links = []
        # Find all links that look like they are part of a ToC
        for link in soup.find_all('a', href=re.compile(r'^#\w')):
            link_text = link.get_text(strip=True).lower()
            # Heuristic for ToC links: they usually contain "item"
            if 'item' in link_text:
                 section_anchors.add(link['href'])
                 toc_links.append(link)

        def get_section_text(keywords):
            target_link = None
            for link in toc_links:
                if any(keyword in link.get_text(strip=True).lower() for keyword in keywords):
                    target_link = link
                    break
            if not target_link:
                return ""

            start_id = target_link['href'][1:]
            start_tag = soup.find(id=start_id) or soup.find('a', {'name': start_id})
            if not start_tag:
                return ""

            content = []
            for elem in start_tag.find_all_next():
                # Stop if we hit another section
                if elem.name == 'a' and elem.has_attr('href') and elem['href'] in section_anchors and elem['href'] != target_link['href']:
                    break
                if elem.name == 'a' and elem.has_attr('name') and '#' + elem['name'] in section_anchors and '#' + elem['name'] != target_link['href']:
                    break
                
                # Heuristic to stop at document end markers
                if elem.name == 'hr' and len(content) > 100:
                    break

                # Get text from non-script and non-style tags
                if elem.name not in ['script', 'style']:
                    text = elem.get_text(strip=True)
                    if text:
                        content.append(text)
            
            return " ".join(content)

        business_text = get_section_text(['item 1', 'business'])
        risk_text = get_section_text(['item 1a', 'risk factors'])
        mda_text = get_section_text(["item 7", "management's discussion and analysis"])

        return business_text, risk_text, mda_text

    except Exception as e:
        st.error(f"Error parsing 10-K with BeautifulSoup: {e}")
        return "", "", ""

def parse_10q_sections(html_content):
    """Parses 10-Q HTML content to extract specific sections using BeautifulSoup."""
    if not html_content:
        return "", ""

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Create a set of all section anchors for quick lookups
        section_anchors = set()
        toc_links = []
        # Find all links that look like they are part of a ToC
        for link in soup.find_all('a', href=re.compile(r'^#\w')):
            link_text = link.get_text(strip=True).lower()
            # Heuristic for ToC links: they usually contain "item"
            if 'item' in link_text:
                 section_anchors.add(link['href'])
                 toc_links.append(link)

        def get_section_text(keywords):
            target_link = None
            for link in toc_links:
                if any(keyword in link.get_text(strip=True).lower() for keyword in keywords):
                    target_link = link
                    break
            if not target_link:
                return ""

            start_id = target_link['href'][1:]
            start_tag = soup.find(id=start_id) or soup.find('a', {'name': start_id})
            if not start_tag:
                return ""

            content = []
            for elem in start_tag.find_all_next():
                # Stop if we hit another section
                if elem.name == 'a' and elem.has_attr('href') and elem['href'] in section_anchors and elem['href'] != target_link['href']:
                    break
                if elem.name == 'a' and elem.has_attr('name') and '#' + elem['name'] in section_anchors and '#' + elem['name'] != target_link['href']:
                    break
                
                # Heuristic to stop at document end markers
                if elem.name == 'hr' and len(content) > 100:
                    break

                # Get text from non-script and non-style tags
                if elem.name not in ['script', 'style']:
                    text = elem.get_text(strip=True)
                    if text:
                        content.append(text)
            
            return " ".join(content)

        risk_text = get_section_text(['item 1a', 'risk factors'])
        mda_text = get_section_text(["item 2", "management's discussion and analysis"])

        return risk_text, mda_text

    except Exception as e:
        st.error(f"Error parsing 10-Q with BeautifulSoup: {e}")
        return "", ""
