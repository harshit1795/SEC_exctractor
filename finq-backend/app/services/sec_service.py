"""
SEC filing service
Migrated from components/sec_edgar_utils.py
"""
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# SEC EDGAR API compliance
SEC_HEADERS = {
    "User-Agent": "HarshitGola harshit.gola@gmail.com",
    "Accept-Encoding": "gzip, deflate"
}


def load_cik_ticker_map(cik_map_path: str = "../company_tickers.json") -> pd.DataFrame:
    """Loads the CIK-ticker mapping from company_tickers.json or secedgarticker.json."""
    try:
        cik_path = Path(cik_map_path)
        
        # Try multiple possible paths
        possible_paths = [
            cik_path,
            Path(__file__).parent.parent.parent.parent / cik_map_path,
            Path(__file__).parent.parent.parent.parent / "company_tickers.json",
            Path(__file__).parent.parent.parent.parent / "secedgarticker.json",
            Path("../company_tickers.json"),
            Path("../secedgarticker.json"),
        ]
        
        actual_path = None
        for path in possible_paths:
            if path.exists():
                actual_path = path
                break
        
        if not actual_path:
            logger.warning(f"CIK map not found. Tried: {possible_paths}")
            return pd.DataFrame()
        
        # Check if it's a known Zip file (even with .json extension)
        if actual_path.name == "secedgarticker.json":
            # Some environments have a Zip file here instead of JSON
            import zipfile
            if zipfile.is_zipfile(actual_path):
                logger.warning(f"Skipping {actual_path} as it is a Zip file, not JSON")
                return pd.DataFrame()

        logger.info(f"Loading CIK map from {actual_path}")
        try:
            cik_df = pd.read_json(actual_path).T
        except Exception as e:
            if 'utf-8' in str(e).lower():
                # Try with different encoding if utf-8 fails
                try:
                    cik_df = pd.read_json(actual_path, encoding='latin1').T
                except:
                    raise e
            else:
                raise e
        
        cik_df.rename(columns={'cik_str': 'cik', 'title': 'name'}, inplace=True)
        cik_df['cik'] = cik_df['cik'].astype(str).str.zfill(10)  # Ensure CIK is 10 digits
        logger.info(f"Loaded {len(cik_df)} CIK mappings")
        return cik_df
    except Exception as e:
        logger.error(f"Error loading CIK-ticker map: {e}")
        return pd.DataFrame()


def lookup_cik_online(ticker: str) -> Optional[str]:
    """
    Look up a company's CIK number directly from SEC EDGAR API.
    This serves as a fallback when the local CIK map file is unavailable.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'META', 'AAPL')
    
    Returns:
        CIK number as a zero-padded 10-digit string, or None if not found
    """
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # data is {0: {cik_str: ..., ticker: ..., title: ...}, 1: {...}, ...}
        for entry in data.values():
            if entry.get('ticker', '').upper() == ticker.upper():
                cik = str(entry.get('cik_str', ''))
                return cik.zfill(10)
        
        logger.warning(f"Ticker {ticker} not found in SEC EDGAR company_tickers.json")
        return None
    except Exception as e:
        logger.error(f"Error looking up CIK online for {ticker}: {e}")
        return None


def get_company_filings(cik: str) -> pd.DataFrame:
    """Fetches a company's recent filing history from SEC EDGAR API."""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    try:
        response = requests.get(url, headers=SEC_HEADERS)
        response.raise_for_status()
        company_filings = response.json()
        filings_df = pd.DataFrame(company_filings["filings"]["recent"])
        return filings_df
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching filing history for CIK {cik}: {e}")
        return pd.DataFrame()
    except KeyError:
        logger.error(f"Could not parse filing history for CIK {cik}. Data structure might have changed.")
        return pd.DataFrame()


