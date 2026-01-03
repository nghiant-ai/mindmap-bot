"""
Date and time utility functions - Simplified for Mindmap Bot
"""
from datetime import datetime, timezone, timedelta


# Vietnam timezone (UTC+7)
VIETNAM_TZ = timezone(timedelta(hours=7))


def get_vietnam_time() -> datetime:
    """
    Get current time in Vietnam timezone

    Returns:
        datetime: Current datetime in Vietnam timezone (UTC+7)
    """
    utc_now = datetime.now(timezone.utc)
    return utc_now.astimezone(VIETNAM_TZ)
