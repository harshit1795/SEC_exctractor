

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
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI for selecting context ---
st.sidebar.header("Context Selection")
all_tickers = sorted(load_data()["Ticker"].unique())
selected_ticker = st.sidebar.selectbox("Select Ticker", all_tickers, index=all_tickers.index(st.session_state.get("selected_ticker", "AAPL")))
st.session_state.selected_ticker = selected_ticker

data_sources = st.sidebar.multiselect(
    "Select Data Sources",
    ["Company Financials", "Macroeconomic Data"],
    default=["Company Financials", "Macroeconomic Data"]
)

# --- Data Loading ---

# Load company financial data
with st.spinner("Loading financial data..."):
    df = load_data()
    category = st.session_state.get("stmt_cat", "Income Statement")
    ticker_df = df[(df["Ticker"] == selected_ticker) & (df["Category"] == category)]

# Fetch FRED data
if "Macroeconomic Data" in data_sources:
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
else:
    fred_df = pd.DataFrame()

# --- Prompt Building ---

def build_prompt_with_context(chat_history):
    context_parts = ["You are a financial analyst AI. Your task is to provide a detailed analysis based on the provided data."]

    if "Company Financials" in data_sources:
        context_parts.append(f"\nHere is the company's financial data for {selected_ticker} in the {category} category:\n{ticker_df.to_markdown()}")

    if "Macroeconomic Data" in data_sources and not fred_df.empty:
        context_parts.append(f"\nHere is the macroeconomic data from FRED:\n{fred_df.to_markdown()}")
    
    # Combine context with chat history
    full_prompt = "\n".join(context_parts) + "\n\n---\n\n" + "\n".join([f"{m['role']}: {m['content']}" for m in chat_history])
    return full_prompt

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
        full_prompt = build_prompt_with_context(st.session_state.messages)
        response = model.generate_content(full_prompt)
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response.text)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response.text})
