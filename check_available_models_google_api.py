import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("GOOGLE_API_KEY not found in environment variables.")
        return

    genai.configure(api_key=api_key)
    models = genai.list_models()
    print("Available Gemini models:")
    for model in models:
        print(f"- {model.name}")

if __name__ == "__main__":
    list_models()