def get_latest_10k_filing_info(ticker: str, cik: str, filings_df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Identifies the latest 10-K filing from the filings DataFrame."""
    if filings_df.empty:
        return None
    
    latest_10k = filings_df[filings_df['form'] == '10-K']
    if latest_10k.empty:
        return None
    
    latest_10k = latest_10k.sort_values(by='filingDate', ascending=False).iloc[0]
    
    accession_number = latest_10k['accessionNumber'].replace('-', '')
    primary_document = latest_10k['primaryDocument']
    
    doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_number}/{primary_document}"
    
    return {
        "ticker": ticker,
        "cik": cik,
        "accessionNumber": latest_10k['accessionNumber'],
        "filingDate": latest_10k['filingDate'],
        "primaryDocument": latest_10k['primaryDocument'],
        "doc_url": doc_url
    }


def get_latest_10q_filing_info(ticker: str, cik: str, filings_df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Identifies the latest 10-Q filing from the filings DataFrame."""
    if filings_df.empty:
        return None
    
    latest_10q = filings_df[filings_df['form'] == '10-Q']
    if latest_10q.empty:
        return None
    
    latest_10q = latest_10q.sort_values(by='filingDate', ascending=False).iloc[0]
    
    accession_number = latest_10q['accessionNumber'].replace('-', '')
    primary_document = latest_10q['primaryDocument']
    
    doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_number}/{primary_document}"
    
    return {
        "ticker": ticker,
        "cik": cik,
        "accessionNumber": latest_10q['accessionNumber'],
        "filingDate": latest_10q['filingDate'],
        "primaryDocument": latest_10q['primaryDocument'],
        "doc_url": doc_url
    }


def download_filing_html(doc_url: str) -> Optional[str]:
    """Downloads the HTML content of a filing."""
    try:
        response = requests.get(doc_url, headers=SEC_HEADERS)
        response.raise_for_status()
        return response.content.decode("utf-8")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading filing HTML from {doc_url}: {e}")
        return None


