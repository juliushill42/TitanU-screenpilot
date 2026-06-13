"""Shared utilities."""
import hashlib
from pathlib import Path


def file_hash(path: str | Path) -> str:
    """SHA256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def truncate(text: str, max_chars: int = 4000) -> str:
    """Truncate text to stay within LLM context."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n...[truncated, {len(text) - max_chars} chars omitted]"
