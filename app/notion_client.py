from typing import Optional
from .utils.logger import logger

class NotionClient:
    """
    Optional Notion client for retrieval of guidelines and templates.
    Currently stubbed as per MVP requirements.
    """
    def __init__(self):
        self.token = None
        self.page_id = None

    def fetch_guidelines(self) -> str:
        logger.logger.info("Notion fetch_guidelines (stub) called.")
        return "Default Blogspot writing guidelines: SEO friendly, H2 headings, FAQ included."

    def fetch_template(self, content_type: str) -> str:
        logger.logger.info(f"Notion fetch_template (stub) called for {content_type}.")
        return f"Template for {content_type}: [TITLE] [BODY] [FAQ]"
