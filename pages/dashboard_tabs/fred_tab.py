import streamlit as st
import pandas as pd
from fred_data import get_multiple_fred_series
from st_aggrid import AgGrid, GridOptionsBuilder
from .charting_utils import render_filter_bar, render_altair_chart

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
        
        # Fetch raw data first to determine date range for filters
        fred_df = get_multiple_fred_series(series_info_to_fetch, "2000-01-01", pd.to_datetime("today").strftime('%Y-%m-%d'))
        
        if not fred_df.empty:
            # --- RENDER FILTERS ---
            agg_options = ['Monthly', 'Quarterly', 'Yearly']
            chart_type_options = ["Line", "Bar"]
            start_date, end_date, aggregation_period, chart_type, chart_view = render_filter_bar(fred_df, "fred", agg_options, chart_type_options, default_agg_index=1)

            # --- PROCESS DATA ---
            filtered_df = fred_df[(fred_df.index >= pd.to_datetime(start_date, utc=True)) & (fred_df.index <= pd.to_datetime(end_date, utc=True))]
            
            period_map = {'Monthly': 'M', 'Quarterly': 'Q', 'Yearly': 'A'}
            agg_df = filtered_df.resample(period_map[aggregation_period]).mean(numeric_only=True)

            if not agg_df.empty:
                st.subheader(f"Aggregated Data ({aggregation_period})")
                
                # --- DISPLAY TABLE ---
                display_df = agg_df.reset_index()
                display_df.rename(columns={'Date': 'period'}, inplace=True)
                # Additional formatting for display can be done here if needed
                with st.container(border=True):
                    gb = GridOptionsBuilder.from_dataframe(display_df)
                    gb.configure_pagination(paginationAutoPageSize=True)
                    gb.configure_column("period", headerName="Period", pinned='left')
                    metric_columns = [col for col in display_df.columns if col != 'period']
                    for col in metric_columns:
                        gb.configure_column(col, type=["numericColumn", "numberColumnFilter", "customNumericFormat"], editable=False)
                    gridOptions = gb.build()
                    AgGrid(display_df, gridOptions=gridOptions, height=350, width='100%', theme='streamlit')

                # --- RENDER CHART ---
                st.subheader("Aggregated Chart")
                st.button("💡 Tips", help="* To Zoom: Place your mouse over the chart and use your mouse wheel to scroll.\n* To Pan: Click and drag the chart to move it up, down, left, or right.\n* To Reset: Double-click on the chart to return to the default view.", disabled=True)
                melted_df = agg_df.reset_index().melt(id_vars='Date', var_name='Metric', value_name='Value')
                render_altair_chart(
                    df=melted_df,
                    aggregation_period=aggregation_period,
                    chart_type=chart_type,
                    chart_view=chart_view,
                    x_col='Date',
                    y_col='Value',
                    color_col='Metric',
                    chart_title="Macroeconomic Trends"
                )
            else:
                st.warning("No data available for the selected filters.")
        else:
            st.warning("No data returned for the selected criteria.")
