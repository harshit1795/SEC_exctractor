import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import yfinance as yf
from auth import _load_user_prefs, _save_user_prefs

@st.cache_data(show_spinner=False)
def get_ticker_earnings_data(ticker_symbol):
    ticker_yf = yf.Ticker(ticker_symbol)
    return ticker_yf.earnings_dates, ticker_yf.info

def render_filters(earnings_dates):
    st.markdown("#### Chart Options")
    user_prefs = st.session_state.get("user_prefs", {})
    earnings_prefs = user_prefs.get("earnings_tab", {})

    df_for_filters = earnings_dates.set_index('Date')
    
    start_date = st.date_input("Start date", df_for_filters.index.min(), key="earnings_start")
    end_date = st.date_input("End date", df_for_filters.index.max(), key="earnings_end")
    
    agg_options = ['Quarterly', 'Yearly']
    default_agg = earnings_prefs.get("aggregation_period", "Quarterly")
    agg_index = agg_options.index(default_agg) if default_agg in agg_options else 0
    aggregation_period = st.selectbox("Aggregation Period:", agg_options, index=agg_index, key="earnings_agg_period")

    chart_type_options = ["Line", "Bar"]
    default_chart_type = earnings_prefs.get("chart_type", "Line")
    chart_type_index = chart_type_options.index(default_chart_type) if default_chart_type in chart_type_options else 0
    chart_type = st.radio("Chart Type:", chart_type_options, index=chart_type_index, key="earnings_chart_type", horizontal=True)

    chart_view_options = ["Combined", "Individual"]
    default_chart_view = earnings_prefs.get("chart_view", "Combined")
    chart_view_index = chart_view_options.index(default_chart_view) if default_chart_view in chart_view_options else 0
    chart_view = st.radio("Chart View:", chart_view_options, index=chart_view_index, key="earnings_view_type", horizontal=True)
    
    if st.button("Save Chart Settings", key="save_earnings_prefs"):
        all_prefs = _load_user_prefs()
        user = st.session_state.get("user")
        if user:
            user_prefs = all_prefs.setdefault(user, {})
            user_prefs["earnings_tab"] = {
                "aggregation_period": aggregation_period,
                "chart_type": chart_type,
                "chart_view": chart_view
            }
            _save_user_prefs(all_prefs)
            st.session_state.user_prefs = user_prefs
            st.success("Earnings chart preferences saved!")

    return {
        "start_date": start_date, 
        "end_date": end_date, 
        "aggregation_period": aggregation_period, 
        "chart_type": chart_type, 
        "chart_view": chart_view
    }

