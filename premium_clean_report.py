import os
import re
import markdown
from xhtml2pdf import pisa
from unidecode import unidecode

def premium_clean_report():
    base_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    input_file = os.path.join(base_dir, "pdf_analysis_summary.txt")
    output_md_path = os.path.join(base_dir, "Updated_Network_Summary_Report_Premium.md")
    output_pdf_path = os.path.join(base_dir, "Cleaned_Network_Summary_Report_v2.pdf")

    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract the relevant section
    start_marker = "--- File: Shrinkage & Spoilage Alert-Network Summary Report1.pdf ---"
    end_marker = "--- File: Shrinkage (theftmisuse) - staff + audits.pdf ---"
    
    if start_marker not in content:
        print("Start marker not found")
        return
        
    report_text = content.split(start_marker)[1]
    if end_marker in report_text:
        report_text = report_text.split(end_marker)[0]
    
    report_text = report_text.replace("FULL TEXT EXTRACT:", "").strip()

    lines = [l.strip() for l in report_text.split('\n')]
    
    final_md_parts = []
    
    # 1. Header reconstruction
    final_md_parts.append("# SHRINKAGE & SPOILAGE ALERT - NETWORK SUMMARY REPORT")
    final_md_parts.append("**Report Date: December 27, 2025 | 4:00 PM IST Prepared for: Client**")
    final_md_parts.append("### 🚨  CRITICAL ALERT - NETWORK-WIDE LOSS EXPOSURE")
    
    # 2. Dashboard Table
    final_md_parts.append("## Executive Summary Dashboard")
    final_md_parts.append("| Metric | Value | Status |")
    final_md_parts.append("| :--- | :--- | :--- |")
    
    dashboard_data = [
        ("Total Locations Analyzed", "22 micromarkets", "📊  FULL NETWORK"),
        ("CRITICAL Sites (Immediate Action)", "10 locations", "🔴  URGENT"),
        ("MONITOR Sites (Next 48H Action)", "12 locations", "🟡  HIGH"),
        ("Total Shrinkage (Missing Units)", "2,413 units", "💰  $96,520"),
        ("Total Spoilage at Risk", "487.5 units", "💰  $11,850"),
        ("Combined Loss Exposure", "$108,370", "🚨  CRITICAL"),
        ("Estimated Weekly Impact", "$379,296", "📈  PROJECTED"),
        ("Estimated Annual Impact", "$19,700,000+", "⚠  EXISTENTIAL")
    ]
    for m, v, s in dashboard_data:
        final_md_parts.append(f"| {m} | {v} | {s} |")

    final_md_parts.append("## 🔴  CRITICAL SHRINKAGE & SPOILAGE SITES")
    final_md_parts.append("*(IMMEDIATE ACTION REQUIRED)*")

    # 3. Rankings parsing
    # Use split but keep the rank prefix and location name together
    blocks = re.split(r"(Rank \d+:.*?\n)", report_text)
    
    for i in range(1, len(blocks), 2):
        rank_header = blocks[i].strip()
        rank_content = blocks[i+1]
        
        # Determine where to stop (before Monitor Sites or Financial Analysis)
        if "🟡  MONITOR SITES" in rank_content or "📊  FINANCIAL IMPACT ANALYSIS" in rank_content:
            rank_content = re.split(r"🟡  MONITOR SITES|📊  FINANCIAL IMPACT ANALYSIS", rank_content)[0]
        
        lines = [l.strip() for l in rank_content.split('\n') if l.strip()]
        
        cleaned_rank_lines = [f"## {rank_header}"]
        
        profile_items = []
        spoilage_items = []
        spoilage_action = None
        status_line = ""
        
        section = None
        
        for line in lines:
            if line.startswith("Status:"):
                # Clean up status line and capture
                status_val = line.replace("Status:", "").strip()
                status_line = f"> **Status:** {status_val}"
                continue
            
            # Detect sections
            if "Pro le:" in line or "Profile:" in line:
                section = 'profile'
                continue
            if any(h in line for h in ["Spoilage Risk", "SPOILAGE ALERT", "Spoilage Status"]):
                section = 'spoilage'
                if ":" in line and any(x in line for x in ["Product", "Stock", "Risk"]):
                    spoilage_items.append(f"- {line}")
                continue
            if "Actions (" in line:
                section = 'actions'
                continue
            if any(h in line for h in ["Owner:", "Timeline:", "Key Finding:", "Root Cause", "ANOMALY"]):
                section = 'ignored'
                continue
            
            # Extract data
            if section == 'profile':
                if any(x in line for x in ["Top shrinkage", "Pattern", "loss", "Weekly"]):
                    profile_items.append(f"- {line}")
                elif profile_items and len(line) < 150:
                    profile_items[-1] = profile_items[-1] + " " + line
            elif section == 'spoilage':
                if line.startswith("Action:"):
                    spoilage_action = line
                elif any(x in line for x in ["Product:", "Projected waste", "expiry", "Risk:", "single spoilage"]):
                    spoilage_items.append(f"- {line}")
                elif spoilage_items and len(line) < 150:
                    spoilage_items[-1] = spoilage_items[-1] + " " + line
            elif section == 'actions':
                if not spoilage_action:
                    if any(act in line.lower() for act in ["bundle", "transfer", "discount", "clearance", "signage"]):
                        spoilage_action = f"Action: {line}"

        if status_line:
            cleaned_rank_lines.append(status_line)
        
        cleaned_rank_lines.append("### Shrinkage Profile:")
        cleaned_rank_lines.extend(profile_items if profile_items else ["- (No detailed breakdown available)"])
        
        if spoilage_items:
            # Clean up redundant Spoilage Risk text in items
            clean_spoil_items = [item.replace("Spoilage Risk:", "").strip("- ").strip() for item in spoilage_items]
            clean_spoil_items = [f"- {item}" for item in clean_spoil_items if item]
            
            cleaned_rank_lines.append("### Spoilage Risk:")
            cleaned_rank_lines.extend(clean_spoil_items)
            if spoilage_action:
                # Highlight the action
                spoil_act_clean = spoilage_action.replace("Action:", "").strip()
                cleaned_rank_lines.append(f"- **Action: {spoil_act_clean}**")
        else:
            cleaned_rank_lines.append("### Spoilage Status:")
            cleaned_rank_lines.append("- ✅ No immediate spoilage risk")
            
        final_md_parts.append("\n".join(cleaned_rank_lines))

    # 4. Monitor Sites Table Reconstruction

    # 4. Monitor Sites Table Reconstruction
    final_md_parts.append("## 🟡  MONITOR SITES (Next 48 Hours)")
    final_md_parts.append("| Rank | Location | Shrinkage | Spoilage Risk | Action | Timeline |")
    final_md_parts.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    
    monitor_data = [
        ("11", "Lincoln Hotel Monterey Park", "77 units", "41.7 (Milk, 3 days)", "Bundle/Discount Milk", "By 12/29 AM"),
        ("12", "Desert Palms Market", "62 units", "40.2 (Yogurt, 4 days)", "Bundle Yogurt", "By 12/29 AM"),
        ("13", "Best Western Norwalk Inn", "52 units", "43.5 (Sandwich, 3 days)", "Bundle Sandwich", "By 12/29 AM"),
        ("14", "SureStay Plus Upland", "40 units", "45.6 (Milk, 1 day)", "Transfer Milk URGENTLY", "By 12/28 PM"),
        ("15", "Fair eld Anaheim", "34 units", "47.2 (Yogurt, 3 days)", "Bundle Yogurt", "By 12/29 AM")
    ]
    for r in monitor_data:
        final_md_parts.append(f"| {' | '.join(r)} |")
        
    # 5. Conclusion Summary (Requested by user)
    final_md_parts.append("## CONCLUSION")
    final_md_parts.append("The network faces a **$108,370** immediate loss exposure driven by:")
    final_md_parts.append("- **Shrinkage dominance**: $96,520 (89% of loss) across 10 critical sites")
    final_md_parts.append("- **Spoilage concentration**: $11,850 (11% of loss) with 2 emergency items (LAX Sandwich $1,916, Thousand Oaks Milk $304)")

    # Combine
    final_md = "\n\n".join(final_md_parts)

    # Save MD
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(final_md)

    print(f"Premium Cleaned Markdown report saved to: {output_md_path}")

    # Convert to PDF with Premium CSS
    try:
        ascii_text = unidecode(final_md)
        html_text = markdown.markdown(ascii_text, extensions=['tables'])
        
        html_content = f"""
        <html>
        <head>
        <style>
            @page {{ size: letter; margin: 0.75in; }}
            body {{ font-family: 'Helvetica', 'Arial', sans-serif; font-size: 10pt; line-height: 1.4; color: #333; }}
            h1 {{ color: #1a5276; border-bottom: 2px solid #1a5276; padding-bottom: 8px; margin-bottom: 15px; text-transform: uppercase; }}
            h2 {{ color: #1f618d; margin-top: 25px; border-bottom: 1px solid #d4e6f1; padding-bottom: 5px; }}
            h3 {{ color: #2e86c1; margin-top: 15px; margin-bottom: 5px; font-size: 11pt; }}
            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
            th, td {{ border: 1px solid #ebf5fb; padding: 8px; text-align: left; vertical-align: top; }}
            th {{ background-color: #2e86c1; color: white; font-weight: bold; border: 1px solid #1f618d; }}
            tr:nth-child(even) {{ background-color: #f7fbfe; }}
            blockquote {{ border-left: 5px solid #e74c3c; background-color: #fdf2f2; padding: 10px; margin: 10px 0; font-style: normal; }}
            .footer {{ position: fixed; bottom: 0; left: 0; right: 0; text-align: center; font-size: 8pt; color: #999; border-top: 1px solid #eee; padding-top: 5px; }}
        </style>
        </head>
        <body>
            {html_text}
            <div class="footer">Confidential Loss Prevention Report - Generated on 2025-12-29</div>
        </body>
        </html>
        """
        
        with open(output_pdf_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
            
        if not pisa_status.err:
            print(f"Premium Cleaned PDF report saved to: {output_pdf_path}")
        else:
            print(f"Error converting to PDF: {pisa_status.err}")
            
    except Exception as e:
        print(f"Error during PDF conversion: {e}")

if __name__ == "__main__":
    premium_clean_report()
