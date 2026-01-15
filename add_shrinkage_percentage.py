import json
import os

def add_shrinkage_percentage():
    work_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    json_path = os.path.join(work_dir, "n8n_consolidated_report_final_fixed.json")
    
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    print(f"Loading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Calculating and adding shrinkage contribution percentages...")
    
    # Process location_ranking
    for loc_entry in data.get('location_ranking', []):
        total_val = loc_entry.get('total_shrinkage_value', 0)
        shrink_prods = loc_entry.get('shrinkage_products', [])
        
        for p in shrink_prods:
            prod_val = p.get('shrinkage_value')
            if prod_val is None:
                prod_val = 0.0
            
            if total_val and total_val > 0:
                percentage = (float(prod_val) / float(total_val)) * 100
                p['shrinkage_contribution_percentage'] = round(percentage, 2)
            else:
                p['shrinkage_contribution_percentage'] = 0.0

    # Process insights (if they contain product lists with shrinkage_value)
    # The user specifically asked for "shrinkage products values" in each location.
    # We already covered the main location_ranking section.
    
    print(f"Saving updated JSON to {json_path}...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print("Successfully added shrinkage contribution percentages.")

if __name__ == "__main__":
    add_shrinkage_percentage()
