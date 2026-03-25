import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .config import get_config

# Constants for worksheet columns
COL_TOPIC = 1
COL_STATUS = 2
COL_DRAFT = 3
COL_URL = 4

# Status constants
STATUS_PENDING = "PENDING"
STATUS_DRAFTED = "DRAFTED"
STATUS_APPROVED = "APPROVED"
STATUS_PUBLISHED = "PUBLISHED"

def get_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    json_path = get_config("GOOGLE_JSON_PATH")
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"Error authenticating with Google Sheets: {e}")
        return None

def get_sheet():
    client = get_client()
    if not client:
        return None
    sheet_id = get_config("GOOGLE_SHEET_ID")
    if not sheet_id:
        print("GOOGLE_SHEET_ID is not configured in .env")
        return None
        
    try:
        # Assuming the first worksheet is the one we want
        sheet = client.open_by_key(sheet_id).sheet1
        return sheet
    except Exception as e:
        print(f"Error opening sheet (ID: {sheet_id}): {e}")
        return None

def init_sheet_headers():
    sheet = get_sheet()
    if not sheet:
        return
    
    headers = ["Topic", "Status", "Content/Draft", "URL"]
    current_headers = sheet.row_values(1)
    if not current_headers or current_headers[0] != headers[0]:
        sheet.insert_row(headers, 1)
        print("Initialized Sheet headers.")

def add_new_topic(topic):
    sheet = get_sheet()
    if not sheet:
        return False
        
    try:
        existing_topics = sheet.col_values(COL_TOPIC)
        if topic in existing_topics:
            print(f"Topic '{topic}' already exists in the sheet.")
            return False
            
        sheet.append_row([topic, STATUS_PENDING, "", ""])
        print(f"Added new topic: {topic}")
        return True
    except Exception as e:
        print(f"Error adding topic to sheet: {e}")
        return False

def get_topics_by_status(status):
    sheet = get_sheet()
    if not sheet:
        return []
        
    try:
        records = sheet.get_all_records()
        topics = []
        for idx, row in enumerate(records):
            if row.get('Status') == status:
                topics.append({
                    "row_num": idx + 2, 
                    "topic": row.get('Topic'),
                    "content": row.get('Content/Draft'),
                    "url": row.get('URL')
                })
        return topics
    except Exception as e:
        print(f"Error fetching topics with status {status}: {e}")
        return []

def get_pending_topics():
    return get_topics_by_status(STATUS_PENDING)

def get_drafted_topics():
    return get_topics_by_status(STATUS_DRAFTED)

def get_approved_topics():
    return get_topics_by_status(STATUS_APPROVED)

def update_topic_status(row_num, status, content=None, url=None):
    sheet = get_sheet()
    if not sheet:
        return False
        
    try:
        sheet.update_cell(row_num, COL_STATUS, status)
        if content is not None:
            sheet.update_cell(row_num, COL_DRAFT, content)
        if url is not None:
            sheet.update_cell(row_num, COL_URL, url)
        return True
    except Exception as e:
        print(f"Error updating sheet at row {row_num}: {e}")
        return False
