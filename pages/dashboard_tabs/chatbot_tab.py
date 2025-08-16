
import streamlit as st
import google.generativeai as genai
from auth import load_api_keys

def render():
    load_api_keys()
    st.markdown("### FinQ Bot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is your question?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response from Gemini API
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')

            # System instruction for the financial analyst AI
            system_instruction = '''You are a highly skilled financial analyst AI. Your primary goal is to provide insightful and accurate financial analysis based on the provided data.
You should:
- Analyze trends and patterns.
- Identify key financial metrics and their implications.
- Highlight potential risks or opportunities.
- Answer questions directly related to the financial data provided.
- If a question cannot be answered from the provided data, state that clearly.
- Do not make up information or provide analysis beyond the scope of the given data.
- Present your analysis in a clear, concise, and professional manner.
- Use consistent financial currency notations (e.g., $1.2B, $500M, $25M) instead of scientific notation for all monetary values.-
'''
            
            # Get the financial data from session state
            current_ticker_df = st.session_state.get("ticker_df")
            if current_ticker_df is not None and not current_ticker_df.empty:
                financial_data_str = current_ticker_df.to_markdown(index=False)
            else:
                financial_data_str = "No specific financial data available for analysis in the current context."

            # Construct the full prompt
            full_prompt = f'''{system_instruction}

Here is the financial data for the selected company and category:
{financial_data_str}

User's question: {prompt}
'''
            response = model.generate_content(full_prompt)
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"An error occurred: {e}")
