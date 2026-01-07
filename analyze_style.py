import fitz # PyMuPDF

def analyze_pdf_style(file_path):
    print(f"Analyzing style for: {file_path}")
    doc = fitz.open(file_path)
    page = doc[0] # Focus on the first page where Executive Summary is
    
    # Get all text spans with formatting info
    dict = page.get_text("dict")
    blocks = dict["blocks"]
    
    for b in blocks:
        if "lines" in b:
            for l in b["lines"]:
                for s in l["spans"]:
                    text = s["text"]
                    if "EXECUTIVE SUMMARY" in text.upper():
                        print(f"Found match: '{text}'")
                        print(f"Font: {s['font']}, Size: {s['size']}, Color: {s['color']}")
                        # Also print some body text for comparison
                    elif len(text.strip()) > 20:
                        # Probably body text
                        if "font" in s:
                             print(f"Sample Text: '{text[:30]}...' Font: {s['font']}, Size: {s['size']}")
                             return # Just need one sample for now

if __name__ == "__main__":
    try:
        analyze_pdf_style("SHRINKAGE DETECTOR.pdf")
    except Exception as e:
        print(f"Error: {e}")
