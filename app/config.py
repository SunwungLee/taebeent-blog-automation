import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Sheets Configuration
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "credentials/service_account.json")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# Blogger API Configuration
BLOGGER_CLIENT_ID = os.getenv("BLOGGER_CLIENT_ID")
BLOGGER_CLIENT_SECRET = os.getenv("BLOGGER_CLIENT_SECRET")
BLOGGER_BLOG_ID = os.getenv("BLOGGER_BLOG_ID")

# LLM APIs (Gemini/OpenAI)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Notion Configuration (Optional)
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")

# Sheet Names
SHEET_KEYWORDS = "keywords"
SHEET_POSTS = "posts"

# Content Types
CONTENT_TYPE_INFO = "info"
CONTENT_TYPE_REVIEW = "review"
CONTENT_TYPE_VLOG = "vlog"

# Statuses - Keywords
KW_STATUS_COLLECTED = "keyword_collected"
KW_STATUS_APPROVED = "approved_for_writing"
KW_STATUS_GEN_REQUESTED = "generation_requested"
KW_STATUS_GENERATING = "generating"
KW_STATUS_HTML_READY = "html_ready"
KW_STATUS_READY_TO_PUBLISH = "ready_to_publish"
KW_STATUS_PUBLISHING = "publishing"
KW_STATUS_PUBLISHED = "published"
KW_STATUS_TRACKING = "tracking"
KW_STATUS_NEEDS_REFRESH = "needs_refresh"

# Statuses - Posts (Publish Status)
POST_STATUS_DRAFT = "draft"
POST_STATUS_READY = "ready_to_publish"
POST_STATUS_PUBLISHING = "publishing"
POST_STATUS_PUBLISHED = "published"
POST_STATUS_FAILED = "failed"
