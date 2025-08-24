import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import yfinance as yf

@st.cache_data(show_spinner=False)
def get_ticker_earnings_data(ticker_symbol):
    ticker_yf = yf.Ticker(ticker_symbol)
    return ticker_yf.earnings_dates, ticker_yf.info

def render(selected_ticker):
    st.markdown("### Earning Summary")

    earnings_dates, ticker_info_yf = get_ticker_earnings_data(selected_ticker)

    if not earnings_dates.empty:
        earnings_dates.index = pd.to_datetime(earnings_dates.index)
        
        # Last Quarter's Earnings
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

        # Next Earnings Prediction
        next_earnings = earnings_dates[
            (earnings_dates.index > pd.Timestamp.now(tz='America/New_York')) &
            (earnings_dates['Event Type'] == 'Earnings') &
            (earnings_dates['EPS Estimate'].notna())
        ].sort_index()

        if not next_earnings.empty:
            next_earnings_date = next_earnings.iloc[0]
            st.write(f"**Next Earnings Date:** {next_earnings_date.name.strftime('%Y-%m-%d')}")
            st.write(f"**Estimated EPS:** {next_earnings_date.get('EPS Estimate', 'N/A')}")

    st.subheader("Historical EPS Trend")
    historical_eps_df = earnings_dates[
        (earnings_dates['Event Type'] == 'Earnings') &
        (earnings_dates['Reported EPS'].notna()) &
        (earnings_dates['EPS Estimate'].notna())
    ].reset_index().rename(columns={'Earnings Date': 'Date'})

    if not historical_eps_df.empty:
        # --- FILTERS ---
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            start_date = st.date_input("Start date", historical_eps_df['Date'].min(), key="earnings_start")
        with c2:
            end_date = st.date_input("End date", historical_eps_df['Date'].max(), key="earnings_end")
        with c3:
            aggregation_period = st.selectbox(
                "Aggregation Period:",
                options=['Quarterly', 'Yearly'],
                index=0,
                key="earnings_agg_period"
            )
        with c4:
            chart_type = st.radio("Chart Type:", ["Line", "Bar"], key="earnings_chart_type")

        # --- PROCESS DATA ---
        mask = (historical_eps_df['Date'] >= pd.to_datetime(start_date, utc=True)) & (historical_eps_df['Date'] <= pd.to_datetime(end_date, utc=True))
        filtered_df = historical_eps_df.loc[mask]

        if aggregation_period == 'Yearly':
            agg_df = filtered_df.set_index('Date').resample('A').sum(numeric_only=True).reset_index()
        else:
            agg_df = filtered_df

        if not agg_df.empty:
            melted_df = agg_df.melt(
                id_vars=['Date'], 
                value_vars=['Reported EPS', 'EPS Estimate'], 
                var_name='EPS Type', 
                value_name='EPS Value'
            )

            # --- CREATE CHART ---
            # Manually format the date label to prevent repetition
            if aggregation_period == 'Yearly':
                melted_df['Label'] = melted_df['Date'].dt.strftime('%Y')
                x_title = 'Year'
            else: # Quarterly
                melted_df['Label'] = melted_df['Date'].dt.to_period('Q').astype(str)
                x_title = 'Quarter'
            
            x_axis = alt.X('Label:O', title=x_title, sort=None) # Use formatted label, disable sorting

            base = alt.Chart(melted_df).encode(
                x=x_axis,
                y=alt.Y('EPS Value', title='EPS'),
                color='EPS Type:N',
                tooltip=['Label', 'EPS Type', 'EPS Value']
            )

            if chart_type == "Line":
                chart = base.mark_line(point=True).interactive()
            else: # Bar
                chart = base.mark_bar().encode(xOffset='EPS Type:N').interactive()

            st.altair_chart(chart.properties(title=f'{selected_ticker} Historical EPS Trend'), use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    else:
        st.info("No sufficient historical EPS data available for charting.")

    # --- Simple EPS Prediction Model --- #
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