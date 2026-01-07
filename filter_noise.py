import json
import os

def filter_noise():
    work_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    json_path = os.path.join(work_dir, "n8n_consolidated_report_final_fixed.json")
    
    if not os.path.exists(json_path):
        print("JSON report not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    original_count = 0
    remaining_count = 0
    
    print("Filtering zero-impact products (shrink=0 and end_stock=0)...")
    
    new_location_ranking = []
    
    for loc_entry in data.get('location_ranking', []):
        shrinkage_prods = loc_entry.get('shrinkage_products', [])
        original_count += len(shrinkage_prods)
        
        # Keep only items with non-zero shrinkage OR remaining stock
        filtered_prods = [
            p for p in shrinkage_prods 
            if p.get('shrinkage_qty', 0) != 0 or p.get('quantity_end', 0) > 0
        ]
        
        remaining_count += len(filtered_prods)
        
        # Update entry
        loc_entry['shrinkage_products'] = filtered_prods
        
        # We keep the site even if it has no products now, 
        # as it might have spoilage_items or total_shrinkage metrics
        # Only remove if it's completely empty across all meaningful arrays
        if filtered_prods or loc_entry.get('spoilage_items') or loc_entry.get('total_shrinkage_qty', 0) != 0:
            new_location_ranking.append(loc_entry)

    data['location_ranking'] = new_location_ranking
    
    # Save JSON with indentation preserved
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Cleanup Complete.")
    print(f"Removed {original_count - remaining_count} noisy entries.")
    print(f"Active items remaining: {remaining_count}")
    print(f"Total sites preserved: {len(new_location_ranking)}")

if __name__ == "__main__":
    filter_noise()
