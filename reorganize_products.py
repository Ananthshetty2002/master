
import json

def fix_locations():
    input_file = 'n8n_consolidated_report.json'
    output_file = 'n8n_consolidated_report_final_fixed.json'
    
    print(f"Loading {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File {input_file} not found.")
        return

    ranking = data.get("location_ranking", [])
    
    print("Recalculating totals...")
    for loc_entry in ranking:
        products = loc_entry.get("shrinkage_products", [])
        
        # Calculate new sums
        # Handle None explicitly
        def safe_float(x):
            if x is None: return 0.0
            try:
                return float(x)
            except:
                return 0.0

        new_shrink_qty = sum(safe_float(p.get("shrinkage_qty")) for p in products)
        new_shrink_val = sum(safe_float(p.get("shrinkage_value")) for p in products)
        
        # Update fields
        loc_entry["total_shrinkage_qty"] = new_shrink_qty
        loc_entry["total_shrinkage_value"] = new_shrink_val
        
        products.sort(key=lambda x: safe_float(x.get("shrinkage_qty")), reverse=True)

    print(f"Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("Done.")

if __name__ == "__main__":
    fix_locations()
