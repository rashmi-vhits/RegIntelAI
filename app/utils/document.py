import hashlib
import re
from pathlib import Path


def detect_document_type(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


def sanitize_filename(filename: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", filename)
    return sanitized or "document"


def hash_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
