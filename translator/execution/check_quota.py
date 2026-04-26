import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

models_to_try = [
    'gemini-1.5-flash', 
    'gemini-1.5-flash-8b', 
    'gemini-1.5-pro', 
    'gemini-pro',
    'gemini-flash-latest'
]

for m in models_to_try:
    try:
        print(f"Trying {m}...")
        model = genai.GenerativeModel(m)
        response = model.generate_content("Hello, translate 'Hi' to Korean.")
        print(f"SUCCESS with {m}: {response.text}")
        break
    except Exception as e:
        print(f"FAILED with {m}: {e}")
