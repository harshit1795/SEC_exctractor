
import google.generativeai as genai
import os
import sys

try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Reading from settoken.sh as a fallback
        with open('settoken.sh', 'r') as f:
            for line in f:
                if 'GEMINI_API_KEY' in line:
                    api_key = line.split('=')[1].strip().strip('"')
                    break
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment or settoken.sh")
        sys.exit(1)

    genai.configure(api_key=api_key)
    
    print("Available models that support 'generateContent':")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"An error occurred while listing models: {e}")
