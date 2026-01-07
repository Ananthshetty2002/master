import sys
import subprocess
import os

pkg_markdown = "markdown"
pkg_xhtml2pdf = "xhtml2pdf"

def install(package):
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import markdown
except ImportError:
    install(pkg_markdown)
    import markdown

try:
    from xhtml2pdf import pisa
except ImportError:
    install(pkg_xhtml2pdf)
    from xhtml2pdf import pisa

def content_to_pdf(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Convert MD to HTML (enable tables extension)
    try:
        html_text = markdown.markdown(text, extensions=['tables', 'fenced_code'])
    except:
        html_text = markdown.markdown(text)

    # Add styling
    html_content = f"""
    <html>
    <head>
    <style>
        @page {{ margin: 2cm; }}
        body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #333; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-top: 0; }}
        h2 {{ color: #34495e; margin-top: 25px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        h3 {{ color: #5d6d7e; margin-top: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #bdc3c7; padding: 10px; text-align: left; vertical-align: top; }}
        th {{ background-color: #ecf0f1; font-weight: bold; color: #2c3e50; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        blockquote {{ border-left: 4px solid #3498db; background-color: #eaf2f8; padding: 10px; margin: 15px 0; color: #2980b9; }}
        strong {{ color: #2980b9; }} 
    </style>
    </head>
    <body>
    {html_text}
    </body>
    </html>
    """

    # Convert HTML to PDF
    with open(output_file, "wb") as result_file:
        pisa_status = pisa.CreatePDF(html_content, dest=result_file)

    if pisa_status.err:
        print(f"Error converting to PDF: {pisa_status.err}")
    else:
        print(f"Successfully created: {output_file}")

if __name__ == "__main__":
    input_path = r"C:\Users\IV-UDP-DT-0122\.gemini\antigravity\brain\7e383187-f2e0-4052-97a2-e0b6d0b0a022\waste_analysis_report.md"
    output_path = r"C:\Users\IV-UDP-DT-0122\.gemini\antigravity\brain\7e383187-f2e0-4052-97a2-e0b6d0b0a022\Waste_Analysis_Report_Dec11.pdf"

    print(f"Converting {input_path} to {output_path}...")
    try:
        content_to_pdf(input_path, output_path)
    except Exception as e:
        print(f"FAILED: {e}")
