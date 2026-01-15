import pandas as pd
import json

def populate_final():
    """Final attempt with correct column detection"""
    
    print("Loading CSV...")
    df = pd.read_csv('shrinkage_report.csv')
    
    print(f"All columns: {list(df.columns)}")
    
    # Find price-related columns
    price_cols = [c for c in df.columns if 'price' in c.lower() or 'unit' in c.lower()]
    print(f"\nPrice-related columns: {price_cols}")
    
    # Show sample data
    if len(df) > 0:
        print("\nSample row:")
        for col in df.columns:
            print(f"  {col}: {df.iloc[0][col]}")
    
    # Build lookup using Shrinkage_Value / shrinkage_qty to derive unit price
    print("\nBuilding price lookup...")
    product_prices = {}
    
    for _, row in df.iterrows():
        prod_id = str(row.get('Product ID', '')).strip()
        shrink_val = row.get('Shrinkage_Value')
        shrink_qty = row.get('Shrinkage_Qty')
        
        if prod_id and pd.notna(shrink_val) and pd.notna(shrink_qty) and shrink_qty > 0:
            # Calculate unit price from shrinkage value and quantity
            unit_price = float(shrink_val) / float(shrink_qty)
            
            if prod_id in product_prices:
                # Average if multiple entries
                product_prices[prod_id] = (product_prices[prod_id] + unit_price) / 2
            else:
                product_prices[prod_id] = unit_price
    
    print(f"Created lookup for {len(product_prices)} products")
    
    if len(product_prices) > 0:
        # Show sample
        sample_id = list(product_prices.keys())[0]
        print(f"Sample: {sample_id} -> ${product_prices[sample_id]:.2f}")
    
    # Load JSON and update
    print("\nLoading JSON...")
    with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    ranking = report.get("location_ranking", [])
    
    updated = 0
    not_found = 0
    
    for loc_entry in ranking:
        products = loc_entry.get("shrinkage_products", [])
        
        for p in products:
            prod_id = str(p.get("product_id", "")).strip()
            shrinkage_qty = p.get("shrinkage_qty", 0) or 0
            
            if prod_id in product_prices:
                unit_price = product_prices[prod_id]
                shrinkage_value = shrinkage_qty * unit_price
                
                p["unit_price"] = round(unit_price, 2)
                p["shrinkage_value"] = round(shrinkage_value, 2)
                updated += 1
            else:
                not_found += 1
        
        # Recalculate total
        total = sum(p.get("shrinkage_value", 0) or 0 for p in products)
        loc_entry["total_shrinkage_value"] = round(total, 2)
    
    print(f"\nUpdated: {updated}")
    print(f"Not found: {not_found}")
    
    # Save
    print("\nSaving...")
    with open('n8n_consolidated_report_final_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("Done!")
    
    return updated, not_found

if __name__ == "__main__":
    updated, not_found = populate_final()
