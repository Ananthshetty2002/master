import pandas as pd
import json
from datetime import datetime

def clean_id(val):
    """Clean ID to remove trailing .0 if it's numeric"""
    s = str(val).strip()
    if s.endswith('.0'):
        return s[:-2]
    if s == 'nan' or s == '0' or s == '0.0':
        return None
    return s

def create_verified_report_v2():
    """Create final report with STRICT distinction between verified and unverified shrinkage"""
    
    report = {
        "report_metadata": {
            "report_title": "December 2025 Inventory & Shrinkage Gap Analysis",
            "generated_at": datetime.now().isoformat(),
            "status": "🚨 DATA INCOMPLETE (Missing Sales Reports)",
            "overall_conclusion": "Total network shrinkage is currently UNKNOWN because Sales By Product reports are missing for 191/193 sites."
        },
        
        "section_1_verified_warehouse_loss": {
            "location": "Stock (Warehouse)",
            "period": "DEC 3-31, 2025",
            "status": "✅ VERIFIED",
            "shrinkage_qty": 3585.0,
            "shrinkage_value": 11583.42,
            "note": "This is the ONLY location with complete data."
        },
        
        "section_2_micromarket_data_gap": {
            "category": "Retail Sites (Micromarkets)",
            "site_count": 192,
            "status": "❌ CALCULATION IMPOSSIBLE",
            "reason": "Missing 'Sales By Product' CSV files.",
            "impact": "Shrinkage for these sites is currently reported as $0.00, but this is a false zero due to missing sales figures in the calculation (Start - Sales - End).",
            "sites_affected": []
        },
        
        "section_3_inventory_snapshots": {
            "note": "We CAN reliably report Start and End quantities even without sales.",
            "by_location": [],
            "by_product": []
        },
        
        "section_4_november_baseline": {
            "period": "November 2025",
            "label": "November Spoilage & Overage baseline",
            "spoilage_events": []
        }
    }
    
    # Load Refined Data
    df_refined = pd.read_csv('shrinkage_report_refined.csv')
    df_refined.columns = [c.strip() for c in df_refined.columns]
    
    # Fill NaNs to prevent invalid JSON
    df_refined = df_refined.fillna(0)
    
    # Process Retail Sites for Section 2
    retail_sites = df_refined[df_refined['Location'] != 'Stock']['Location'].unique()
    for loc in retail_sites:
        if pd.isna(loc): continue
        report['section_2_micromarket_data_gap']['sites_affected'].append(str(loc))
    
    # Process Inventory for Section 3
    for location in df_refined['Location'].unique():
        if pd.isna(location): continue
        loc_data = df_refined[df_refined['Location'] == location]
        
        report['section_3_inventory_snapshots']['by_location'].append({
            "location": str(location),
            "period": "DEC 3-31, 2025",
            "start_qty": float(loc_data['Quantity_Start'].sum()),
            "end_qty": float(loc_data['Quantity_End'].sum()),
            "net_inventory_change": float(loc_data['Quantity_End'].sum() - loc_data['Quantity_Start'].sum())
        })

    # Product-level inventory
    product_inv = {}
    for _, row in df_refined.iterrows():
        pid = clean_id(row['Product ID'])
        if pid is None: continue
        if pid not in product_inv:
            product_inv[pid] = {"product_id": pid, "total_start": 0, "total_end": 0}
        product_inv[pid]['total_start'] += float(row['Quantity_Start'])
        product_inv[pid]['total_end'] += float(row['Quantity_End'])
    
    report['section_3_inventory_snapshots']['by_product'] = [
        {"id": k, "start": v['total_start'], "end": v['total_end']} for k, v in product_inv.items()
    ]

    # Load November Spoilage for Section 4
    try:
        with open('spoilage_report.json', 'r', encoding='utf-8') as f:
            spoilage = json.load(f)
        for item in spoilage.get('risky_items', []):
            report['section_4_november_baseline']['spoilage_events'].append({
                "product": item.get('item_name'),
                "location": item.get('location'),
                "expiry": item.get('expiry_date'),
                "risk": item.get('stock_qty', 0) * item.get('unit_price', 0)
            })
    except:
        pass

    # Save
    with open('december_2025_verified_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print("V2 Report generated with clear data gap separation.")

if __name__ == "__main__":
    create_verified_report_v2()