def parse_10k_sections(html_content: str) -> tuple:
    """Parses 10-K HTML content to extract specific sections."""
    if not html_content:
        return "", "", ""

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Strategy 1: Find all anchor links (more flexible pattern)
        section_anchors = set()
        toc_links = []
        
        # Try multiple anchor patterns
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            link_text = link.get_text(strip=True).lower()
            
            # Match anchors: #something, #item1, #i1, etc.
            if href.startswith('#') and len(href) > 1:
                if 'item' in link_text or any(keyword in link_text for keyword in ['business', 'risk', 'mda', 'management']):
                    section_anchors.add(href)
                    toc_links.append(link)
        
        # Strategy 2: Also look for headings with IDs or names
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div'], 
                                string=re.compile(r'item\s*1[^a-z]|business', re.I))
        for heading in headings:
            parent = heading.find_parent()
            if parent:
                heading_id = parent.get('id') or heading.get('id')
                if heading_id:
                    section_anchors.add(f'#{heading_id}')

        def get_section_text(keywords):
            """Extract section text using multiple strategies."""
            target_link = None
            
            # Strategy 1: Find link in TOC
            for link in toc_links:
                link_text = link.get_text(strip=True).lower()
                if any(keyword in link_text for keyword in keywords):
                    target_link = link
                    break
            
            # Strategy 2: If no TOC link, search for headings directly
            if not target_link:
                for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span', 'b', 'strong']):
                    heading_text = heading.get_text(strip=True).lower()
                    if any(keyword in heading_text for keyword in keywords) and len(heading_text) < 100:
                        # Found a heading, use it as start point
                        start_tag = heading
                        content = []
                        for elem in start_tag.find_all_next():
                            # Stop at next major section
                            if elem.name in ['h1', 'h2', 'h3']:
                                next_text = elem.get_text(strip=True).lower()
                                if any(stop_word in next_text for stop_word in ['item 1a', 'item 2', 'item 3', 'item 4', 'item 5', 'item 6', 'item 7', 'item 8']):
                                    if any(keyword not in next_text for keyword in keywords):
                                        break
                            
                            if elem.name == 'a' and elem.has_attr('href') and elem['href'].startswith('#') and len(content) > 50:
                                # Check if this is a different major section
                                link_text = elem.get_text(strip=True).lower()
                                if any(stop_word in link_text for stop_word in ['item 1a', 'item 2', 'item 3', 'item 4', 'item 5', 'item 6', 'item 7', 'item 8']):
                                    if any(keyword not in link_text for keyword in keywords):
                                        break
                            
                            if elem.name == 'hr' and len(content) > 100:
                                break

                            if elem.name not in ['script', 'style', 'noscript']:
                                text = elem.get_text(strip=True)
                                if text and len(text) > 3:  # Filter out very short text
                                    content.append(text)
                        
                        result = " ".join(content)
                        if len(result) > 100:  # Only return if we got substantial content
                            return result
                        break
            
            if not target_link:
                return ""

            # Extract anchor ID from href
            start_id = target_link['href'][1:] if target_link['href'].startswith('#') else target_link['href']
            
            # Try multiple ways to find the start tag
            start_tag = (soup.find(id=start_id) or 
                        soup.find('a', {'name': start_id}) or
                        soup.find('a', {'id': start_id}) or
                        soup.find(id=start_id.replace('-', '_')) or
                        soup.find('a', {'name': start_id.replace('-', '_')}))
            
            # If still not found, try to find by text content near the link
            if not start_tag:
                # Look for the link's parent or nearby elements
                parent = target_link.find_parent(['div', 'p', 'td', 'th', 'li'])
                if parent:
                    start_tag = parent
                else:
                    # Last resort: find text matching the section
                    for elem in soup.find_all(['p', 'div', 'span', 'b', 'strong']):
                        text = elem.get_text(strip=True).lower()
                        if any(keyword in text for keyword in keywords) and len(text) < 200:
                            start_tag = elem
                            break
            
            if not start_tag:
                logger.warning(f"Could not find start tag for section with keywords: {keywords}")
                return ""

            content = []
            section_anchors_lower = {a.lower() for a in section_anchors}
            
            for elem in start_tag.find_all_next():
                # Stop conditions
                if elem.name == 'a' and elem.has_attr('href'):
                    href = elem['href']
                    if href.startswith('#') and href.lower() in section_anchors_lower:
                        if href != target_link['href']:
                            # Check if this is a different major section
                            link_text = elem.get_text(strip=True).lower()
                            if any(stop_word in link_text for stop_word in ['item 1a', 'item 2', 'item 3', 'item 4', 'item 5', 'item 6', 'item 7', 'item 8']):
                                if any(keyword not in link_text for keyword in keywords):
                                    break
                
                if elem.name == 'a' and elem.has_attr('name'):
                    name = '#' + elem['name']
                    if name.lower() in section_anchors_lower and name != target_link['href']:
                        link_text = elem.get_text(strip=True).lower()
                        if any(stop_word in link_text for stop_word in ['item 1a', 'item 2', 'item 3', 'item 4', 'item 5', 'item 6', 'item 7', 'item 8']):
                            if any(keyword not in link_text for keyword in keywords):
                                break
                
                # Stop at horizontal rules if we have enough content
                if elem.name == 'hr' and len(content) > 100:
                    break
                
                # Stop at next major heading if it's a different section
                if elem.name in ['h1', 'h2', 'h3']:
                    heading_text = elem.get_text(strip=True).lower()
                    if any(stop_word in heading_text for stop_word in ['item 1a', 'item 2', 'item 3', 'item 4', 'item 5', 'item 6', 'item 7', 'item 8']):
                        if any(keyword not in heading_text for keyword in keywords):
                            break

                if elem.name not in ['script', 'style', 'noscript', 'meta', 'link']:
                    text = elem.get_text(strip=True)
                    # Filter out very short or likely navigation text
                    if text and len(text) > 3 and not text.startswith('Table of Contents'):
                        content.append(text)
            
            result = " ".join(content)
            # Clean up: remove excessive whitespace
            result = re.sub(r'\s+', ' ', result).strip()
            return result

        business_text = get_section_text(['item 1', 'business'])
        risk_text = get_section_text(['item 1a', 'risk factors', 'item 1 a'])
        mda_text = get_section_text(["item 7", "management's discussion and analysis", "mda", "management discussion"])

        # Log results for debugging
        if not business_text and not risk_text and not mda_text:
            logger.warning("No sections extracted. HTML structure may be different than expected.")
        else:
            logger.info(f"Extracted sections - Business: {len(business_text)} chars, Risk: {len(risk_text)} chars, MDA: {len(mda_text)} chars")

        return business_text, risk_text, mda_text

    except Exception as e:
        logger.error(f"Error parsing 10-K with BeautifulSoup: {e}", exc_info=True)
        return "", "", ""


