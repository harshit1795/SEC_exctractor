
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
        # Last Quarter's Earnings
        st.subheader("Last Quarter's Earnings")
        # Ensure the index is a datetime object for comparison
        earnings_dates.index = pd.to_datetime(earnings_dates.index)
        
        # Get the most recent past earnings date
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

        # Next Earnings Prediction (from yfinance)
        # This section is now integrated with the simple prediction model below
        # so we remove the redundant subheader here.
        # st.subheader("Next Earnings Prediction")
        # Find the next earnings date that is in the future and is an 'Earnings' event
        next_earnings = earnings_dates[
            (earnings_dates.index > pd.Timestamp.now(tz='America/New_York')) &
            (earnings_dates['Event Type'] == 'Earnings') &
            (earnings_dates['EPS Estimate'].notna())
        ].sort_index()

        if not next_earnings.empty:
            next_earnings = next_earnings.iloc[0]
            st.write(f"**Next Earnings Date:** {next_earnings.name.strftime('%Y-%m-%d')}")
            st.write(f"**Estimated EPS:** {next_earnings.get('EPS Estimate', 'N/A')}")
            # You can add more predictions if available in ticker_info_yf
            if ticker_info_yf and 'earningsHigh' in ticker_info_yf:
                st.write(f"**High Estimate:** {ticker_info_yf['earningsHigh']}")
            if ticker_info_yf and 'earningsLow' in ticker_info_yf:
                st.write(f"**Low Estimate:** {ticker_info_yf['earningsLow']}")
            if ticker_info_yf and 'earningsAvg' in ticker_info_yf:
                st.write(f"**Average Estimate:** {ticker_info_yf['earningsAvg']}")

    st.subheader("Historical EPS Trend")
    # Filter for earnings events and valid EPS data
    historical_eps_df = earnings_dates[
        (earnings_dates['Event Type'] == 'Earnings') &
        (earnings_dates['Reported EPS'].notna()) &
        (earnings_dates['EPS Estimate'].notna())
    ].reset_index().rename(columns={'Earnings Date': 'Date'})

    if not historical_eps_df.empty:
        # Melt the DataFrame for Altair
        melted_eps_df = historical_eps_df.melt(
            id_vars=['Date'], 
            value_vars=['Reported EPS', 'EPS Estimate'], 
            var_name='EPS Type', 
            value_name='EPS Value'
        )

        chart = alt.Chart(melted_eps_df).mark_line(point=True).encode(
            x=alt.X('Date', type='temporal', title='Earnings Date', axis=alt.Axis(format='%b %Y', labelAngle=-90)),
            y=alt.Y('EPS Value', title='EPS'),
            color='EPS Type',
            tooltip=[
                alt.Tooltip('Date', title='Period'),
                alt.Tooltip('EPS Type', title='Type'),
                alt.Tooltip('EPS Value', title='EPS')
            ]
        ).properties(
            title=f'{selected_ticker} Historical EPS Trend'
        ).interactive()
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No sufficient historical EPS data available for charting.")

    # --- Simple EPS Prediction Model --- #
    st.subheader("Next Earning Prediction")
    
    # Get reported EPS data for prediction
    reported_eps_data = earnings_dates[
        (earnings_dates['Event Type'] == 'Earnings') &
        (earnings_dates['Reported EPS'].notna())
    ].sort_index(ascending=False) # Sort to get most recent first

    if not reported_eps_data.empty and len(reported_eps_data) >= 4: # Need at least 4 quarters for a basic trend
        # Take the last 4 reported EPS values
        eps_values = reported_eps_data['Reported EPS'].head(4).values
        
        predicted_eps = np.mean(eps_values)
        st.write(f"**Predicted EPS for Next Quarter:** {predicted_eps:.2f}")
        st.caption("Prediction based on the average of the last 4 reported EPS values.")
    else:
        st.info("Not enough historical data to make a prediction (need at least 4 reported EPS values).")
