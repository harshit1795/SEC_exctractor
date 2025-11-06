import streamlit as st
import pandas as pd
from components.sec_edgar_utils import (
    load_cik_ticker_map,
    get_company_filings,
    get_latest_10k_filing_info,
    get_latest_10q_filing_info,
    download_filing_html,
    parse_10k_sections,
    parse_10q_sections
)

def render(selected_ticker):
    st.title("🏛️ Company Disclosures (10-K & 10-Q)")
    st.markdown("View key sections from the latest 10-K and 10-Q filings for selected companies.")

    report_type = st.radio("Select Report Type", ("10-K", "10-Q"), horizontal=True)

    cik_df = load_cik_ticker_map()
    if cik_df.empty:
        st.error("Could not load CIK-ticker map. Please check the application logs.")
        return

    if selected_ticker:
        company_info = cik_df[cik_df['ticker'] == selected_ticker]
        if company_info.empty:
            st.warning(f"No CIK information found for {selected_ticker}.")
            return
        company_info = company_info.iloc[0]
        cik = company_info['cik']
        company_name = company_info['name']

        st.subheader(f"Latest {report_type} for {company_name} ({selected_ticker})")

        filings_df = get_company_filings(cik)
        if filings_df.empty:
            st.warning(f"No recent filings found for {selected_ticker}.")
            return

        if report_type == "10-K":
            latest_filing_info = get_latest_10k_filing_info(selected_ticker, cik, filings_df)
            if not latest_filing_info:
                st.warning(f"No 10-K filings found for {selected_ticker}.")
                return
        else: # 10-Q
            latest_filing_info = get_latest_10q_filing_info(selected_ticker, cik, filings_df)
            if not latest_filing_info:
                st.warning(f"No 10-Q filings found for {selected_ticker}.")
                return

        st.info(f"Latest {report_type} filed on: {latest_filing_info['filingDate']} "
                f"([View on SEC.gov]({latest_filing_info['doc_url']}))")

        html_content = download_filing_html(latest_filing_info['doc_url'])
        if not html_content:
            st.error(f"Could not download {report_type} HTML content.")
            return

        st.markdown("### Select Sections to Display")
        if report_type == "10-K":
            section_options = {
                "Business Overview (Item 1)": 1,
                "Risk Factors (Item 1A)": 2,
                "Management's Discussion & Analysis (Item 7)": 3,
            }
            business_text, risk_text, mda_text = parse_10k_sections(html_content)
        else: # 10-Q
            section_options = {
                "Risk Factors (Part II, Item 1A)": 1,
                "Management's Discussion & Analysis (Part I, Item 2)": 2,
            }
            risk_text, mda_text = parse_10q_sections(html_content)

        selected_section_name = st.selectbox(
            "Choose a section",
            list(section_options.keys())
        )
        selected_section_code = section_options[selected_section_name]

        if report_type == "10-K":
            if selected_section_code == 1:
                st.subheader("Business Overview (Item 1)")
                st.write(business_text if business_text else "Section not found or empty.")
            elif selected_section_code == 2:
                st.subheader("Risk Factors (Item 1A)")
                st.write(risk_text if risk_text else "Section not found or empty.")
            elif selected_section_code == 3:
                st.subheader("Management's Discussion & Analysis (Item 7)")
                st.write(mda_text if mda_text else "Section not found or empty.")
        else: # 10-Q
            if selected_section_code == 1:
                st.subheader("Risk Factors (Part II, Item 1A)")
                st.write(risk_text if risk_text else "Section not found or empty.")
            elif selected_section_code == 2:
                st.subheader("Management's Discussion & Analysis (Part I, Item 2)")
                st.write(mda_text if mda_text else "Section not found or empty.")

