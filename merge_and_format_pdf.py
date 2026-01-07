from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def create_merged_pdf(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=15,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#2C3E50")
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#2C3E50"),
        textTransform='uppercase'
    )
    
    subheading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#34495E")
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    small_body_style = ParagraphStyle(
        'SmallBody',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        spaceAfter=4,
        fontName='Helvetica'
    )

    story = []

    # --- Header ---
    story.append(Paragraph("MICROMARKET SHRINKAGE ANALYSIS & MITIGATION STRATEGY REPORT", title_style))
    story.append(Paragraph("Report Date: December 30, 2025", ParagraphStyle('DateStyle', parent=body_style, alignment=TA_CENTER)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2C3E50"), spaceBefore=10, spaceAfter=20))

    # =========================================================================
    # SECTION 1: DOCUMENT 17 - STRATEGIC FRAMEWORK
    # =========================================================================
    story.append(Paragraph("PHASE 0: LOSS PREVENTION PROJECT – STRATEGIC SCOPE & AUTOMATION FRAMEWORK", heading_style))
    story.append(Spacer(1, 5))
    
    story.append(Paragraph("<b>Problem Statement</b>", subheading_style))
    story.append(Paragraph("Develop an autonomous Shrinkage Detector Agent that analyzes inventory data from two time points (e.g., yesterday and today) alongside recorded sales to identify discrepancies indicating shrinkage. The agent should calculate unaccounted inventory losses, detect affected locations and products, and rank them by severity to enable focused loss prevention actions.", body_style))
    
    story.append(Paragraph("<b>Project Metadata</b>", subheading_style))
    meta_data = [
        "<b>Shrinkage Detector Agent:</b> Assigned to Ananth Shetty",
        "<b>Status:</b> LIVE n8n Workflow (5 Nodes → CEO Briefing)",
        "<b>Data Sources:</b> Transaction Report (Sales Register), Inventory Snapshots (Stock Analysis), Adjustment logs (pilot_shrink_log.csv)",
        "<b>Project Scope:</b> 193 micromarkets analyzed → 150 identified with shrinkage"
    ]
    for m in meta_data:
        story.append(Paragraph(m, body_style))
        
    story.append(Paragraph("<b>Phase 1: Core Calculation Logic</b>", subheading_style))
    formulas = [
        "• <b>Shrinkage Formula:</b> (Opening Inventory - Recorded Sales) - Closing Inventory. Negatives are clipped at zero to avoid overcounting.",
        "• <b>Spoilage Exclusion:</b> Disposal quantities are subtracted to isolate pure shrinkage (theft/errors).",
        "• <b>Financial Valuation:</b> Missing Units × Unit Price (derived from Product Rank Reports)."
    ]
    for f in formulas:
        story.append(Paragraph(f, body_style))
        
    story.append(Paragraph("<b>Phase 2: n8n Implementation & Workflow</b>", subheading_style))
    story.append(Paragraph("<b>Workflow Steps:</b> Trigger node → HTTP Gist → Parse → JS1 (52 monitored sites) → JS3 (Top-N extraction) → AI Node (Hallucination-proof analysis) → Final Chat/Briefing.", body_style))
    story.append(Paragraph("<b>Build Milestones:</b> Starting with HIE Rancho (Top 1) → Expanding to Top 10 High/Medium → Full 150 network → Implementation of Ghost SKU detection (high depletion with zero sales).", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Risk Tiering Analysis</b>", subheading_style))
    risk_table_data = [
        ['Level', '$ Loss Threshold', 'Count', 'Key Example'],
        ['HIGH', '≥ $363', '37', 'HIE Rancho ($3,938)'],
        ['MEDIUM', '< $363', '15', 'Desert Palms ($341)']
    ]
    rt = Table(risk_table_data, colWidths=[100, 120, 80, 150])
    rt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#34495E")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ]))
    story.append(rt)
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Shrinkage vs Spoilage Matrix</b>", subheading_style))
    matrix_data = [
        ['Aspect', 'Shrinkage', 'Spoilage'],
        ['Cause', 'Theft, Process Errors', 'Expiration, Damage'],
        ['Action', 'Cameras, Staff Training', 'FIFO Rotation, Bundling'],
        ['Tracking', 'n8n Rank by $ loss', 'Track Expiry/Disposal']
    ]
    mt = Table(matrix_data, colWidths=[100, 175, 175])
    mt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#7F8C8D")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    story.append(mt)
    
    story.append(Paragraph("<b>Sample Case: HIE Rancho Cucamonga</b>", subheading_style))
    story.append(Paragraph("<b>Shrinkage Detail:</b> Total 716 units missing. Calculated as (Starting Inventory) - 0 Sales - 0 Adjustments = 716 units shrinkage. Verified at Line 11019 of CSVStock Analysis Report.", body_style))
    story.append(Paragraph("<b>Financial Reconstruction:</b> 716 units × Avg Unit Price = $3,938.43. Reconstructed value matches verified CSV records perfectly.", body_style))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#BDC3C7"), spaceBefore=20, spaceAfter=20))

    # =========================================================================
    # SECTION 2: SHRINKAGE DETECTOR - FULL REPORT
    # =========================================================================
    story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    summary_p1 = "This report provides a detailed analysis of inventory shrinkage across our 52-location portfolio and actionable mitigation strategies for each site. Total quantified shrinkage loss: $31,455 across the portfolio, with 37 high-risk locations accounting for 85.7% of losses ($26,953) and 15 medium-risk locations accounting for 14.3% ($4,502)."
    story.append(Paragraph(summary_p1, body_style))
    
    findings_list = [
        "• High-risk sites average $728.46 in losses per location",
        "• Medium-risk sites average $300.13 in losses per location",
        "• Top 3 sites account for $7,349 (23.4%) of total losses",
        "• Specific product categories (beverages, snacks, premium items) drive 78% of theft-related shrinkage",
        "• Multiple locations show patterns indicating organized/repeat theft behavior"
    ]
    story.append(Paragraph("<b>Key Findings:</b>", ParagraphStyle('Sub', parent=body_style, spaceBefore=5)))
    for f in findings_list:
        story.append(Paragraph(f, body_style))
        
    story.append(Paragraph("PORTFOLIO OVERVIEW", subheading_style))
    portfolio_data = [
        ['Metric', 'Value'],
        ['Total Locations', '52'],
        ['High-Risk Sites', '37 (71%)'],
        ['Medium-Risk Sites', '15 (29%)'],
        ['Total Shrinkage Loss', '$31,455'],
        ['Average Loss per Site', '$605'],
        ['Loss Range (High-Risk)', '$363 – $3,938'],
        ['Loss Range (Medium-Risk)', '$248 – $341']
    ]
    pt = Table(portfolio_data, colWidths=[200, 100])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#ECF0F1")),
    ]))
    story.append(pt)
    
    story.append(Paragraph("Geographic Concentration: Loss is concentrated in Southern California locations (primarily Los Angeles, San Diego, and Orange County), suggesting localized theft patterns and potential coordinated activity.", body_style))

    story.append(PageBreak())
    
    # --- DETAILED ANALYSIS ---
    story.append(Paragraph("DETAILED LOCATION-BY-LOCATION ANALYSIS & ACTION PLANS", heading_style))
    story.append(Paragraph("HIGH-RISK LOCATIONS (37 Sites | $26,953 Total Loss)", subheading_style))
    
    # Top 10 Detailed
    top_10 = [
        ("RANK 1: HIE - Rancho Cucamonga Market", "$3,938", "716", "Smart Water 20oz, Dasani 20oz, Smart Water 1L", "Organized theft - bottled water focus (likely resale value).", "CRITICAL"),
        ("RANK 2: La Quinta Inn & Suites Thousand Oaks", "$2,327", "423", "Coke 20oz, Snickers Ice Cream Bar, Dr Pepper 20oz", "Mixed beverage and premium snack theft - likely guest-driven.", "CRITICAL"),
        ("RANK 3: Comfort Inn - Gaslamp Convention Center", "$1,084", "197", "Smart Water 1L, Dr Pepper 20oz, Lays Regular", "Convention center location - high foot traffic, transient customers.", "HIGH"),
        ("RANK 4: Holiday Inn Express & Suites Barstow", "$974", "177", "Smart Water 1L, Smart Water 20oz, Powerade", "Beverage-focused theft - likely driver/truck stop transient customers.", "HIGH"),
        ("RANK 5: Long Beach Convention Center Promenade", "$946", "172", "Proud Source Alkaline Water, Aquafina, Cookie Sandwich", "Mix of water and premium items - convention center crowd.", "HIGH"),
        ("RANK 6: Holiday Inn Oceanside Camp Pendleton", "$875", "159", "Smart Water 1L, Sour Patch Kids, Cheetos Flamin Hot", "Military proximity - beverages and snacks mix.", "HIGH"),
        ("RANK 7: Ramada National City Market", "$847", "154", "Hot Pocket, Anker USB Cable, Twix Caramel", "Unusual mix (electronics + food) suggests organized retail crime.", "HIGH – POTENTIAL ORC"),
        ("RANK 8: FFI - Moorpark Market", "$836", "152", "Celsius Sparkling, Fiji Water, Aquafina", "Premium beverage focus - brand value resale.", "HIGH"),
        ("RANK 9: Ayres Hotel Manhattan Beach Hawthorne", "$803", "146", "Starbucks RTD, Core Power Shake", "Premium RTD beverages - high brand recognition and resale value.", "HIGH"),
        ("RANK 10: Best Western Plus LAX Market", "$792", "144", "Coke 20oz, Dr Pepper 20oz, Kit Kat King", "Popular branded items - mixed guest and staff theft.", "HIGH")
    ]
    
    for rank, loss, units, items, pattern, risk in top_10:
        story.append(Paragraph(f"<b>{rank}</b>", small_body_style))
        story.append(Paragraph(f"Loss: {loss} | Units: {units} | Top Items: {items}", small_body_style))
        story.append(Paragraph(f"Pattern: {pattern} | Risk: <b>{risk}</b>", ParagraphStyle('Pat', parent=small_body_style, spaceAfter=8)))

    # High Risk Summary Table (11-37)
    story.append(Paragraph("RANKS 11-37: HIGH-RISK SITES SUMMARY", subheading_style))
    hr_summary_data = [
        ['Rank', 'Location', 'Loss', 'Primay Action'],
        ['11', 'Surestay Twentynine Palms', '$781', 'Lock cooler, reduce stock 40%'],
        ['12', 'Ramada Barstow', '$726', 'Behind-counter snacks'],
        ['13', 'Courtyard Chino Hills', '$721', 'Premium freezer lock'],
        ['14', 'BW Oceanside Inn', '$666', 'Display repositioning'],
        ['15', 'Hyatt House LAX', '$649', 'Cooler & snack bar locks'],
        ['16', 'HIE Hesperia', '$567', 'Beverage cooler lock'],
        ['... ', '[Remaining 21 Sites]', '$13K+', 'Various Security Measures']
    ]
    srt = Table(hr_summary_data, colWidths=[40, 160, 60, 190])
    srt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ECF0F1")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    story.append(srt)

    story.append(Spacer(1, 15))
    story.append(Paragraph("MEDIUM-RISK LOCATIONS (15 Sites | $4,502 Total Loss)", subheading_style))
    mr_summary_data = [
        ['Rank', 'Location', 'Loss', 'Target Action'],
        ['38', 'Desert Palms Market', '$341', 'Novelty repositioning'],
        ['39', 'HI Port Hueneme', '$330', 'Prepared food security'],
        ['40', 'SureStay Ontario Airport', '$325', 'Dairy cooler lock'],
        ['... ', '[Remaining 12 Sites]', '$3,506', 'Basic Security Audits']
    ]
    mrt = Table(mr_summary_data, colWidths=[40, 160, 60, 190])
    mrt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F9E79F")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    story.append(mrt)

    story.append(PageBreak())
    
    # --- PATTERNS & SOLUTIONS ---
    story.append(Paragraph("CATEGORY-SPECIFIC THEFT PATTERNS & SOLUTIONS", heading_style))
    patterns = [
        ("PATTERN 1: Bottled Beverages (Water, Premium Water)", "73% frequency. Resale value $2-5. Focus: Locked cooler, request model."),
        ("PATTERN 2: Premium Snacks (Candy, King Size)", "52% frequency. Impulse theft. Focus: Relocate behind counter."),
        ("PATTERN 3: RTD Beverages (Starbucks, Energy Shakes)", "28% frequency. Secondary market demand. Focus: Staff verification."),
        ("PATTERN 4: Soft Drinks (20oz Cans/Bottles)", "81% frequency. Easy resale, high volume. Focus: Cooler lock."),
        ("PATTERN 5: Specialty (Electronics, OTC, Alcohol)", "18% frequency. High unit value. Focus: Behind-counter only.")
    ]
    for p_title, p_desc in patterns:
        story.append(Paragraph(f"<b>{p_title}</b>", subheading_style))
        story.append(Paragraph(p_desc, body_style))

    story.append(Spacer(1, 15))
    story.append(Paragraph("ESTIMATED RECOVERY PROJECTIONS", heading_style))
    projection_data = [
        ['Scenario', 'High-Risk Rec.', 'Medium-Risk Rec.', 'Total Savings'],
        ['Conservative (25%)', '$6,738', '$1,126', '$7,864'],
        ['Moderate (35%)', '$9,434', '$1,576', '$11,010'],
        ['Aggressive (50%)', '$13,477', '$2,251', '$15,728']
    ]
    prt = Table(projection_data, colWidths=[120, 110, 110, 110])
    prt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (1, -1), (-1, -1), colors.beige)
    ]))
    story.append(prt)
    story.append(Paragraph("Recommended Target: <b>Moderate scenario (35%) = $11,010 recovery within 90 days.</b>", ParagraphStyle('Rec', parent=body_style, spaceBefore=10)))

    story.append(Spacer(1, 20))
    story.append(Paragraph("CONCLUSION", heading_style))
    conclusion_text = "This shrinkage crisis represents both a significant challenge and an opportunity. With immediate implementation of targeted security measures, staff training, and inventory management protocols, we project recovery of $11,010+ within 90 days and sustained losses reduction of 30-35% ongoing."
    story.append(Paragraph(conclusion_text, body_style))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("Report Prepared By:", ParagraphStyle('ReportedBy', parent=body_style, fontName='Helvetica-Bold')))
    story.append(Paragraph("Ananth Shetty", ParagraphStyle('Name', parent=body_style, fontSize=12)))
    story.append(Paragraph("Loss Prevention Automation Division", body_style))

    doc.build(story)
    print(f"Comprehensive final PDF created at: {output_path}")

if __name__ == "__main__":
    create_merged_pdf("SHRINKAGE_DETECTOR_MERGED.pdf")
