
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
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Convert MD to HTML (enable tables extension)
    try:
        html_text = markdown.markdown(text, extensions=['tables'])
    except:
        # Fallback if extensions fail
        html_text = markdown.markdown(text)

    # Add styling for a professional look
    html_content = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #333; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-top: 0; }}
        h2 {{ color: #34495e; margin-top: 25px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        h3 {{ color: #5d6d7e; margin-top: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; table-layout: fixed; }} /* Fixed layout helps with wrapping */
        th, td {{ border: 1px solid #bdc3c7; padding: 5px; text-align: left; vertical-align: top; font-size: 10pt; word-wrap: break-word; }} /* Smaller font, less padding */
        th {{ background-color: #ecf0f1; font-weight: bold; color: #2c3e50; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        ul {{ margin-top: 5px; }}
        li {{ margin-bottom: 5px; }}
        strong {{ color: #e74c3c; }} /* Highlight key risks in red/bold style */
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
    # Source file
    base_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    input_path = os.path.join(base_dir, "Client_Summary_Transfer_Plan.md")
    
    # Output file
    output_path = os.path.join(base_dir, "Client_Summary_Transfer_Plan.pdf")

    print(f"Converting {input_path} to {output_path}...")
    try:
        content_to_pdf(input_path, output_path)
    except Exception as e:
        print(f"FAILED: {e}")
