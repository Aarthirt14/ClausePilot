import hashlib
import logging
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)

_OCR_NOISE_PATTERN = re.compile(r"\b(?:l\s*\/\s*I|I\s*\/\s*l|\|{2,}|_{2,})\b")
_MULTI_DOT_PATTERN = re.compile(r"\.{3,}")


def normalize_text(text: str) -> str:
    """Normalize text for modeling and deduplication."""
    if not text:
        return ""
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = cleaned.replace("\x0c", " ")
    cleaned = _OCR_NOISE_PATTERN.sub(" ", cleaned)
    cleaned = _MULTI_DOT_PATTERN.sub(".", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines())
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip().lower()


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def deduplicate_clauses(clauses: List[str]) -> Tuple[List[str], int]:
    """Remove duplicate clauses using hashing. Returns (unique, removed_count)."""
    seen = set()
    unique = []
    removed = 0

    for clause in clauses:
        normalized = normalize_text(clause)
        if not normalized:
            continue
        hashed = _hash_text(normalized)
        if hashed in seen:
            removed += 1
            continue
        seen.add(hashed)
        unique.append(clause)

    if removed:
        logger.info("Removed %s duplicate clauses during cleaning", removed)

    return unique, removed
