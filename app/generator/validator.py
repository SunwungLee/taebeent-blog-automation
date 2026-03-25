import re
from ..models import GeneratedContent
from ..utils.logger import logger

class ContentValidator:
    def __init__(self):
        self.min_length = 500 # Minimum characters
        self.banned_phrases = ["click here", "buy now", "subscribe", "ad", "promo"]

    def validate(self, content: GeneratedContent) -> bool:
        """
        Validates the generated HTML content.
        """
        html = content.html
        
        # 1. HTML not empty
        if not html or len(html.strip()) == 0:
            logger.logger.error("Validation Failed: HTML is empty")
            return False
            
        # 2. Minimum length
        if len(html) < self.min_length:
            logger.logger.error(f"Validation Failed: Content too short ({len(html)} chars)")
            return False
            
        # 3. Contains at least 3 <h2> sections
        h2_count = len(re.findall(r'<h2.*?>', html, re.IGNORECASE))
        if h2_count < 3:
            logger.logger.error(f"Validation Failed: Found only {h2_count} <h2> tags (need at least 3)")
            return False
            
        # 4. Contains FAQ
        if '자주 묻는 질문' not in html and 'FAQ' not in html.upper():
            logger.logger.error("Validation Failed: FAQ section missing")
            return False
            
        # 5. No banned phrases (case-insensitive, whole words)
        for phrase in self.banned_phrases:
            pattern = rf'\b{re.escape(phrase)}\b'
            if re.search(pattern, html, re.IGNORECASE):
                logger.logger.error(f"Validation Failed: Banned phrase '{phrase}' found")
                return False
                
        # 6. Paragraphs are reasonably short (check for long blocks of text)
        # Simple check: no <p> should contain more than 1000 characters
        p_contents = re.findall(r'<p.*?>(.*?)</p>', html, re.DOTALL | re.IGNORECASE)
        for p in p_contents:
            if len(p) > 1000:
                logger.logger.error("Validation Failed: Paragraph too long")
                return False

        logger.logger.info(f"Validation Passed for keyword: {content.keyword_id}")
        return True
