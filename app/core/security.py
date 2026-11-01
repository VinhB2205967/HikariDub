"""
Core Security Module - Local-First & Permanent Free Edition
Manages license status and subtitle watermark policy.
"""

# Always set to premium status to ensure full feature unlock and no watermarks
CURRENT_LICENSE_STATUS = "premium"

def inject_watermark_to_srt(subs, watermark_text: str = "[HikariDub]"):
    """
    In the permanent free edition, subtitles remain clean without injected watermarks.
    Returns original subtitles unmodified.
    """
    return subs