def render(selected_ticker, filters):
    st.markdown("### Earning Summary")

    earnings_dates, ticker_info_yf = get_ticker_earnings_data(selected_ticker)

    st.subheader("Historical EPS Trend")
    st.button("💡 Tips", help="* To Zoom: Place your mouse over the chart and use your mouse wheel to scroll.\n* To Pan: Click and drag the chart to move it up, down, left, or right.\n* To Reset: Double-click on the chart to return to the default view.", disabled=True)
    
    if not earnings_dates.empty:
        historical_eps_df = earnings_dates[
            (earnings_dates['Event Type'] == 'Earnings') &
            (earnings_dates['Reported EPS'].notna()) &
            (earnings_dates['EPS Estimate'].notna())
        ].reset_index().rename(columns={'Earnings Date': 'Date'})

        if not historical_eps_df.empty and filters:
            start_date = filters['start_date']
            end_date = filters['end_date']
            aggregation_period = filters['aggregation_period']
            chart_type = filters['chart_type']
            chart_view = filters['chart_view']

            mask = (historical_eps_df['Date'] >= pd.to_datetime(start_date, utc=True)) & (historical_eps_df['Date'] <= pd.to_datetime(end_date, utc=True))
            filtered_df = historical_eps_df.loc[mask]

            processing_df = filtered_df.set_index('Date')

            if aggregation_period == 'Yearly':
                agg_df = processing_df.resample('A').sum(numeric_only=True)
            else: # Quarterly
                agg_df = processing_df
            
            agg_df = agg_df.reset_index()

            if not agg_df.empty:
                if chart_view == 'Combined':
                    melted_df = agg_df.melt(
                        id_vars=['Date'], 
                        value_vars=['Reported EPS', 'EPS Estimate'], 
                        var_name='EPS Type', 
                        value_name='EPS Value'
                    )
                    if aggregation_period == 'Yearly':
                        x_axis = alt.X('Date:O', timeUnit='year', title='Year', axis=alt.Axis(labelAngle=0))
                    else: # Quarterly
                        x_axis = alt.X('Date:O', timeUnit='yearquarter', title='Quarter')

                    base = alt.Chart(melted_df).encode(
                        x=x_axis,
                        y=alt.Y('EPS Value', title='EPS'),
                        color='EPS Type:N',
                        tooltip=['Date', 'EPS Type', 'EPS Value']
                    )

                    if chart_type == "Line":
                        chart = base.mark_line(point=True).interactive()
                    else: # Bar
                        chart = base.mark_bar().encode(xOffset='EPS Type:N').interactive()

                    st.altair_chart(chart.properties(title=f'{selected_ticker} Historical EPS Trend'), use_container_width=True)
                
                else: # Individual View
                    for metric in ['Reported EPS', 'EPS Estimate']:
                        chart_df = agg_df[['Date', metric]].copy()
                        chart_df.rename(columns={metric: 'Value'}, inplace=True)
                        
                        if aggregation_period == 'Yearly':
                            chart_df['Label'] = chart_df['Date'].dt.strftime('%Y')
                            x_title = 'Year'
                        else: # Quarterly
                            chart_df['Label'] = chart_df['Date'].dt.to_period('Q').astype(str)
                            x_title = 'Quarter'
                        
                        x_axis = alt.X('Label:O', title=x_title, sort=None)

                        base = alt.Chart(chart_df).encode(
                            x=x_axis,
                            y=alt.Y('Value', title=metric, scale=alt.Scale(zero=False)),
                            tooltip=['Label', 'Value']
                        ).properties(
                            title=f'{selected_ticker} - {metric}'
                        )

                        if chart_type == "Line":
                            chart = base.mark_line(point=True).interactive()
                        else: # Bar
                            chart = base.mark_bar().interactive()
                        st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No data available for the selected filters.")
        else:
            st.info("No sufficient historical EPS data available for charting.")

    if not earnings_dates.empty:
        earnings_dates.index = pd.to_datetime(earnings_dates.index)
        
        st.subheader("Last Quarter's Earnings")
        past_earnings = earnings_dates[
            (earnings_dates.index < pd.Timestamp.now(tz='America/New_York')) &
            (earnings_dates['Event Type'] == 'Earnings') &
            (earnings_dates['Reported EPS'].notna())
        ].sort_index(ascending=False)
        
        if not past_earnings.empty:
            last_earnings = past_earnings.iloc[0]
            st.write(f"**Date:** {last_earnings.name.strftime('%Y-%m-%d')}")
            st.write(f"**Reported EPS:** {last_earnings.get('Reported EPS', 'N/A')}")
            st.write(f"**Estimated EPS:** {last_earnings.get('EPS Estimate', 'N/A')}")
            st.write(f"**Surprise (%):** {last_earnings.get('Surprise(%)', 'N/A')}")
        else:
            st.info("No past earnings data available.")

        next_earnings = earnings_dates[
            (earnings_dates.index > pd.Timestamp.now(tz='America/New_York')) &
            (earnings_dates['Event Type'] == 'Earnings') &
            (earnings_dates['EPS Estimate'].notna())
        ].sort_index()

        if not next_earnings.empty:
            next_earnings_date = next_earnings.iloc[0]
            st.write(f"**Next Earnings Date:** {next_earnings_date.name.strftime('%Y-%m-%d')}")
            st.write(f"**Estimated EPS:** {next_earnings_date.get('EPS Estimate', 'N/A')}")

    st.subheader("Next Earning Prediction")
    reported_eps_data = earnings_dates[
        (earnings_dates['Event Type'] == 'Earnings') &
        (earnings_dates['Reported EPS'].notna())
    ].sort_index(ascending=False)

    if not reported_eps_data.empty and len(reported_eps_data) >= 4:
        eps_values = reported_eps_data['Reported EPS'].head(4).values
        predicted_eps = np.mean(eps_values)
        st.write(f"**Predicted EPS for Next Quarter:** {predicted_eps:.2f}")
        st.caption("Prediction based on the average of the last 4 reported EPS values.")
    else:
        st.info("Not enough historical data to make a prediction.")