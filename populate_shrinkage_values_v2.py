import json
import pandas as pd
import os

def populate_shrinkage_values():
    json_path = 'n8n_consolidated_report_final_fixed.json'
    csv_path = 'shrinkage_report.csv'
    
    if not os.path.exists(json_path):
        print(f"JSON file not found: {json_path}")
        return
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return

    print("Loading CSV data...")
    df = pd.read_csv(csv_path)
    
    # Mapping (Location, Product ID) -> Implied_Unit_Price
    # Mapping Product ID -> Average Implied_Unit_Price (for fallback)
    
    loc_prod_price = {}
    prod_price_fallback = {}
    
    # Process CSV
    for _, row in df.iterrows():
        loc = str(row['Location']).strip()
        pid = str(row['Product ID']).strip()
        price = row.get('Implied_Unit_Price', 0)
        
        if pd.isna(price) or price <= 0:
            # Try to calculate from Shrinkage_Value / Shrinkage_Qty
            s_val = row.get('Shrinkage_Value', 0)
            s_qty = row.get('Shrinkage_Qty', 0)
            if s_qty != 0:
                price = abs(s_val / s_qty)
            else:
                price = 0
                
        if price > 0:
            loc_prod_price[(loc, pid)] = price
            if pid not in prod_price_fallback:
                prod_price_fallback[pid] = []
            prod_price_fallback[pid].append(price)

    # Average the fallback prices
    for pid in prod_price_fallback:
        prices = prod_price_fallback[pid]
        prod_price_fallback[pid] = sum(prices) / len(prices)

    print("Loading JSON data...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Populating values...")
    total_products = 0
    updated_products = 0
    fallback_used = 0
    still_null = 0

    for loc_entry in data.get('location_ranking', []):
        loc_name = str(loc_entry.get('location')).strip()
        products = loc_entry.get('shrinkage_products', [])
        
        loc_shrink_val_sum = 0
        
        for p in products:
            total_products += 1
            pid = str(p.get('product_id')).strip()
            qty = p.get('shrinkage_qty', 0)
            
            price = None
            if (loc_name, pid) in loc_prod_price:
                price = loc_prod_price[(loc_name, pid)]
            elif pid in prod_price_fallback:
                price = prod_price_fallback[pid]
                fallback_used += 1
            
            if price is not None:
                p['unit_price'] = round(price, 4)
                p['shrinkage_value'] = round(qty * price, 4)
                updated_products += 1
            else:
                p['unit_price'] = None
                p['shrinkage_value'] = 0 # Or keep as null? Usually 0 is better for sums
                still_null += 1
            
            loc_shrink_val_sum += p.get('shrinkage_value', 0)
            
        # Update location total
        loc_entry['total_shrinkage_value'] = round(loc_shrink_val_sum, 4)

    print(f"Total products processed: {total_products}")
    print(f"Products updated (Exact Match): {updated_products - fallback_used}")
    print(f"Products updated (Fallback): {fallback_used}")
    print(f"Products still without price: {still_null}")

    print("Saving updated JSON...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("Done!")

if __name__ == "__main__":
    populate_shrinkage_values()
