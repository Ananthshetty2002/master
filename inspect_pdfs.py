import pypdf
import os

def inspect_pdf(file_path):
    print(f"Inspecting: {file_path}")
    if not os.path.exists(file_path):
        print("File not found.")
        return
    
    try:
        reader = pypdf.PdfReader(file_path)
        print(f"Number of pages: {len(reader.pages)}")
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if "EXECUTIVE SUMMARY" in text.upper():
                print(f"Found 'EXECUTIVE SUMMARY' on page {i+1}")
                # Print a bit of context
                start_idx = text.upper().find("EXECUTIVE SUMMARY")
                print(f"Context: {text[max(0, start_idx-50):min(len(text), start_idx+100)]}")
            
            # Print first 100 characters of each page for style/content hint
            print(f"Page {i+1} start: {text[:100].replace('\n', ' ')}")
            
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    inspect_pdf("SHRINKAGE DETECTOR.pdf")
    print("-" * 20)
    inspect_pdf("Document 17 (6).pdf")
