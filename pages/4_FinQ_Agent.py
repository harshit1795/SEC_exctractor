
import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="FinQ Agent", layout="wide")

st.title("FinQ Agent")

# Configure the Gemini API key
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except Exception as e:
    st.error("Please set the GEMINI_API_KEY environment variable.")
    st.stop()

# Initialize the model
model = genai.GenerativeModel('gemini-pro')

# Get the ticker and category from the session state
ticker = st.session_state.get("selected_ticker", "AAPL")
category = st.session_state.get("stmt_cat", "Income Statement")

# Create the prompt
prompt = f"""
You are a financial analyst AI. Your task is to provide a detailed analysis of the financial data for {ticker} in the {category} category.

Here is the data:
{st.session_state.get("ticker_df", "No data available.")}

Please provide a detailed analysis of the data, including any trends, insights, or red flags that you identify.
"""

if st.button("Analyze"):
    with st.spinner("Analyzing..."):
        response = model.generate_content(prompt)
        st.markdown(response.text)
