import json
from datetime import datetime

def add_spoilage_section():
    # 1. Load Main Report
    report_path = 'n8n_consolidated_report_FINAL_VERIFIED.json'
    with open(report_path, 'r', encoding='utf-8') as f:
        report_data = json.load(f)

    # 2. Load Spoilage Data
    with open('spoilage_report.json', 'r', encoding='utf-8') as f:
        spoilage_data = json.load(f)

    # 3. Process Spoilage Items
    # Source structure: 'risky_items': [ {item_name, stock_qty, expiry_date, unit_price ...} ]
    # Or top level list? 'spoilage_report.json' usually has keys like 'risky_items' or is a list.
    # Based on Step 2076 output: {"current_date": "...", "risky_items": [...]}
    
    risky_items = spoilage_data.get('risky_items', [])
    ref_date_str = spoilage_data.get('current_date', '2025-12-31')
    try:
        ref_date = datetime.strptime(ref_date_str, "%Y-%m-%d")
    except:
        ref_date = datetime.now()

    formatted_spoilage = []
    
    for item in risky_items:
        # Calculate Days Left
        exp_str = item.get('expiry_date')
        days_left_str = "N/A"
        if exp_str:
            try:
                exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
                delta = (exp_date - ref_date).days
                days_left_str = f"{delta}d"
                if delta < 0: days_left_str = "EXPIRED"
            except:
                pass
        
        # Calculate Waste Risk
        qty = item.get('stock_qty', 0)
        price = item.get('unit_price', 0)
        risk_val = round(qty * price, 2)
        
        # Action Logic (Simple rule or from file)
        action = "Bundle/Discount"
        if days_left_str == "EXPIRED":
            action = "Discard/Write-off"
        elif days_left_str != "N/A" and "d" in days_left_str and int(days_left_str.replace('d','')) > 7:
            action = "Monitor"

        formatted_spoilage.append({
            "Product": item.get('item_name', 'Unknown'),
            "Stock": qty,
            "Expiry Date": exp_str,
            "Days Left": days_left_str,
            "Waste Risk": f"$ {risk_val}",
            "Action": action,
            "Location": item.get('location', 'Unknown')
        })

    # 4. Inject into Report
    # Add as a top-level key: "spoilage_risk_details"
    report_data["spoilage_risk_details"] = formatted_spoilage
    
    # 5. Save
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2)
    
    # Also update final_fixed for consistency
    with open('n8n_consolidated_report_final_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2)

    print(f"Added {len(formatted_spoilage)} spoilage items to report.")

if __name__ == "__main__":
    add_spoilage_section()
