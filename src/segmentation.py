"""
src/segmentation.py
-------------------
Splits raw contract text into individual clauses using:
  1. Numbered sections  (e.g.  1.  /  1.1  /  1.1.1  /  (a)  /  (i) )
  2. Semicolons
  3. Sentence boundaries (period / question-mark / exclamation-mark)

Returns only clauses longer than 20 characters after stripping whitespace.
"""
import re
from typing import List

from src.data_processing.cleaning import deduplicate_clauses

# ── Regex patterns ──────────────────────────────────────────────────
# Matches lines that start with a numbered heading like  1.  /  1.1  /  (a)
_SECTION_PATTERN = re.compile(
    r"(?:^|\n)"                              # start of string or newline
    r"(?:"
    r"  \d+(?:\.\d+)*\.?\s"                  # 1.  1.1  1.1.1
    r"| \([a-z]\)\s"                         # (a) (b) …
    r"| \([ivxlcdm]+\)\s"                    # (i) (ii) (iii) …
    r")",
    re.IGNORECASE | re.VERBOSE,
)

# Sentence-ending punctuation followed by a space + uppercase letter
_SENTENCE_BOUNDARY = re.compile(
    r"(?<=[.!?])\s+(?=[A-Z])"
)

_OCR_NOISE_PATTERN = re.compile(r"\b(?:l\s*\/\s*I|I\s*\/\s*l|\|{2,}|_{2,})\b")
_MULTI_DOT_PATTERN = re.compile(r"\.{3,}")
_ARTIFACT_PREFIX_PATTERN = re.compile(r"^(?:\d+[\.)]|\(?[a-zA-Z]\)|[ivxlcdm]+\.)\s*$", re.IGNORECASE)


def normalize_contract_text(text: str) -> str:
    """Apply contract-specific text normalization and OCR cleanup."""
    normalized = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalized.replace("\x0c", " ")
    normalized = _OCR_NOISE_PATTERN.sub(" ", normalized)
    normalized = _MULTI_DOT_PATTERN.sub(".", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = "\n".join(line.strip() for line in normalized.splitlines())
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def _clean_clause_artifacts(clause: str) -> str:
    """Remove numbering/outline artifacts left after segmentation."""
    cleaned = clause.strip()
    cleaned = re.sub(r"^\s*(?:\d+(?:\.\d+)*\.?\s+)+", "", cleaned)
    cleaned = re.sub(r"^\s*\(([a-z]|[ivxlcdm]+)\)\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def segment_clauses(text: str, min_length: int = 20) -> List[str]:
    """
    Split raw contract text into a cleaned list of clauses.

    Strategy (applied in order):
      1. Split on numbered-section headings.
      2. Split each fragment on semicolons.
      3. Split remaining fragments on sentence boundaries.
      4. Keep only clauses with len > min_length.

    Args:
        text:       The full raw contract text (ideally from pdf_extractor).
        min_length: Minimum character count to keep a clause (default 20).

    Returns:
        A list of cleaned clause strings.
    """
    if not text or not text.strip():
        return []

    text = normalize_contract_text(text)

    # ── Step 1: split on numbered section headings ─────────────────
    # Insert a unique delimiter before each section marker
    delimited = _SECTION_PATTERN.sub(r"\n<SPLIT>\g<0>", text)
    fragments = delimited.split("<SPLIT>")

    # ── Step 2: split on semicolons ────────────────────────────────
    semi_fragments = []
    for frag in fragments:
        semi_fragments.extend(frag.split(";"))

    # ── Step 3: split on sentence boundaries ───────────────────────
    clauses = []
    for frag in semi_fragments:
        parts = _SENTENCE_BOUNDARY.split(frag)
        clauses.extend(parts)

    # ── Step 4: clean and filter ───────────────────────────────────
    cleaned = []
    for clause in clauses:
        c = _clean_clause_artifacts(clause)
        if _ARTIFACT_PREFIX_PATTERN.match(c):
            continue
        if len(c) > min_length:
            cleaned.append(c)

    unique, _ = deduplicate_clauses(cleaned)
    return unique


# ── Stand-alone usage / demo ────────────────────────────────────────
if __name__ == "__main__":
    import sys
    import os

    # Allow import of sibling modules when run directly
    sys.path.insert(0, os.path.dirname(__file__))
    from pdf_extractor import extract_text_from_pdf

    if len(sys.argv) < 2:
        # Default: run on both sample contracts
        pdfs = [
            "data/sample_contracts/software_services_agreement.pdf",
            "data/sample_contracts/mutual_nda.pdf",
        ]
    else:
        pdfs = sys.argv[1:]

    for pdf_path in pdfs:
        if not os.path.exists(pdf_path):
            print(f"Skipping (not found): {pdf_path}")
            continue

        text = extract_text_from_pdf(pdf_path)
        clauses = segment_clauses(text)

        print(f"\n{'='*60}")
        print(f"File   : {pdf_path}")
        print(f"Clauses: {len(clauses)}")
        print(f"{'='*60}")
        for i, cl in enumerate(clauses, 1):
            print(f"  [{i:2d}] {cl[:120]}{'…' if len(cl) > 120 else ''}")
