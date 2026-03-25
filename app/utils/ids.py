import random
import string
from .dates import get_today_str

def generate_post_id() -> str:
    """
    Generates a stable ID for a post.
    Format: POST-YYYYMMDD-XXX (where XXX is a random alphanumeric string)
    """
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"POST-{get_today_str()}-{random_part}"
