import pandas as pd
from fredapi import Fred
import streamlit as st
import os

# It's recommended to store your API key securely, e.g., in Streamlit secrets
# For this example, we'll assume it's set as an environment variable.
FRED_API_KEY = os.environ.get("FRED_API_KEY", "YOUR_DEFAULT_API_KEY")

@st.cache_data(ttl=3600)  # Cache data for 1 hour
def get_fred_series(series_id: str, start_date: str, end_date: str) -> pd.Series:
    """Fetch a single data series from FRED."""
    try:
        fred = Fred(api_key=FRED_API_KEY)
        series = fred.get_series(series_id, start_time=start_date, end_time=end_date)
        return series
    except Exception as e:
        st.error(f"Failed to fetch FRED data for {series_id}: {e}")
        return pd.Series(dtype=float)

@st.cache_data(ttl=3600)
def get_multiple_fred_series(series_ids: list[str], start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch multiple data series from FRED and return as a DataFrame."""
    data = {}
    for series_id in series_ids:
        data[series_id] = get_fred_series(series_id, start_date, end_date)
    return pd.DataFrame(data)

# Example usage:
if __name__ == "__main__":
    st.title("FRED Economic Data Viewer")

    # Define some key economic indicators
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
        
        # Date range selection
        today = pd.to_datetime("today")
        start = st.date_input("Start date", today - pd.DateOffset(years=10))
        end = st.date_input("End date", today)

        if st.button("Fetch Data"):
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