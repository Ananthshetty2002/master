import json
import os
import pandas as pd

def final_fix():
    work_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    json_path = os.path.join(work_dir, "n8n_consolidated_report_final_fixed.json")
    shrinkage_csv = os.path.join(work_dir, "shrinkage_report.csv")
    
    if not os.path.exists(json_path):
        print("JSON report not found.")
        return

    # 1. Build Price Mapping
    price_map = {}
    if os.path.exists(shrinkage_csv):
        print(f"Loading prices from {shrinkage_csv}...")
        df = pd.read_csv(shrinkage_csv)
        # Use indices if names fail: Location=0, Product ID=1, Unit_Price=6
        p_id_col = df.columns[1] if len(df.columns) > 1 else 'Product ID'
        price_col = df.columns[6] if len(df.columns) > 6 else 'Unit_Price'
        
        for _, row in df.iterrows():
            pid = str(row[p_id_col]).strip()
            up = float(row[price_col]) if not pd.isna(row[price_col]) else 0.0
            if up > 0:
                if pid not in price_map or up > price_map[pid]:
                    price_map[pid] = up

    # 2. Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 3. Recalculate Site Summaries
    print("Recalculating all site totals...")
    sites_with_impact = []
    all_global_items = []
    
    for loc_entry in data.get('location_ranking', []):
        shrink_prods = loc_entry.get('shrinkage_products', [])
        
        # Enrich each product
        for p in shrink_prods:
            pid = p.get('product_id')
            qty = p.get('shrinkage_qty', 0)
            if qty is None: qty = 0.0
            
            # Fill missing price/value
            if pid in price_map:
                up = price_map[pid]
                p['unit_price'] = up
                curr_val = p.get('shrinkage_value', 0)
                if curr_val is None or curr_val == 0:
                    p['shrinkage_value'] = round(qty * up, 2)
            
            if qty > 0:
                all_global_items.append({
                    "product_name": p.get('product_name'),
                    "location": loc_entry.get('location'),
                    "shrinkage_qty": qty,
                    "shrinkage_value": p.get('shrinkage_value', 0)
                })
        
        # Site Summary
        total_qty = sum(float(p.get('shrinkage_qty', 0) or 0) for p in shrink_prods)
        total_val = sum(float(p.get('shrinkage_value', 0) or 0) for p in shrink_prods)
        
        loc_entry['total_shrinkage_qty'] = total_qty
        loc_entry['total_shrinkage_value'] = round(total_val, 2)
        
        if total_qty > 0 or total_val > 0:
            sites_with_impact.append({
                "location": loc_entry.get('location'),
                "total_shrinkage_qty": total_qty,
                "total_shrinkage_value": round(total_val, 2)
            })

    # 4. Update the "Overall Shrinkage Summary" Insight
    for s in sites_with_impact:
        if s.get('total_shrinkage_value') is None: s['total_shrinkage_value'] = 0.0
    for i in all_global_items:
        if i.get('shrinkage_value') is None: i['shrinkage_value'] = 0.0

    sites_with_impact.sort(key=lambda x: x['total_shrinkage_value'], reverse=True)
    all_global_items.sort(key=lambda x: x['shrinkage_value'], reverse=True)
    
    top_locs = sites_with_impact[:10]
    top_prods = all_global_items[:10]
    
    updated_insight = False
    for insight in data.get('insights', []):
        if insight.get('id') == "overall_shrinkage_summary":
            insight['result_data']['top_locations'] = top_locs
            insight['result_data']['top_items'] = top_prods
            updated_insight = True
            print("Successfully updated overall_shrinkage_summary.")

    # 5. Global Summary Metrics
    if 'summary_metrics' in data:
        data['summary_metrics']['total_shrinkage_qty'] = sum(s['total_shrinkage_qty'] for s in sites_with_impact)
        data['summary_metrics']['total_shrinkage_value'] = round(sum(s['total_shrinkage_value'] for s in sites_with_impact), 2)
        data['summary_metrics']['total_locations_impacted'] = len(sites_with_impact)

    # 6. Save
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Final Fix Applied. {len(sites_with_impact)} sites now have accurate shrinkage data.")
    if top_locs:
        print(f"Verified Top Location: {top_locs[0]['location']} (${top_locs[0]['total_shrinkage_value']})")

if __name__ == "__main__":
    final_fix()
