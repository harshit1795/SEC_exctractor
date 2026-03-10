import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Loaded API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("Error: GEMINI_API_KEY not found in environment.")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-flash-latest')

try:
    print("Attempting to generate content...")
    response = model.generate_content("Hello, can you hear me?")
    print("Success! Response received:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
