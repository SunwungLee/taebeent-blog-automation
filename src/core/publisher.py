import os
import markdown
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from ..config import get_config
from ..integrations.google_sheets import update_topic_status, STATUS_PUBLISHED

SCOPES = ['https://www.googleapis.com/auth/blogger']

def authenticate_blogger():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_id = get_config("BLOGGER_CLIENT_ID")
            client_secret = get_config("BLOGGER_CLIENT_SECRET")
            if not client_id or not client_secret:
                print("Missing Blogger OAuth credentials in .env")
                return None
                
            client_config = {
                "installed": {
                    "client_id": client_id,
                    "project_id": "blog-automation",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": client_secret,
                    "redirect_uris": ["http://localhost"]
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    try:
        service = build('blogger', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Failed to build Blogger service: {e}")
        return None

def publish_to_blogspot(title, content):
    service = authenticate_blogger()
    if not service:
        return None
        
    blog_id = get_config("BLOGGER_BLOG_ID")
    if not blog_id:
        print("BLOGGER_BLOG_ID is missing from .env")
        return None
        
    html_content = markdown.markdown(content)
    
    body = {
        "kind": "blogger#post",
        "title": title,
        "content": html_content
    }
    
    try:
        posts = service.posts()
        request = posts.insert(blogId=blog_id, body=body, isDraft=False)
        response = request.execute()
        return response.get('url')
    except Exception as e:
        print(f"Error publishing to Blogger: {e}")
        return None

def process_approved_topics(approved_topics):
    processed_count = 0
    for item in approved_topics:
        topic = item['topic']
        row_num = item['row_num']
        content = item.get('content')
        
        if not content:
            continue
            
        print(f"Publishing topic: '{topic}'...")
        url = publish_to_blogspot(title=topic, content=content)
        if url:
            success = update_topic_status(row_num, STATUS_PUBLISHED, url=url)
            if success:
                print(f"Successfully published: {topic} -> {url}")
                processed_count += 1
                
    return processed_count
