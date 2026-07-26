"""
helpers.py — Shared utility functions.
"""
import re
from typing import Optional


def clean_phone(phone: str) -> str:
    """Strip non-digit characters, keep leading +."""
    phone = phone.strip()
    cleaned = re.sub(r"[^\d+]", "", phone)
    return cleaned


def normalise_url(url: Optional[str]) -> Optional[str]:
    """Ensure URL has a scheme."""
    if not url:
        return None
    url = url.strip()
    if url and not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def slug(text: str) -> str:
    """Convert a string to a lowercase slug."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def truncate(text: str, max_len: int = 200) -> str:
    """Truncate long strings for display."""
    return text if len(text) <= max_len else text[:max_len] + "…"
