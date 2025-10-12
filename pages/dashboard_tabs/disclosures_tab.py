import streamlit as st
import pandas as pd
from components.sec_edgar_utils import (
    load_cik_ticker_map,
    get_company_filings,
    get_latest_10k_filing_info,
    download_10k_html,
    parse_10k_sections
)

def render(selected_ticker):
    st.title("🏛️ Company Disclosures (10-K)")
    st.markdown("View key sections from the latest 10-K filings for selected companies.")

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

        st.subheader(f"Latest 10-K for {company_name} ({selected_ticker})")

        filings_df = get_company_filings(cik)
        if filings_df.empty:
            st.warning(f"No recent filings found for {selected_ticker}.")
            return

        latest_10k_info = get_latest_10k_filing_info(selected_ticker, cik, filings_df)
        if not latest_10k_info:
            st.warning(f"No 10-K filings found for {selected_ticker}.")
            return

        st.info(f"Latest 10-K filed on: {latest_10k_info['filingDate']} "
                f"([View on SEC.gov]({latest_10k_info['doc_url']}))")

        html_content = download_10k_html(latest_10k_info['doc_url'])
        if not html_content:
            st.error("Could not download 10-K HTML content.")
            return

        st.markdown("### Select Sections to Display")
        section_options = {
            "Business Overview (Item 1)": 1,
            "Risk Factors (Item 1A)": 2,
            "Management's Discussion & Analysis (Item 7)": 3,
        }
        selected_section_name = st.selectbox(
            "Choose a section",
            list(section_options.keys())
        )
        selected_section_code = section_options[selected_section_name]

        business_text, risk_text, mda_text = parse_10k_sections(html_content)

        if selected_section_code == 1:
            st.subheader("Business Overview (Item 1)")
            st.write(business_text if business_text else "Section not found or empty.")
        elif selected_section_code == 2:
            st.subheader("Risk Factors (Item 1A)")
            st.write(risk_text if risk_text else "Section not found or empty.")
        elif selected_section_code == 3:
            st.subheader("Management's Discussion & Analysis (Item 7)")
            st.write(mda_text if mda_text else "Section not found or empty.")

