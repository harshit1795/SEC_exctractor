
import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from fred_data import get_multiple_fred_series

st.set_page_config(page_title="FinQ Agent", layout="wide")

st.title("FinQ Agent")

# Configure the Gemini API key
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except Exception as e:
    st.error("Please set the GEMINI_API_KEY environment variable.")
    st.stop()

# Define the path to the data
PARQUET_PATH = "fundamentals_tall.parquet"

@st.cache_data(show_spinner=True)
def load_data(path: str = PARQUET_PATH) -> pd.DataFrame:
    """Load the fundamentals data from the parquet file."""
    return pd.read_parquet(path)

# Initialize the model
model = genai.GenerativeModel('gemini-pro')

# Initialize chat history in session state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# Get the ticker and category from the session state
ticker = st.session_state.get("selected_ticker", "AAPL")
category = st.session_state.get("stmt_cat", "Income Statement")

# Always load the full data and filter it to ensure it's fresh and relevant
with st.spinner("Loading financial data..."):
    df = load_data()
    # Filter the DataFrame for the selected ticker and category
    ticker_df = df[(df["Ticker"] == ticker) & (df["Category"] == category)]

# Fetch FRED data
INDICATORS = {
    "GDP": "GDP",
    "Real GDP": "GDPC1",
    "Inflation (CPI)": "CPIAUCSL",
    "Unemployment Rate": "UNRATE",
    "10-Year Treasury Yield": "DGS10",
    "Federal Funds Rate": "FEDFUNDS",
}
series_to_fetch = list(INDICATORS.values())
today = pd.to_datetime("today")
start_date = (today - pd.DateOffset(years=5)).strftime('%Y-%m-%d')
end_date = today.strftime('%Y-%m-%d')
fred_df = get_multiple_fred_series(series_to_fetch, start_date, end_date)

# Initial prompt for analysis
initial_prompt = f"""
You are a financial analyst AI. Your task is to provide a detailed analysis of the financial data for {ticker} in the {category} category, considering the broader economic context.

Here is the company's financial data:
{ticker_df.to_markdown()}

Here is the macroeconomic data from FRED:
{fred_df.to_markdown()}

Please provide a detailed analysis of the company's financial data, including any trends, insights, or red flags that you identify. Also, analyze how the macroeconomic data might be impacting the company's performance and outlook. After your analysis, ask the user if they have any specific questions.
"""

# If chat is empty, start with an analysis
if not st.session_state.messages:
    with st.spinner("Analyzing..."):
        response = st.session_state.chat.send_message(initial_prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is your question?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.spinner("Thinking..."):
        response = st.session_state.chat.send_message(prompt)
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response.text)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response.text})
