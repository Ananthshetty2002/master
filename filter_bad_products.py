
import json

def filter_bad():
    bad_ids = set()
    try:
        with open('found_entry.json', 'r') as f:
            entries = json.load(f)
            for entry in entries:
                if "Barstow" in entry.get("location", ""):
                    for p in entry.get("shrinkage_products", []):
                        if "Altura" in p.get("location", ""):
                            bad_ids.add(p.get("product_id"))
    except Exception as e:
        print(f"Error loading found_entry.json: {e}")
        return

    print(f"Identified {len(bad_ids)} bad product IDs (Alturas).")
    
    report_file = 'n8n_consolidated_report_final_fixed.json'
    with open(report_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    ranking = data.get("location_ranking", [])
    
    def safe_float(x):
        if x is None: return 0.0
        try:
            return float(x)
        except:
            return 0.0
    
    for loc in ranking:
        if "Barstow" in loc.get("location", ""):
            print(f"Processing Barstow...")
            prods = loc.get("shrinkage_products", [])
            initial_count = len(prods)
            
            new_prods = [p for p in prods if p.get("product_id") not in bad_ids]
            
            loc["shrinkage_products"] = new_prods
            final_count = len(new_prods)
            print(f"Removed {initial_count - final_count} products.")
            
            new_shrink_qty = sum(safe_float(p.get("shrinkage_qty")) for p in new_prods)
            loc["total_shrinkage_qty"] = new_shrink_qty
            loc["total_shrinkage_value"] = sum(safe_float(p.get("shrinkage_value")) for p in new_prods)
            
            print(f"New Total Shrink Qty: {new_shrink_qty}")
            
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("Saved filtered report.")

if __name__ == "__main__":
    filter_bad()
