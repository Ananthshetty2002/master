import json

def finalize_report():
    json_path = 'n8n_consolidated_report_final_fixed.json'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Manual fixes for the 2 missing products
    # 1. Penn Championship Tennis Balls
    # 2. Boom Chicka Popcorn Sea Salt 4.8oz
    
    fixes = {
        "Penn Championship Tennis Balls": 5.95,
        "Boom Chicka Popcorn Sea Salt 4.8oz": 6.95
    }

    print("Applying final fixes...")
    updated_count = 0
    for loc_entry in data.get('location_ranking', []):
        products = loc_entry.get('shrinkage_products', [])
        loc_val_change = False
        
        for p in products:
            pname = p.get('product_name')
            pid = p.get('product_id')
            
            if pname in fixes and (p.get('unit_price') is None or p.get('unit_price') == 0):
                price = fixes[pname]
                qty = p.get('shrinkage_qty', 0)
                p['unit_price'] = price
                p['shrinkage_value'] = round(qty * price, 4)
                updated_count += 1
                loc_val_change = True
            elif pid in fixes and (p.get('unit_price') is None or p.get('unit_price') == 0):
                 price = fixes[pid]
                 qty = p.get('shrinkage_qty', 0)
                 p['unit_price'] = price
                 p['shrinkage_value'] = round(qty * price, 4)
                 updated_count += 1
                 loc_val_change = True
        
        if loc_val_change:
            # Recalculate location total
            new_total = sum(p.get('shrinkage_value', 0) for p in products)
            loc_entry['total_shrinkage_value'] = round(new_total, 4)

    print(f"Final items updated: {updated_count}")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("Report finalized.")

if __name__ == "__main__":
    finalize_report()
