import os
import re
from pypdf import PdfReader

def clean_report():
    base_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    pdf_path = os.path.join(base_dir, "Shrinkage & Spoilage Alert-Network Summary Report1.pdf")
    output_md_path = os.path.join(base_dir, "Cleaned_Network_Summary_Report.md")

    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    # Define sections to remove
    # 1. Rankings sections to remove
    rank_sections_to_remove = [
        r"Immediate Actions \(By EOD 12/27\):.*?(?=Rank \d+:|🟡|📊|$)",
        r"Owner:.*?(?=Rank \d+:|🟡|📊|$)",
        r"Timeline:.*?(?=Rank \d+:|🟡|📊|$)",
        r"Key Finding:.*?(?=Rank \d+:|🟡|📊|$)",
        r"Root Cause Hypothesis:.*?(?=Rank \d+:|🟡|📊|$)",
        r"⚠\s+ANOMALY DETECTED:.*?(?=Rank \d+:|🟡|📊|$)",
        r"EMERGENCY Actions \(Within Next 4 Hours\):.*?(?=Rank \d+:|🟡|📊|$)",
        r"Secondary Actions \(By EOD\):.*?(?=Rank \d+:|🟡|📊|$)",
    ]

    cleaned_text = full_text

    # Remove ranks sub-sections
    for pattern in rank_sections_to_remove:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.DOTALL | re.IGNORECASE)

    # 2. Large sections to remove from financial impact onwards
    large_sections_to_remove = [
        r"📊\s+FINANCIAL IMPACT ANALYSIS.*",
        r"Scenario Analysis.*",
        r"🎯\s+IMMEDIATE ACTION PLAN.*",
        r"📋\s+ROLE ASSIGNMENTS & ACCOUNTABILITY.*",
        r"🔧\s+SYSTEMIC IMPROVEMENTS.*",
        r"📈\s+EXPECTED OUTCOMES.*",
        r"CONCLUSION.*",
    ]

    for pattern in large_sections_to_remove:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.DOTALL | re.IGNORECASE)

    # Clean up multiple newlines
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # Remove leading/trailing whitespace
    cleaned_text = cleaned_text.strip()

    # Add a title
    cleaned_text = "# CLEANED NETWORK SUMMARY REPORT\n\n" + cleaned_text

    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print(f"Cleaned report saved to: {output_md_path}")
    
    # Try to convert to PDF
    try:
        import markdown
        from xhtml2pdf import pisa
        from unidecode import unidecode
        
        output_pdf_path = os.path.join(base_dir, "Cleaned_Network_Summary_Report.pdf")
        
        # Normalize text to ASCII to avoid encoding issues with xhtml2pdf
        ascii_text = unidecode(cleaned_text)
        html_text = markdown.markdown(ascii_text, extensions=['tables'])
        
        # Simple professional styling
        html_content = f"""
        <html>
        <head>
        <style>
            body {{ font-family: Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.4; color: #333; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 8px; margin-top: 0; }}
            h2 {{ color: #34495e; margin-top: 20px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #bdc3c7; padding: 6px; text-align: left; vertical-align: top; }}
            th {{ background-color: #ecf0f1; font-weight: bold; }}
            .status-red {{ color: #e74c3c; font-weight: bold; }}
            .alert {{ color: #e67e22; font-weight: bold; }}
        </style>
        </head>
        <body>
        {html_text}
        </body>
        </html>
        """
        
        with open(output_pdf_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
            
        if not pisa_status.err:
            print(f"Cleaned PDF report saved to: {output_pdf_path}")
        else:
            print(f"Error converting to PDF: {pisa_status.err}")
            
    except ImportError as e:
        print(f"Skipping PDF conversion due to missing package: {e}")
    except Exception as e:
        print(f"Error during PDF conversion: {e}")

if __name__ == "__main__":
    clean_report()
