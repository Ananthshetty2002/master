import pypdf

def extract_full_text(file_path, output_path):
    reader = pypdf.PdfReader(file_path)
    with open(output_path, "w", encoding="utf-8") as f:
        for page in reader.pages:
            f.write(page.extract_text())
            f.write("\n" + "="*20 + "\n")

if __name__ == "__main__":
    extract_full_text("Document 17 (6).pdf", "extracted_document_17.txt")
    extract_full_text("SHRINKAGE DETECTOR.pdf", "extracted_shrinkage_detector.txt")
