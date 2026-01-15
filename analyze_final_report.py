import os
import pypdf

WORK_DIR = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
PDF_FILE = os.path.join(WORK_DIR, "final reportath.htm.pdf")
OUTPUT_FILE = os.path.join(WORK_DIR, "final_report_htm_content.txt")

def analyze_report():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        out.write("ANALYSIS OF FINAL REPORT\n")
        out.write("========================\n\n")

        # 1. Analyze PDF
        if os.path.exists(PDF_FILE):
            out.write(f"--- CONTENT OF {os.path.basename(PDF_FILE)} ---\n")
            try:
                reader = pypdf.PdfReader(PDF_FILE)
                out.write(f"Total Pages: {len(reader.pages)}\n\n")
                
                text = ""
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    # Capture first few pages fully, skip middle if too long
                    if i < 3:
                        out.write(f"--- Page {i+1} ---\n{page_text}\n\n")
                
                out.write("\n--- Full PDF Text Summary ---\n")
                out.write(f"Total characters: {len(text)}\n")
            except Exception as e:
                out.write(f"Error reading PDF: {e}\n")
        else:
            out.write(f"PDF File not found: {PDF_FILE}\n")

    print(f"Analysis saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    analyze_report()
