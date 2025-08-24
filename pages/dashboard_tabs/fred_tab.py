import streamlit as st
import pandas as pd
import altair as alt
from fred_data import get_multiple_fred_series
from st_aggrid import AgGrid, GridOptionsBuilder

def render():
    st.markdown("### Macroeconomic Data")

    INDICATORS = {
        "GDP": {"id": "GDP", "freq": "q"},
        "Real GDP": {"id": "GDPC1", "freq": "q"},
        "Inflation (CPI)": {"id": "CPIAUCSL", "freq": "m"},
        "Unemployment Rate": {"id": "UNRATE", "freq": "m"},
        "10-Year Treasury Yield": {"id": "DGS10", "freq": "d"},
        "Federal Funds Rate": {"id": "FEDFUNDS", "freq": "d"},
    }

    selected_indicators = st.multiselect(
        "Select economic indicators to display:",
        options=list(INDICATORS.keys()),
        default=["Real GDP", "Inflation (CPI)", "Unemployment Rate"]
    )

    if selected_indicators:
        series_info_to_fetch = {INDICATORS[key]["id"]: INDICATORS[key]["freq"] for key in selected_indicators}
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            start = st.date_input("Start date", pd.to_datetime("today") - pd.DateOffset(years=10), key="fred_start")
        with c2:
            end = st.date_input("End date", pd.to_datetime("today"), key="fred_end")
        with c3:
            aggregation_period = st.selectbox(
                "Aggregation Period:",
                options=['Monthly', 'Quarterly', 'Yearly'],
                index=0,
                key="fred_agg_period"
            )
        with c4:
            chart_type = st.radio("Chart Type:", ["Line", "Bar"], key="fred_chart_type")

        # Fetch raw data
        fred_df = get_multiple_fred_series(series_info_to_fetch, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        
        if not fred_df.empty:
            # --- AGGREGATION LOGIC ---
            period_map = {
                'Monthly': 'M',
                'Quarterly': 'Q',
                'Yearly': 'A'
            }
            resample_freq = period_map.get(aggregation_period)
            
            # Resample and aggregate. Using mean() is generally better for rates/indices.
            agg_df = fred_df.resample(resample_freq).mean(numeric_only=True)
            # --- END AGGREGATION LOGIC ---

            st.subheader(f"Aggregated Data ({aggregation_period})")
            
            # Prepare data for display
            display_df = agg_df.reset_index()
            display_df.rename(columns={'Date': 'period'}, inplace=True)
            
            # Format the period column for readability
            if resample_freq == 'M':
                display_df['period'] = display_df['period'].dt.strftime('%Y-%m')
            elif resample_freq == 'Q':
                display_df['period'] = display_df['period'].dt.to_period('Q').astype(str)
            elif resample_freq == 'A':
                display_df['period'] = display_df['period'].dt.strftime('%Y')

            # --- INTERACTIVE TABLE ---
            with st.container(border=True):
                gb = GridOptionsBuilder.from_dataframe(display_df)
                gb.configure_pagination(paginationAutoPageSize=True)
                gb.configure_column("period", headerName="Period", pinned='left')
                metric_columns = [col for col in display_df.columns if col != 'period']
                for col in metric_columns:
                    gb.configure_column(col, type=["numericColumn", "numberColumnFilter", "customNumericFormat"], editable=False)
                gridOptions = gb.build()

                AgGrid(
                    display_df,
                    gridOptions=gridOptions,
                    enable_enterprise_modules=False,
                    height=350,
                    width='100%',
                    reload_data=True,
                    theme='streamlit'
                )

            # --- DOWNLOAD BUTTON ---
            st.download_button(
                label="Download Aggregated Data as CSV",
                data=display_df.to_csv(index=False).encode('utf-8'),
                file_name=f"fred_data_{aggregation_period.lower()}.csv",
                mime="text/csv",
            )

            # --- CHARTS ---
            st.subheader("Aggregated Charts")
            for col in agg_df.columns:
                series_data = agg_df[col].dropna()
                if not series_data.empty:
                    user_friendly_name = next((key for key, value in INDICATORS.items() if value["id"] == col), col)
                    
                    # Prepare data for Altair
                    chart_df = series_data.reset_index()
                    chart_df.columns = ['Date', 'Value']

                    # --- Manually format the date label to prevent repetition ---
                    if aggregation_period == 'Yearly':
                        chart_df['Label'] = chart_df['Date'].dt.strftime('%Y')
                        x_title = 'Year'
                    elif aggregation_period == 'Quarterly':
                        chart_df['Label'] = chart_df['Date'].dt.to_period('Q').astype(str)
                        x_title = 'Quarter'
                    else: # Monthly
                        chart_df['Label'] = chart_df['Date'].dt.strftime('%b %Y')
                        x_title = 'Month'
                    
                    x_axis = alt.X('Label:O', title=x_title, sort=None) # Use formatted label, disable sorting

                    # Base chart
                    base = alt.Chart(chart_df).encode(
                        x=x_axis,
                        y=alt.Y('Value', title=user_friendly_name),
                        tooltip=['Label', 'Value'] # Add tooltip for clarity
                    ).properties(
                        title=f"{user_friendly_name}"
                    )

                    # Select mark based on user input
                    if chart_type == "Line":
                        chart = base.mark_line().interactive()
                    elif chart_type == "Bar":
                        chart = base.mark_bar().interactive()
                    
                    st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("No data returned for the selected criteria.")