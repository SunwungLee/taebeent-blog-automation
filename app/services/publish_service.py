from ..sheets_client import SheetsClient
from ..blogger_client import BloggerClient
from ..models import PostRow, PublishResult
from ..config import KW_STATUS_PUBLISHED
from .post_service import PostService
from ..utils.logger import logger

class PublishService:
    def __init__(self, sheets_client: SheetsClient, blogger_client: BloggerClient, post_service: PostService):
        self.sheets = sheets_client
        self.blogger = blogger_client
        self.post_service = post_service

    def publish_post(self, post: PostRow) -> bool:
        """
        Orchestrates publishing a post to Blogger.
        """
        logger.log_action("Publish Post Start", post_id=post.post_id)
        
        # 1. Mark as publishing
        self.post_service.mark_publishing(post.post_id)
        
        # 2. Publish via Blogger
        result: PublishResult = self.blogger.create_post(title=post.title, html=post.draft_html)
        
        if result.success:
            # 3. Update Sheets: post publish_status = published, external_url saved
            self.post_service.mark_published(post.post_id, result.url)
            
            # 4. Update Sheets: keyword status = published
            self.sheets.update_keyword_status(post.keyword_id, KW_STATUS_PUBLISHED)
            
            logger.log_action("Publish Post Success", post_id=post.post_id)
            return True
        else:
            # 5. Handle failure
            self.post_service.mark_failed(post.post_id)
            logger.log_action("Publish Post Failure", post_id=post.post_id, success=False, error_message=result.error_message)
            return False
