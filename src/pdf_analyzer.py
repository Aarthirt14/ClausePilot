import pdfplumber
import os
import argparse
import sys
# Import from predict to reuse loading logic
from predict import load_model_assets, predict_risk

def analyze_pdf(pdf_path, model, tfidf):
    """
    Extracts text from PDF and analyzes each paragraph for risk.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found.")
        return
        
    print(f"Analyzing PDF: {pdf_path}...")
    findings = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
                
            # Split by double newline or common paragraph starters to approximate clauses
            paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
            
            for p in paragraphs:
                label, confidence = predict_risk(p, model, tfidf)
                if label != 'Neutral':
                    findings.append({
                        'page': i + 1,
                        'text': p[:200] + "...",
                        'risk_label': label,
                        'confidence': confidence
                    })
                    
    return findings

def main():
    parser = argparse.ArgumentParser(description="Analyze a contract PDF for risks.")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file.")
    args = parser.parse_args()
    
    try:
        model, tfidf = load_model_assets()
        findings = analyze_pdf(args.pdf_path, model, tfidf)
        
        if not findings:
            print("\nNo significant risks detected.")
            return
            
        print(f"\n--- Risk Report ({len(findings)} clauses flagged) ---")
        for f in findings:
            print(f"\n[Page {f['page']}] [{f['risk_label']}] (Conf: {f['confidence']:.2f})")
            print(f"Text: {f['text']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
