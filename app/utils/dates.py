from datetime import datetime

def get_now_iso() -> str:
    """Returns current timestamp in ISO format."""
    return datetime.now().isoformat()

def get_today_str() -> str:
    """Returns today's date in YYYYMMDD format."""
    return datetime.now().strftime("%Y%m%d")
