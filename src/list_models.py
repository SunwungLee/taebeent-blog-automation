from google import genai
from .config import get_config

def list_available_models():
    api_key = get_config("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is missing.")
        return
    
    client = genai.Client(api_key=api_key)
    print("Listing available models for your API key:")
    try:
        # The new SDK might have a different way to list models
        # or we can iterate through a known list and check availability
        for model in client.models.list():
            print(f" - {model.name} (Supported: {model.supported_generation_methods})")
    except Exception as e:
        print(f"Could not list models: {e}")

if __name__ == "__main__":
    import os
    import sys
    # Add parent directory to path to allow importing src
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    list_available_models()
