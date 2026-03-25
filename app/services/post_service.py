from typing import List
from ..sheets_client import SheetsClient
from ..models import PostRow, GeneratedContent
from ..config import POST_STATUS_READY, POST_STATUS_DRAFT
from ..utils.ids import generate_post_id
from ..utils.dates import get_now_iso

class PostService:
    def __init__(self, sheets_client: SheetsClient):
        self.sheets = sheets_client

    def create_post_record_from_generated_content(self, content: GeneratedContent) -> PostRow:
        """
        Converts GeneratedContent into a PostRow and saves it to Sheets.
        """
        post = PostRow(
            post_id=generate_post_id(),
            keyword_id=content.keyword_id,
            title=content.title,
            draft_html=content.html,
            publish_status=POST_STATUS_READY, # Transition directly to ready since it's already generated and validated
            created_at=get_now_iso()
        )
        self.sheets.append_post(post)
        return post

    def get_publish_candidates(self, limit: int = 2) -> List[PostRow]:
        """
        Reads posts where publish_status = ready_to_publish
        """
        return self.sheets.find_posts_by_status(POST_STATUS_READY)[:limit]

    def mark_publishing(self, post_id: str):
        self.sheets.update_post_status(post_id, "publishing")

    def mark_published(self, post_id: str, external_url: str):
        self.sheets.update_post_status(post_id, "published", external_url=external_url)

    def mark_failed(self, post_id: str):
        self.sheets.update_post_status(post_id, "failed")