def parse_10q_sections(html_content: str) -> tuple:
    """Parses 10-Q HTML content to extract specific sections using robust strategies."""
    if not html_content:
        return "", ""

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Strategy 1: Find all potential section anchors
        section_anchors = set()
        toc_links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            link_text = link.get_text(strip=True).lower()
            
            if href.startswith('#') and len(href) > 1:
                # 10-Q specific keywords: Management's Discussion, Risk Factors, Item 2, Item 1A
                if any(keyword in link_text for keyword in ['item 2', 'item 1a', 'management', 'risk factors']):
                    section_anchors.add(href)
                    toc_links.append(link)

        def get_section_text(keywords, stop_keywords):
            """Extract section text using multiple strategies adapted for 10-Q."""
            target_link = None
            
            # Strategy 1: Find link in TOC
            for link in toc_links:
                link_text = link.get_text(strip=True).lower()
                if any(keyword in link_text for keyword in keywords):
                    target_link = link
                    break
            
            # Strategy 2: If no TOC link, search for headings directly
            if not target_link:
                for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span', 'b', 'strong']):
                    heading_text = heading.get_text(strip=True).lower()
                    if any(keyword in heading_text for keyword in keywords) and len(heading_text) < 150:
                        # Found a heading, use it as start point
                        start_tag = heading
                        content = []
                        for elem in start_tag.find_all_next():
                            # Stop at next major section
                            if elem.name in ['h1', 'h2', 'h3', 'p', 'div']:
                                next_text = elem.get_text(strip=True).lower()
                                if any(stop_word in next_text for stop_word in stop_keywords):
                                    # Ensure it's a real item heading and not a reference back to TOC
                                    if len(next_text) < 100:
                                        break
                            
                            if elem.name == 'hr' and len(content) > 100:
                                break

                            if elem.name not in ['script', 'style', 'noscript', 'meta', 'link']:
                                text = elem.get_text(strip=True)
                                if text and len(text) > 3:
                                    content.append(text)
                        
                        result = " ".join(content)
                        result = re.sub(r'\s+', ' ', result).strip()
                        if len(result) > 100:
                            return result
                        break

            if not target_link:
                return ""

            # Strategy 1 Extraction Logic (Anchor based)
            start_id = target_link['href'][1:]
            start_tag = (soup.find(id=start_id) or 
                        soup.find('a', {'name': start_id}) or
                        soup.find('a', {'id': start_id}) or
                        soup.find(id=start_id.replace('-', '_')) or
                        soup.find('a', {'name': start_id.replace('-', '_')}))
            
            if not start_tag:
                parent = target_link.find_parent(['div', 'p', 'td', 'th', 'li'])
                if parent:
                    start_tag = parent

            if not start_tag:
                return ""

            content = []
            section_anchors_lower = {a.lower() for a in section_anchors}
            
            for elem in start_tag.find_all_next():
                # Stop conditions: another anchor that looks like a major section
                if elem.name == 'a' and elem.has_attr('href'):
                    href = elem['href']
                    if href.startswith('#') and href.lower() in section_anchors_lower:
                        if href != target_link['href']:
                            link_text = elem.get_text(strip=True).lower()
                            if any(stop_word in link_text for stop_word in stop_keywords):
                                break
                
                if elem.name == 'hr' and len(content) > 100:
                    break
                
                if elem.name in ['h1', 'h2', 'h3']:
                    heading_text = elem.get_text(strip=True).lower()
                    if any(stop_word in heading_text for stop_word in stop_keywords):
                        break

                if elem.name not in ['script', 'style', 'noscript', 'meta', 'link']:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 3 and not text.startswith('Table of Contents'):
                        content.append(text)
            
            result = " ".join(content)
            result = re.sub(r'\s+', ' ', result).strip()
            return result

        # 10-Q Sections:
        # MDA is Item 2 in Part I
        # Risk Factors is Item 1A in Part II (but some omit if no changes, we still try to find the heading)
        risk_keywords = ['item 1a', 'risk factors', 'item 1 a']
        risk_stop = ['item 2', 'item 3', 'item 4', 'part ii', 'signatures', 'exhibit']
        
        mda_keywords = ['item 2', "management's discussion", 'mda']
        mda_stop = ['item 3', 'item 4', 'item 1', 'part ii', 'signatures']

        risk_text = get_section_text(risk_keywords, risk_stop)
        mda_text = get_section_text(mda_keywords, mda_stop)

        if not risk_text and not mda_text:
            logger.warning("No 10-Q sections extracted. Structure may be non-standard.")
        else:
            logger.info(f"Extracted 10-Q sections - Risk: {len(risk_text)} chars, MDA: {len(mda_text)} chars")

        return risk_text, mda_text

    except Exception as e:
        logger.error(f"Error parsing 10-Q with BeautifulSoup: {e}")
        return "", ""
