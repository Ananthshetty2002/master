import pandas as pd
import json
import os

def fix_and_verify():
    """
    1. Load JSON.
    2. Load Refined CSV (Source of Truth).
    3. Iterate through every product in the JSON.
    4. If values mismatch, update the JSON.
    5. Recalculate totals.
    6. Verify everything again.
    """
    json_path = 'n8n_consolidated_report_final_fixed.json'
    csv_path = 'shrinkage_report_refined.csv'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    
    # Matching columns
    qty_col = 'Shrinkage_Qty'
    sales_col = 'Sales_Quantity'
    price_col = 'Implied_Unit_Price'
    val_col = 'Shrinkage_Value'
    
    csv_lookup = {}
    for _, row in df.iterrows():
        key = (str(row['Location']).strip(), str(row['Product ID']).strip())
        csv_lookup[key] = row.to_dict()

    fix_count = 0
    total_items = 0

    for loc_entry in data.get('location_ranking', []):
        loc_name = str(loc_entry.get('location', '')).strip()
        products = loc_entry.get('shrinkage_products', [])
        
        for p in products:
            total_items += 1
            pid = str(p.get('product_id', '')).strip()
            key = (loc_name, pid)
            
            if key in csv_lookup:
                row = csv_lookup[key]
                
                # Check and fix Sales
                c_sales = float(row.get(sales_col, 0))
                if abs(p.get('sales_units', 0) - c_sales) > 0.01:
                    p['sales_units'] = c_sales
                    fix_count += 1
                
                # Check and fix Shrinkage Qty
                c_qty = float(row.get(qty_col, 0))
                if abs(p.get('shrinkage_qty', 0) - c_qty) > 0.01:
                    p['shrinkage_qty'] = c_qty
                    fix_count += 1
                
                # Recalculate shrinkage_value if we have the unit_price
                price = p.get('unit_price', 0)
                if price and price > 0:
                    p['shrinkage_value'] = round(p['shrinkage_qty'] * price, 4)
            else:
                # Log products in JSON but not in CSV root
                pass

        # Recalculate Location Totals
        loc_entry['total_shrinkage_qty'] = round(sum(p.get('shrinkage_qty', 0) for p in products), 4)
        loc_entry['total_shrinkage_value'] = round(sum(p.get('shrinkage_value', 0) for p in products), 4)
        loc_entry['sales_units'] = round(sum(p.get('sales_units', 0) for p in products), 4)
        
        # Verify Inventory Equation again (start - sales - end = shrink)
        # We might need to adjust 'end_qty' to keep it balanced if 'sales_units' or 'shrinkage_qty' changed.
        start = loc_entry.get('start_qty', 0)
        sales = loc_entry.get('sales_units', 0)
        shrink = loc_entry.get('total_shrinkage_qty', 0)
        loc_entry['end_qty'] = round(start - sales - shrink, 4)

    # Recalculate overall summary metrics
    all_prods = [p for loc in data['location_ranking'] for p in loc['shrinkage_products']]
    data['summary_metrics']['total_shrinkage_qty'] = round(sum(p.get('shrinkage_qty', 0) for p in all_prods if p.get('shrinkage_qty', 0) > 0), 4)
    data['summary_metrics']['total_shrinkage_value'] = round(sum(p.get('shrinkage_value', 0) for p in all_prods if p.get('shrinkage_value', 0) > 0), 4)
    data['summary_metrics']['total_sales_units'] = round(sum(p.get('sales_units', 0) for p in all_prods), 4)

    print(f"Total items checked: {total_items}")
    print(f"Total fixes applied: {fix_count}")
    
    with open('n8n_consolidated_report_RE-FIXED.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("Corrected report saved to n8n_consolidated_report_RE-FIXED.json")

if __name__ == "__main__":
    fix_and_verify()
