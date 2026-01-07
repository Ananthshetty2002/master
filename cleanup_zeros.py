import json
import os

def aggressive_filter():
    work_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    json_path = os.path.join(work_dir, "n8n_consolidated_report_final_fixed.json")
    
    if not os.path.exists(json_path):
        print("JSON report not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    original_count = 0
    removed_count = 0
    
    new_location_ranking = []
    
    for loc_entry in data.get('location_ranking', []):
        shrinkage_prods = loc_entry.get('shrinkage_products', [])
        original_count += len(shrinkage_prods)
        
        # Aggressive rule: If we have NO inventory context (Start=0 and End=0), 
        # it is noise for a shrinkage report, regardless of sales.
        filtered_prods = [
            p for p in shrinkage_prods 
            if not (p.get('quantity_start', 0) == 0 and p.get('quantity_end', 0) == 0)
        ]
        
        removed_count += (len(shrinkage_prods) - len(filtered_prods))
        
        # Update entry
        loc_entry['shrinkage_products'] = filtered_prods
        
        # Keep site if it still has anything useful
        if filtered_prods or loc_entry.get('spoilage_items') or loc_entry.get('total_shrinkage_qty', 0) != 0:
            new_location_ranking.append(loc_entry)

    data['location_ranking'] = new_location_ranking
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Aggressive Filtering Complete.")
    print(f"Removed {removed_count} total noise items (0.0 Start and 0.0 End).")
    print(f"Final total active items: {original_count - removed_count}")

if __name__ == "__main__":
    aggressive_filter()
