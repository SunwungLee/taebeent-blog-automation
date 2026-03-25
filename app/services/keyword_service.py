from typing import List
from ..sheets_client import SheetsClient
from ..models import KeywordRow
from ..config import (
    KW_STATUS_APPROVED, KW_STATUS_GEN_REQUESTED,
    KW_STATUS_GENERATING, KW_STATUS_HTML_READY
)
from ..state_machine import validate_kw_transition

class KeywordService:
    def __init__(self, sheets_client: SheetsClient):
        self.sheets = sheets_client

    def get_generation_candidates(self, limit: int = 3) -> List[KeywordRow]:
        """
        Reads keywords where status = approved_for_writing
        """
        candidates = self.sheets.find_keywords_by_status(KW_STATUS_APPROVED)
        return candidates[:limit]

    def _update_status(self, keyword_id: str, current_status: str, next_status: str):
        validate_kw_transition(current_status, next_status)
        self.sheets.update_keyword_status(keyword_id, next_status)

    def mark_generation_requested(self, kw: KeywordRow):
        self._update_status(kw.keyword_id, kw.status, KW_STATUS_GEN_REQUESTED)

    def mark_generating(self, kw: KeywordRow):
        self._update_status(kw.keyword_id, KW_STATUS_GEN_REQUESTED, KW_STATUS_GENERATING)

    def mark_html_ready(self, kw: KeywordRow):
        self._update_status(kw.keyword_id, KW_STATUS_GENERATING, KW_STATUS_HTML_READY)
        
    def revert_to_approved(self, kw: KeywordRow):
        """Used on failure."""
        self.sheets.update_keyword_status(kw.keyword_id, KW_STATUS_APPROVED)
