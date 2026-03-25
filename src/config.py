import os
from dotenv import load_dotenv

load_dotenv()

# Configuration mapping
CONFIG = {
    "GOOGLE_JSON_PATH": os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "service_account.json"),
    "GOOGLE_SHEET_ID": os.getenv("GOOGLE_SHEET_ID"),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "BLOGGER_CLIENT_ID": os.getenv("BLOGGER_CLIENT_ID"),
    "BLOGGER_CLIENT_SECRET": os.getenv("BLOGGER_CLIENT_SECRET"),
    "BLOGGER_BLOG_ID": os.getenv("BLOGGER_BLOG_ID"),
}

def get_config(key):
    return CONFIG.get(key)
