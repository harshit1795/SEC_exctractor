import streamlit as st
import pandas as pd
from fred_data import get_multiple_fred_series
from st_aggrid import AgGrid, GridOptionsBuilder
from .charting_utils import render_altair_chart
from auth import _load_user_prefs, _save_user_prefs

INDICATORS = {
    "GDP": {"id": "GDP", "freq": "q"},
    "Real GDP": {"id": "GDPC1", "freq": "q"},
    "Inflation (CPI)": {"id": "CPIAUCSL", "freq": "m"},
    "Unemployment Rate": {"id": "UNRATE", "freq": "m"},
    "10-Year Treasury Yield": {"id": "DGS10", "freq": "d"},
    "Federal Funds Rate": {"id": "FEDFUNDS", "freq": "d"},
}

def render_filters():
    st.markdown("#### Macroeconomic Options")
    user_prefs = st.session_state.get("user_prefs", {})
    fred_prefs = user_prefs.get("fred_tab", {})

    default_indicators = fred_prefs.get("selected_indicators", ["Real GDP", "Inflation (CPI)", "Unemployment Rate"])
    selected_indicators = st.multiselect(
        "Select economic indicators:",
        options=list(INDICATORS.keys()),
        default=default_indicators
    )

    filters = {"selected_indicators": selected_indicators}

    if selected_indicators:
        series_info_to_fetch = {INDICATORS[key]["id"]: INDICATORS[key]["freq"] for key in selected_indicators}
        fred_df = get_multiple_fred_series(series_info_to_fetch, "2000-01-01", pd.to_datetime("today").strftime('%Y-%m-%d'))
        filters["fred_df"] = fred_df

        if not fred_df.empty:
            agg_options = ['Monthly', 'Quarterly', 'Yearly']
            default_agg = fred_prefs.get("aggregation_period", "Quarterly")
            agg_index = agg_options.index(default_agg) if default_agg in agg_options else 1
            filters["aggregation_period"] = st.selectbox("Aggregation Period:", options=agg_options, index=agg_index, key="fred_agg_period")

            chart_type_options = ["Line", "Bar"]
            default_chart_type = fred_prefs.get("chart_type", "Line")
            chart_type_index = chart_type_options.index(default_chart_type) if default_chart_type in chart_type_options else 0
            filters["chart_type"] = st.radio("Chart Type:", chart_type_options, index=chart_type_index, key="fred_chart_type", horizontal=True)

            chart_view_options = ["Combined", "Individual"]
            default_chart_view = fred_prefs.get("chart_view", "Combined")
            chart_view_index = chart_view_options.index(default_chart_view) if default_chart_view in chart_view_options else 0
            filters["chart_view"] = st.radio("Chart View:", chart_view_options, index=chart_view_index, key="fred_view_type", horizontal=True)

            min_date = fred_df.index.min().date()
            max_date = fred_df.index.max().date()

            filters["start_date"] = st.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date, key="fred_start")
            filters["end_date"] = st.date_input("End date", value=max_date, min_value=min_date, max_value=max_date, key="fred_end")

            if st.button("Save Macro Settings", key="save_fred_prefs"):
                all_prefs = _load_user_prefs()
                user = st.session_state.get("user")
                if user:
                    user_prefs = all_prefs.setdefault(user, {})
                    user_prefs["fred_tab"] = {
                        "selected_indicators": selected_indicators,
                        "aggregation_period": filters["aggregation_period"],
                        "chart_type": filters["chart_type"],
                        "chart_view": filters["chart_view"],
                        "start_date": filters["start_date"].isoformat(),
                        "end_date": filters["end_date"].isoformat()
                    }
                    _save_user_prefs(all_prefs)
                    st.session_state.user_prefs = user_prefs
                    st.success("Macro preferences saved!")

    return filters

def render(filters):
    st.markdown("### Macroeconomic Data")

    if not filters.get("selected_indicators"):
        st.info("Select one or more economic indicators from the sidebar to begin.")
        return

    fred_df = filters.get("fred_df")
    if fred_df is None or fred_df.empty:
        st.warning("No data returned for the selected criteria.")
        return

    start_date = filters["start_date"]
    end_date = filters["end_date"]
    aggregation_period = filters["aggregation_period"]
    chart_type = filters["chart_type"]
    chart_view = filters["chart_view"]

    filtered_df = fred_df[(fred_df.index >= pd.to_datetime(start_date, utc=True)) & (fred_df.index <= pd.to_datetime(end_date, utc=True))]
    
    period_map = {'Monthly': 'M', 'Quarterly': 'Q', 'Yearly': 'A'}
    agg_df = filtered_df.resample(period_map[aggregation_period]).mean(numeric_only=True)

    if not agg_df.empty:
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

        st.subheader(f"Aggregated Data ({aggregation_period})")
        
        display_df = agg_df.reset_index()
        display_df.rename(columns={'Date': 'period'}, inplace=True)
        with st.container(border=True):
            gb = GridOptionsBuilder.from_dataframe(display_df)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_column("period", headerName="Period", pinned='left')
            metric_columns = [col for col in display_df.columns if col != 'period']
            for col in metric_columns:
                gb.configure_column(col, type=["numericColumn", "numberColumnFilter", "customNumericFormat"], editable=False)
            gridOptions = gb.build()
            AgGrid(display_df, gridOptions=gridOptions, height=350, width='100%', theme='streamlit')
    else:
        st.warning("No data available for the selected filters.")