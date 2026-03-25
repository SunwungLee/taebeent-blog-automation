import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from .config import BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET, BLOGGER_BLOG_ID
from .models import PublishResult
from .utils.logger import logger

SCOPES = ['https://www.googleapis.com/auth/blogger']

class BloggerClient:
    def __init__(self):
        self.service = self._authenticate()
        self.blog_id = BLOGGER_BLOG_ID

    def _authenticate(self):
        creds = None
        token_path = os.path.join('credentials', 'token.json')
        
        # Ensure credentials directory exists
        os.makedirs('credentials', exist_ok=True)

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.log_action("Blogger Token Refresh", success=False, error_message=str(e))
                    creds = None # Force re-auth
            
            if not creds:
                if not BLOGGER_CLIENT_ID or not BLOGGER_CLIENT_SECRET:
                    raise ValueError("Missing Blogger OAuth credentials in environment variables")
                
                client_config = {
                    "installed": {
                        "client_id": BLOGGER_CLIENT_ID,
                        "project_id": "blog-automation",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_secret": BLOGGER_CLIENT_SECRET,
                        "redirect_uris": ["http://localhost"]
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                creds = flow.run_local_server(port=0)
                
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
                
        try:
            return build('blogger', 'v3', credentials=creds)
        except Exception as e:
            logger.log_action("Blogger Service Build", success=False, error_message=str(e))
            raise

    def create_post(self, title: str, html: str, labels: list = None) -> PublishResult:
        """
        Creates a post in Blogger.
        """
        body = {
            "kind": "blogger#post",
            "title": title,
            "content": html
        }
        if labels:
            body["labels"] = labels
            
        try:
            posts = self.service.posts()
            request = posts.insert(blogId=self.blog_id, body=body, isDraft=False)
            response = request.execute()
            url = response.get('url')
            return PublishResult(post_id="", success=True, url=url)
        except Exception as e:
            logger.log_action("Blogger Create Post", success=False, error_message=str(e))
            return PublishResult(post_id="", success=False, error_message=str(e))
