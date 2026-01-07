import os
import glob
import sys
import subprocess

# Define base directory
base_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"

def install_and_import(package):
    try:
        import importlib
        importlib.import_module(package)
    except ImportError:
        print(f"{package} not found. installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    finally:
        globals()[package] = importlib.import_module(package)

def read_pdfs():
    # Try to import pypdf, install if missing
    try:
        import pypdf
    except ImportError:
        print("pypdf not found. Installing...")
        try:
             subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
             import pypdf
        except Exception as e:
            print(f"Failed to install pypdf: {e}")
            return

    output_file = os.path.join(base_dir, "pdf_analysis_summary.txt")
    pdf_files = glob.glob(os.path.join(base_dir, "*.pdf"))

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("PDF FILE ANALYSIS\n")
        f.write("=================\n\n")

        if not pdf_files:
            f.write("No PDF files found in the directory.\n")
            return

        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            f.write(f"--- File: {filename} ---\n")
            try:
                reader = pypdf.PdfReader(pdf_path)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
                
                f.write(f"Page Count: {len(reader.pages)}\n")
                if "low stockout.pdf" in filename.lower() or "summary report1" in filename.lower():
                     f.write("FULL TEXT EXTRACT:\n")
                     f.write(text_content)
                else:
                     f.write(f"Extracted Text Preview (First 1000 chars):\n")
                     f.write(text_content[:1000])
                f.write("\n\n" + "-"*30 + "\n\n")
            except Exception as e:
                f.write(f"Error reading PDF: {e}\n\n")

if __name__ == "__main__":
    read_pdfs()
    print("PDF analysis complete.")
