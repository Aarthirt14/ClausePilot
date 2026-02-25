"""
scripts/create_sample_pdfs.py
------------------------------
Creates 2 realistic sample contract PDFs in data/sample_contracts/
for testing the pdf_extractor module.
"""
from fpdf import FPDF
import os

os.makedirs("data/sample_contracts", exist_ok=True)

# ── Contract 1: Software Services Agreement ────────────────────────
c1_text = [
    ("SOFTWARE SERVICES AGREEMENT", True),
    ("", False),
    ("This Software Services Agreement (the \"Agreement\") is entered into as of"
     " January 1, 2025, by and between TechCorp Inc., a Delaware corporation"
     " (\"Provider\"), and Acme Ltd., a California corporation (\"Client\").", False),
    ("", False),
    ("1. SERVICES", True),
    ("Provider agrees to deliver software development services as described in"
     " Exhibit A attached hereto. Services shall commence on February 1, 2025"
     " and continue for a period of twelve (12) months unless earlier terminated.", False),
    ("", False),
    ("2. PAYMENT TERMS", True),
    ("Client shall pay Provider a monthly retainer of USD 15,000 (fifteen thousand"
     " dollars), due on the first business day of each calendar month. Late payments"
     " shall accrue interest at 1.5% per month.", False),
    ("", False),
    ("3. TERMINATION", True),
    ("Either party may terminate this Agreement upon thirty (30) days written notice."
     " Provider may terminate immediately upon Client's material breach, including"
     " non-payment. Upon termination, Client shall pay all outstanding invoices.", False),
    ("", False),
    ("4. LIMITATION OF LIABILITY", True),
    ("In no event shall either party's aggregate liability exceed the total fees paid"
     " in the three (3) months preceding the claim. Neither party shall be liable for"
     " incidental, consequential, or punitive damages.", False),
    ("", False),
    ("5. CONFIDENTIALITY", True),
    ("Each party agrees to keep the other's proprietary information strictly"
     " confidential. This obligation survives termination for a period of five (5) years.", False),
    ("", False),
    ("6. GOVERNING LAW", True),
    ("This Agreement shall be governed by the laws of the State of Delaware,"
     " without regard to conflict of law principles.", False),
]

# ── Contract 2: Non-Disclosure Agreement ──────────────────────────
c2_text = [
    ("MUTUAL NON-DISCLOSURE AGREEMENT", True),
    ("", False),
    ("This Mutual Non-Disclosure Agreement (\"NDA\") is entered into as of March 15,"
     " 2025, between GlobalVentures LLC (\"Party A\") and InnovateCo Inc. (\"Party B\").", False),
    ("", False),
    ("1. DEFINITION OF CONFIDENTIAL INFORMATION", True),
    ("\"Confidential Information\" means any non-public information disclosed by one"
     " party to the other, including technical data, trade secrets, business plans,"
     " financial projections, customer lists, and proprietary algorithms.", False),
    ("", False),
    ("2. OBLIGATIONS", True),
    ("Each party shall: (a) hold the other's Confidential Information in strict"
     " confidence; (b) not disclose it to any third party without prior written consent;"
     " (c) use it solely for the purpose of evaluating a potential business relationship.", False),
    ("", False),
    ("3. TERM", True),
    ("This Agreement shall remain in force for a period of three (3) years from the"
     " Effective Date. Confidentiality obligations survive termination.", False),
    ("", False),
    ("4. EXCLUSIONS", True),
    ("Obligations do not apply to information that: (a) is or becomes publicly known;"
     " (b) was rightfully known before disclosure; (c) is independently developed;"
     " or (d) is required to be disclosed by law.", False),
    ("", False),
    ("5. REMEDIES", True),
    ("Breach of this Agreement may cause irreparable harm for which monetary damages"
     " would be insufficient. Each party shall be entitled to seek injunctive relief"
     " without the requirement of posting bond.", False),
    ("", False),
    ("6. ASSIGNMENT", True),
    ("Neither party may assign its rights or obligations under this Agreement without"
     " the prior written consent of the other party. Any assignment in violation hereof"
     " shall be null and void.", False),
]

def make_pdf(rows, filename):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(20, 15, 20)

    for text, bold in rows:
        if not text:
            pdf.ln(4)
            continue
        pdf.set_font("Helvetica", style="B" if bold else "", size=11 if bold else 10)
        pdf.multi_cell(0, 6, text)
        pdf.ln(1)

    pdf.output(filename)
    print(f"Created: {filename}")

make_pdf(c1_text, "data/sample_contracts/software_services_agreement.pdf")
make_pdf(c2_text, "data/sample_contracts/mutual_nda.pdf")
print("Done.")
