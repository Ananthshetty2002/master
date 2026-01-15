import pandas as pd
import json
import os

def strict_cross_check():
    json_path = 'n8n_consolidated_report_FINAL_VERIFIED_V2.json'
    csv_path = 'shrinkage_report_refined.csv'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    print(f"DEBUG: Detected columns: {list(df.columns)}")
    
    # Matching Logic
    # Correct columns for refined.csv (from Step 1409)
    qty_col = 'Shrinkage_Qty'
    sales_col = 'Sales_Quantity'
    price_col = 'Implied_Unit_Price'
    val_col = 'Shrinkage_Value'
    
    print(f"DEBUG: Using columns: qty={qty_col}, sales={sales_col}")

    csv_lookup = {}
    for _, row in df.iterrows():
        key = (str(row['Location']).strip(), str(row['Product ID']).strip())
        csv_lookup[key] = row.to_dict()

    errors = []
    total_checked = 0
    matched = 0

    for loc_entry in data.get('location_ranking', []):
        loc_name = str(loc_entry.get('location', '')).strip()
        for p in loc_entry.get('shrinkage_products', []):
            total_checked += 1
            pid = str(p.get('product_id', '')).strip()
            key = (loc_name, pid)
            
            if key in csv_lookup:
                matched += 1
                row = csv_lookup[key]
                
                # Check Qty
                c_qty = float(row.get(qty_col, 0))
                j_qty = float(p.get('shrinkage_qty', 0))
                if abs(c_qty - j_qty) > 0.01:
                    errors.append(f"Qty Mismatch: {loc_name} | {pid} | CSV={c_qty}, JSON={j_qty}")
                
                # Check Sales
                c_sales = float(row.get(sales_col, 0))
                j_sales = float(p.get('sales_units', 0))
                if abs(c_sales - j_sales) > 0.01:
                    errors.append(f"Sales Mismatch: {loc_name} | {pid} | CSV={c_sales}, JSON={j_sales}")
            else:
                # errors.append(f"Not in CSV: {loc_name} | {pid}")
                pass

    print(f"Checked: {total_checked}, Matched: {matched}, Errors: {len(errors)}")
    with open('AUDIT_DEBUG.txt', 'w', encoding='utf-8') as f:
        for e in errors:
            f.write(e + "\n")

if __name__ == "__main__":
    strict_cross_check()
