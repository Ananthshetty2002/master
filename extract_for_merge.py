import pypdf
import os

def extract_content(file_path):
    print(f"Extracting: {file_path}")
    reader = pypdf.PdfReader(file_path)
    content = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        content.append(f"--- PAGE {i+1} ---\n{text}")
    return "\n".join(content)

if __name__ == "__main__":
    doc17_text = extract_content("Document 17 (6).pdf")
    with open("doc17_full_text.txt", "w", encoding="utf-8") as f:
        f.write(doc17_text)
        
    detector_text = extract_content("SHRINKAGE DETECTOR.pdf")
    with open("detector_full_text.txt", "w", encoding="utf-8") as f:
        f.write(detector_text)
    
    print("Done extracting.")
