import os

def clean_report():
    input_file = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage\pdf_analysis_summary.txt"
    output_file = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage\Updated_Network_Summary_Report.md"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the relevant section for the report
    start_marker = "--- File: Shrinkage & Spoilage Alert-Network Summary Report1.pdf ---"
    end_marker = "--- File: Shrinkage (theftmisuse) - staff + audits.pdf ---"
    
    if start_marker not in content:
        print("Start marker not found")
        return
        
    report_text = content.split(start_marker)[1]
    if end_marker in report_text:
        report_text = report_text.split(end_marker)[0]
    
    # Remove "FULL TEXT EXTRACT:" line
    report_text = report_text.replace("FULL TEXT EXTRACT:", "")
    
    lines = report_text.split('\n')
    cleaned_lines = []
    skip_mode = False
    
    # Define sections to skip entirely
    skip_sections = [
        "FINANCIAL IMPACT ANALYSIS",
        "Scenario Analysis",
        "IMMEDIATE ACTION PLAN",
        "ROLE ASSIGNMENTS",
        "SYSTEMIC IMPROVEMENTS",
        "EXPECTED OUTCOMES",
        "CONCLUSION"
    ]
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check if we should start skipping a major section
        if any(sec in stripped for sec in skip_sections):
            skip_mode = True
            continue
            
        # Stop skip mode if we hit a new major section header (which we are not skipping)
        # However, in this specific request, almost everything after Rank 10 is skipped.
        # But let's be careful. If a line starts with Rank or Status, we might want to keep it if it's within the first part.
        
        if skip_mode:
            continue
            
        # Filter specific lines within the rankings
        if "Immediate Actions" in stripped:
            continue
        if "Owner:" in stripped:
            continue
        if "Timeline:" in stripped:
            continue
        if "EMERGENCY Actions" in stripped:
            continue
        if "Secondary Actions" in stripped:
            continue
        if "Key Finding:" in stripped and "Rank 4:" in lines[i-1 if i>0 else 0]:
             continue
        if "Root Cause Hypothesis:" in stripped and "Rank 5:" in lines[i-1 if i>0 else 0]:
             continue
        if "ANOMALY DETECTED:" in stripped and "Rank 7:" in lines[i-1 if i>0 else 0]:
             continue
        
        # Specific bullet points under Actions to remove
        if stripped.startswith("- ") or stripped.startswith("* "):
            # Check if this is under an "Actions" section we just removed
            # We can check a few lines back
            prev_lines = "\n".join(lines[max(0, i-5):i])
            if "Actions" in prev_lines:
                continue
        
        cleaned_lines.append(line)
    
    # Final cleanup of any dangling artifacts
    final_output = "\n".join(cleaned_lines)
    
    # Manual surgical removals for specific patterns that might have survived
    # Removing action blocks
    import re
    final_output = re.sub(r'Immediate Actions \(By EOD 12/27\):.*?(?=\nRank|\n📊|\n\n)', '', final_output, flags=re.DOTALL)
    final_output = re.sub(r'EMERGENCY Actions \(Within Next 4 Hours\):.*?(?=\nSecondary Actions|\nOwner|\nRank|\n\n)', '', final_output, flags=re.DOTALL)
    final_output = re.sub(r'Secondary Actions \(By EOD\):.*?(?=\nOwner|\nRank|\n\n)', '', final_output, flags=re.DOTALL)
    final_output = re.sub(r'Owner: .*?\n', '', final_output)
    final_output = re.sub(r'Timeline: .*?\n', '', final_output)
    
    # Removing rank-specific findings
    final_output = re.sub(r'Key Finding: This location shows excessive water.*?Timeline:.*?hours', '', final_output, flags=re.DOTALL)
    final_output = re.sub(r'Root Cause Hypothesis: High-value aluminum.*?Timeline:.*?hours', '', final_output, flags=re.DOTALL)
    final_output = re.sub(r'⚠  ANOMALY DETECTED: USB cable.*?Timeline:.*?hours', '', final_output, flags=re.DOTALL)

    # Removing the footer/conclusion that starts with "Root cause complexity"
    final_output = final_output.split("Root cause complexity")[0]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# SHRINKAGE & SPOILAGE ALERT - NETWORK SUMMARY REPORT\n\n")
        f.write(final_output.strip())

    print(f"Generated {output_file}")

if __name__ == "__main__":
    clean_report()
