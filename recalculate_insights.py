import json
import os

def fix_zero_insights():
    work_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    json_path = os.path.join(work_dir, "n8n_consolidated_report_final_fixed.json")
    
    if not os.path.exists(json_path):
        print("JSON report not found.")
        return

    # 1. Load Data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Re-summarize each location in location_ranking
    print("Recalculating site totals from product-level data...")
    all_locations = []
    
    for loc_entry in data.get('location_ranking', []):
        shrink_prods = loc_entry.get('shrinkage_products', [])
        
        # Calculate actual sums from products
        actual_qty = sum(p.get('shrinkage_qty', 0) for p in shrink_prods)
        actual_val = sum(p.get('shrinkage_value', 0) for p in shrink_prods)
        
        # Update site-level totals in ranking
        loc_entry['total_shrinkage_qty'] = actual_qty
        loc_entry['total_shrinkage_value'] = actual_val
        
        if actual_qty > 0 or actual_val > 0:
            all_locations.append({
                "location": loc_entry.get('location'),
                "total_shrinkage_qty": actual_qty,
                "total_shrinkage_value": actual_val
            })

    # 3. Fix overall_shrinkage_summary insight
    print("Updating overall_shrinkage_summary insight rankings...")
    
    # Sort locations by value desc
    all_locations.sort(key=lambda x: x['total_shrinkage_value'], reverse=True)
    top_10_locs = all_locations[:10]
    
    # Also find top items across all locations
    all_items = []
    for loc_entry in data.get('location_ranking', []):
        for p in loc_entry.get('shrinkage_products', []):
            if p.get('shrinkage_qty', 0) > 0:
                all_items.append({
                    "product_name": p.get('product_name'),
                    "location": loc_entry.get('location'),
                    "shrinkage_qty": p.get('shrinkage_qty'),
                    "shrinkage_value": p.get('shrinkage_value')
                })
    
    all_items.sort(key=lambda x: x['shrinkage_value'], reverse=True)
    top_10_items = all_items[:10]

    # Update the insight
    found_insight = False
    for insight in data.get('insights', []):
        if insight.get('id') == "overall_shrinkage_summary":
            insight['result_data']['top_locations'] = top_10_locs
            insight['result_data']['top_items'] = top_10_items
            insight['severity'] = "Critical" if top_10_locs and top_10_locs[0]['total_shrinkage_value'] > 0 else "Low"
            found_insight = True

    # 4. Update Summary Metrics
    if 'summary_metrics' in data:
        data['summary_metrics']['total_shrinkage_qty'] = sum(l['total_shrinkage_qty'] for l in all_locations)
        data['summary_metrics']['total_shrinkage_value'] = sum(l['total_shrinkage_value'] for l in all_locations)
        data['summary_metrics']['total_locations_impacted'] = len(all_locations)

    # 5. Save
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Recalculation complete. Updated {len(all_locations)} sites in summary.")
    if top_10_locs:
        print(f"Top site: {top_10_locs[0]['location']} with ${top_10_locs[0]['total_shrinkage_value']:.2f}")

if __name__ == "__main__":
    fix_zero_insights()
