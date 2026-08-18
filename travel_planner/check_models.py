import os
from dotenv import load_dotenv

load_dotenv()

try:
    from google.generativeai import list_models
    
    print("Available Google Generative AI models:")
    for model in list_models():
        print(f"  - {model.name}")
except Exception as e:
    print(f"Error: {e}")
    print("\nTry using OpenAI instead. Do you have an OPENAI_API_KEY?")
    print("Export it: export OPENAI_API_KEY=your-key")
