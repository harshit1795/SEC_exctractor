
import streamlit as st
import pandas as pd
from fred_data import get_multiple_fred_series

def render():
    st.markdown("### Macroeconomic Data")

    INDICATORS = {
        "GDP": "GDP",
        "Real GDP": "GDPC1",
        "Inflation (CPI)": "CPIAUCSL",
        "Unemployment Rate": "UNRATE",
        "10-Year Treasury Yield": "DGS10",
        "Federal Funds Rate": "FEDFUNDS",
    }

    selected_indicators = st.multiselect(
        "Select economic indicators to display:",
        options=list(INDICATORS.keys()),
        default=["Real GDP", "Inflation (CPI)", "Unemployment Rate"]
    )

    if selected_indicators:
        series_to_fetch = [INDICATORS[key] for key in selected_indicators]
        
        today = pd.to_datetime("today")
        start = st.date_input("Start date", today - pd.DateOffset(years=10), key="fred_start")
        end = st.date_input("End date", today, key="fred_end")

        if st.button("Fetch FRED Data"):
            fred_df = get_multiple_fred_series(series_to_fetch, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
            
            if not fred_df.empty:
                st.subheader("Data Preview")
                st.dataframe(fred_df.head())

                st.subheader("Charts")
                for col in fred_df.columns:
                    st.line_chart(fred_df[col].dropna(), use_container_width=True)
                    st.markdown(f"**{col}** - {selected_indicators[series_to_fetch.index(col)]}")
            else:
                st.warning("No data returned. Please check the series IDs and date range.")
