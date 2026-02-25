"""
src/pdf_extractor.py
--------------------
Utility for extracting clean raw text from contract PDF files.
"""
import re
import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract and clean the full text of a contract PDF.

    Steps:
    1. Open the PDF with pdfplumber.
    2. Extract text from every page.
    3. Strip extra whitespace: collapse runs of spaces/tabs,
       preserve meaningful paragraph breaks (double newlines),
       and strip leading/trailing whitespace.

    Args:
        pdf_path: Absolute or relative path to the PDF file.

    Returns:
        A single cleaned string containing the full contract text.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if no text could be extracted.
    """
    import os
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    page_texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                page_texts.append(page_text)

    if not page_texts:
        raise ValueError(f"No extractable text found in: {pdf_path}")

    # Join pages with a paragraph separator
    raw = "\n\n".join(page_texts)

    # --- Cleaning pipeline ---
    # 1. Replace tabs with spaces
    text = raw.replace("\t", " ")

    # 2. Collapse multiple spaces / non-newline whitespace within a line
    text = re.sub(r"[ \t]+", " ", text)

    # 3. Remove trailing whitespace on each line
    text = "\n".join(line.rstrip() for line in text.splitlines())

    # 4. Collapse 3+ consecutive newlines into exactly 2 (paragraph break)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 5. Strip leading / trailing whitespace from the whole document
    text = text.strip()

    return text


# ──────────────────────────────────────────────
# Stand-alone usage
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <path/to/contract.pdf>")
        sys.exit(1)

    path = sys.argv[1]
    extracted = extract_text_from_pdf(path)

    print(f"\n{'='*60}")
    print(f"File      : {path}")
    print(f"Characters: {len(extracted):,}")
    print(f"Words     : {len(extracted.split()):,}")
    print(f"{'='*60}")
    print("\n--- First 1,000 characters ---\n")
    print(extracted[:1_000])
