import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Optional, Dict, Any
from .config import (
    GOOGLE_SERVICE_ACCOUNT_JSON, GOOGLE_SHEET_ID,
    SHEET_KEYWORDS, SHEET_POSTS
)
from .models import KeywordRow, PostRow
from .utils.logger import logger

class SheetsClient:
    def __init__(self):
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.client = self._authenticate()
        self.spreadsheet = self._open_spreadsheet()

    def _authenticate(self):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                GOOGLE_SERVICE_ACCOUNT_JSON, self.scopes
            )
            return gspread.authorize(creds)
        except Exception as e:
            logger.log_action("Sheets Authentication", success=False, error_message=str(e))
            raise

    def _open_spreadsheet(self):
        try:
            return self.client.open_by_key(GOOGLE_SHEET_ID)
        except Exception as e:
            logger.log_action("Open Spreadsheet", success=False, error_message=str(e))
            raise

    def _get_worksheet(self, name: str):
        try:
            return self.spreadsheet.worksheet(name)
        except gspread.WorksheetNotFound:
            # For simplicity, create if missing (though usually pre-created)
            logger.logger.warning(f"Worksheet '{name}' not found. Creating it.")
            if name == SHEET_KEYWORDS:
                ws = self.spreadsheet.add_worksheet(title=name, rows="100", cols="6")
                ws.append_row(["keyword_id", "main_keyword", "content_type", "score", "status", "created_at"])
                return ws
            elif name == SHEET_POSTS:
                ws = self.spreadsheet.add_worksheet(title=name, rows="100", cols="7")
                ws.append_row(["post_id", "keyword_id", "title", "draft_html", "publish_status", "external_url", "created_at"])
                return ws
            return self.spreadsheet.add_worksheet(title=name, rows="100", cols="10")

    def read_keywords(self) -> List[KeywordRow]:
        ws = self._get_worksheet(SHEET_KEYWORDS)
        records = ws.get_all_records()
        return [KeywordRow.from_dict(rec) for rec in records]

    def find_keywords_by_status(self, status: str) -> List[KeywordRow]:
        keywords = self.read_keywords()
        return [kw for kw in keywords if kw.status == status]

    def update_keyword_status(self, keyword_id: str, status: str):
        ws = self._get_worksheet(SHEET_KEYWORDS)
        cell = ws.find(keyword_id)
        if not cell:
            logger.log_action("Update Keyword Status", keyword_id=keyword_id, success=False, error_message="Keyword ID not found")
            return
        
        # Determine column index for 'status'
        headers = ws.row_values(1)
        status_col = headers.index("status") + 1
        ws.update_cell(cell.row, status_col, status)
        logger.log_action("Update Keyword Status", keyword_id=keyword_id, next_status=status)

    def read_posts(self) -> List[PostRow]:
        ws = self._get_worksheet(SHEET_POSTS)
        records = ws.get_all_records()
        return [PostRow.from_dict(rec) for rec in records]

    def append_post(self, post: PostRow):
        ws = self._get_worksheet(SHEET_POSTS)
        headers = ws.row_values(1)
        
        # Create a full row representing all headers
        row_data = [""] * len(headers)
        
        # Map fields to indices
        mapping = {
            "post_id": post.post_id,
            "keyword_id": post.keyword_id,
            "title": post.title,
            "draft_html": post.draft_html,
            "publish_status": post.publish_status,
            "external_url": post.external_url or "",
            "created_at": post.created_at
        }
        
        for field_name, value in mapping.items():
            if field_name in headers:
                idx = headers.index(field_name)
                row_data[idx] = value
        
        ws.append_row(row_data)
        logger.log_action("Append Post", post_id=post.post_id, keyword_id=post.keyword_id)

    def update_post_status(self, post_id: str, publish_status: str, external_url: Optional[str] = None):
        ws = self._get_worksheet(SHEET_POSTS)
        cell = ws.find(post_id)
        if not cell:
            logger.log_action("Update Post Status", post_id=post_id, success=False, error_message="Post ID not found")
            return
        
        headers = ws.row_values(1)
        status_col = headers.index("publish_status") + 1
        ws.update_cell(cell.row, status_col, publish_status)
        
        if external_url:
            url_col = headers.index("external_url") + 1
            ws.update_cell(cell.row, url_col, external_url)
            
        logger.log_action("Update Post Status", post_id=post_id, next_status=publish_status)

    def find_posts_by_status(self, status: str) -> List[PostRow]:
        posts = self.read_posts()
        return [p for p in posts if p.publish_status == status]
