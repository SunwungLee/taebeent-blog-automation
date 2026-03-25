import logging
import sys
from datetime import datetime

class StructuredLogger:
    def __init__(self, name="blogspot_agent"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_action(self, action: str, keyword_id: str = None, post_id: str = None, 
                   current_status: str = None, next_status: str = None, 
                   success: bool = True, error_message: str = None):
        """
        Logs a structured action message.
        """
        msg = f"ACTION: {action}"
        if keyword_id: msg += f" | KW_ID: {keyword_id}"
        if post_id: msg += f" | POST_ID: {post_id}"
        if current_status: msg += f" | FROM: {current_status}"
        if next_status: msg += f" | TO: {next_status}"
        msg += f" | RESULT: {'SUCCESS' if success else 'FAILURE'}"
        if error_message: msg += f" | ERROR: {error_message}"
        
        if success:
            self.logger.info(msg)
        else:
            self.logger.error(msg)

# Singleton instance
logger = StructuredLogger()
