import json
import os

def format_report():
    input_file = "n8n_consolidated_report1.json"
    output_file = "n8n_consolidated_report_final.json" # User requested this name
    
    print(f"Reading {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Create new structure based on n8n_consolidated_report.json keys
    formatted_data = {}
    
    # 1. Report Period
    formatted_data["report_period"] = data.get("report_period", {})
    
    # 2. Engine Context
    formatted_data["engine_context"] = data.get("engine_context", "Analysis Context")
    
    # 3. Location Ranking (Filtered)
    print("Formatting location rankings...")
    locations = []
    source_rankings = data.get("location_ranking", [])
    
    for loc in source_rankings:
        new_loc = {
            "location": loc.get("location"),
            "total_shrinkage_qty": loc.get("total_shrinkage_qty"),
            "sales_units": loc.get("sales_units"),
            "start_qty": loc.get("start_qty"),
            "end_qty": loc.get("end_qty"),
            "shrinkage_products": []
        }
        
        # Filter products - Limit to Top 50 by shrinkage_value
        all_products = loc.get("shrinkage_products", [])
        
        # Sort by shrinkage_value descending (handle None as 0)
        def get_shrink_val(p):
            val = p.get("shrinkage_value")
            return float(val) if val is not None else 0.0
            
        all_products.sort(key=get_shrink_val, reverse=True)
        top_50_products = all_products[:50]
        
        for prod in top_50_products:
            new_prod = {
                "product_name": prod.get("product_name"),
                "product_id": prod.get("product_id"),
                "shrinkage_qty": prod.get("shrinkage_qty"),
                "shrinkage_value": prod.get("shrinkage_value"),
                "sales_units": prod.get("sales_units")
            }
            new_loc["shrinkage_products"].append(new_prod)
            
        locations.append(new_loc)
        
    formatted_data["location_ranking"] = locations

    # 4. Transfer Insights
    # Search for key starting with 'network_transfer_' or containing 'transfer'
    transfer_data = None
    
    # Check exact keys first
    possible_keys = ["network_transfer_optimizations", "network_transfer_opportunities", "inventory_transfers"]
    for key in possible_keys:
        if key in data:
            print(f"Found transfer data (exact match): {key}")
            transfer_data = data[key]
            formatted_data[key] = transfer_data
            break
            
    # Fuzzy search if not found
    if not transfer_data:
        print("Searching for transfer key via partial match...")
        for key in data.keys():
            if "network_transfer_" in key:
                print(f"Found transfer data (partial match): {key}")
                transfer_data = data[key]
                formatted_data[key] = transfer_data
                break
    
    if not transfer_data:
        print("WARNING: No transfer data found in top-level keys.")
        # Print available keys for debugging
        print(f"Available keys: {list(data.keys())}")

    # Write output - Standard Pretty Print (Top 50 Limit kept)
    print(f"Writing to {output_file} (Pretty Printed)...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, indent=2)
    
    print("Done.")

if __name__ == "__main__":
    format_report()
