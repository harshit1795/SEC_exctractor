import pandas as pd
from fredapi import Fred
import streamlit as st
import os
from st_aggrid import AgGrid, GridOptionsBuilder

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_fred_api_key():
    """Retrieve FRED API key from environment variables or Streamlit secrets."""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        api_key = st.secrets.get("FRED_API_KEY")
    if not api_key:
        st.error("FRED API key not found. Please set it in your environment variables or Streamlit secrets.")
        st.stop()
    return api_key

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_fred_series(series_id: str, start_date: str, end_date: str, frequency: str = None) -> pd.Series:
    """Fetch a single FRED series with optional frequency."""
    api_key = get_fred_api_key()
    fred = Fred(api_key=api_key)
    try:
        data = fred.get_series(series_id, observation_start=start_date, observation_end=end_date, frequency=frequency)
        if data is None or data.empty:
            st.warning(f"No data found for FRED series: {series_id}")
            return pd.Series()
        return data
    except Exception as e:
        st.error(f"Error fetching FRED series {series_id}: {e}")
        return pd.Series()

@st.cache_data(ttl=3600)
def get_multiple_fred_series(series_info: dict, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch multiple FRED series with specified frequencies and combine into a DataFrame."""
    all_data = {}
    for series_id, freq in series_info.items():
        data = get_fred_series(series_id, start_date, end_date, frequency=freq)
        if not data.empty:
            all_data[series_id] = data
    
    if not all_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(all_data)
    df.index.name = 'Date'
    df.index = df.index.tz_localize('UTC')
    return df

# Example usage (for testing purposes, not part of the main app flow)
if __name__ == "__main__":
    st.title("FRED Economic Data Viewer")

    INDICATORS = {
        "GDP": {"id": "GDP", "freq": "q"},
        "Real GDP": {"id": "GDPC1", "freq": "q"},
        "Inflation (CPI)": {"id": "CPIAUCSL", "freq": "m"},
        "Unemployment Rate": {"id": "UNRATE", "freq": "m"},
        "10-Year Treasury Yield": {"id": "DGS10", "freq": "d"},
        "Federal Funds Rate": {"id": "FEDFUNDS", "freq": "d"},
    }

    selected_indicators_keys = st.multiselect(
        "Select economic indicators to display:",
        options=list(INDICATORS.keys()),
        default=["Real GDP", "Inflation (CPI)", "Unemployment Rate"]
    )

    if selected_indicators_keys:
        series_info_to_fetch = {INDICATORS[key]["id"]: INDICATORS[key]["freq"] for key in selected_indicators_keys}
        
        c1, c2, c3 = st.columns(3)
        with c1:
            start = st.date_input("Start date", pd.to_datetime("today") - pd.DateOffset(years=10))
        with c2:
            end = st.date_input("End date", pd.to_datetime("today"))
        with c3:
            aggregation_period = st.selectbox(
                "Aggregation Period:",
                options=['Monthly', 'Quarterly', 'Yearly'],
                index=0 # Default to Monthly
            )

        fred_df = get_multiple_fred_series(series_info_to_fetch, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        
        if not fred_df.empty:
            
            # --- RESAMPLING LOGIC ---
            period_map = {
                'Monthly': 'M',
                'Quarterly': 'Q',
                'Yearly': 'A'
            }
            resample_freq = period_map.get(aggregation_period)
            
            # Resample and aggregate. Using sum() as requested by user.
            agg_df = fred_df.resample(resample_freq).sum()
            # --- END RESAMPLING LOGIC ---

            st.subheader(f"Aggregated Data ({aggregation_period})")
            
            # Prepare data for display
            display_df = agg_df.reset_index()
            display_df.rename(columns={'Date': 'period'}, inplace=True)
            
            # Format the period column to be more readable
            if resample_freq == 'M':
                display_df['period'] = display_df['period'].dt.strftime('%Y-%m')
            elif resample_freq == 'Q':
                display_df['period'] = display_df['period'].dt.to_period('Q').astype(str)
            elif resample_freq == 'A':
                display_df['period'] = display_df['period'].dt.strftime('%Y')


            # Display static dataframe
            st.dataframe(display_df)

            st.subheader("Interactive Aggregated Table")
            # Configure AgGrid
            gb = GridOptionsBuilder.from_dataframe(display_df)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_column("period", headerName="Period", pinned='left')
            metric_columns = [col for col in display_df.columns if col != 'period']
            for col in metric_columns:
                gb.configure_column(col, type=["numericColumn", "numberColumnFilter", "customNumericFormat"], aggFunc='sum', editable=False)
            gridOptions = gb.build()

            AgGrid(
                display_df,
                gridOptions=gridOptions,
                enable_enterprise_modules=False,
                height=600,
                width='100%',
                reload_data=True,
                allow_unsafe_jscode=True,
                theme='streamlit'
            )

            st.subheader("Aggregated Charts")
            for col in agg_df.columns:
                # Find the user-friendly name for the current series_id
                user_friendly_name = "N/A"
                for key, value in INDICATORS.items():
                    if value["id"] == col:
                        user_friendly_name = key
                        break
                
                st.markdown(f"**{user_friendly_name}** ({col})")
                st.line_chart(agg_df[col].dropna(), use_container_width=True)

        else:
            st.warning("No data returned. Please check the series IDs and date range.")
