import json
import os
import pandas as pd

def recalculate_insights():
    work_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    json_path = os.path.join(work_dir, "n8n_consolidated_report_final_fixed.json")
    shrinkage_csv = os.path.join(work_dir, "shrinkage_report.csv")
    pilot_csv = os.path.join(work_dir, "pilot_shrink_log.csv")
    
    if not os.path.exists(json_path):
        print("JSON report not found.")
        return

    # 1. Build Price Mapping
    price_map = {}
    
    if os.path.exists(shrinkage_csv):
        print(f"Loading prices from {shrinkage_csv}...")
        df_shrink = pd.read_csv(shrinkage_csv)
        df_shrink.columns = [c.strip() for c in df_shrink.columns]
        # Use Product ID and Unit_Price
        if 'Product ID' in df_shrink.columns and 'Unit_Price' in df_shrink.columns:
            for _, row in df_shrink.iterrows():
                pid = str(row['Product ID']).strip()
                price = float(row['Unit_Price']) if not pd.isna(row['Unit_Price']) else 0.0
                if price > 0:
                    if pid not in price_map or price > price_map[pid]:
                        price_map[pid] = price

    if os.path.exists(pilot_csv):
        print(f"Loading prices from {pilot_csv}...")
        df_pilot = pd.read_csv(pilot_csv)
        df_pilot.columns = [c.strip() for c in df_pilot.columns]
        # Use Product Code and Total Product cost / Quantity
        if 'Product Code' in df_pilot.columns and 'Quantity' in df_pilot.columns and 'Total Product cost' in df_pilot.columns:
            for _, row in df_pilot.iterrows():
                pid = str(row['Product Code']).strip()
                qty = float(row['Quantity'])
                cost = float(row['Total Product cost']) if not pd.isna(row['Total Product cost']) else 0.0
                if qty != 0 and cost != 0:
                    up = abs(cost / qty)
                    if pid not in price_map or up > price_map[pid]:
                        price_map[pid] = up

    print(f"Built price lookup with {len(price_map)} products.")

    # 2. Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 3. Enrich Products and Summarize Sites
    print("Enriching products and recalculating site totals...")
    all_sites_summary = []
    
    for loc_entry in data.get('location_ranking', []):
        loc_name = loc_entry.get('location')
        shrink_prods = loc_entry.get('shrinkage_products', [])
        
        for p in shrink_prods:
            pid = p.get('product_id')
            qty = p.get('shrinkage_qty', 0)
            
            # Fill missing price/value
            if pid in price_map:
                up = price_map[pid]
                p['unit_price'] = up
                if p.get('shrinkage_value', 0) == 0:
                    p['shrinkage_value'] = round(qty * up, 2)
            
        # Recalculate site totals
        total_qty = sum(p.get('shrinkage_qty', 0) for p in shrink_prods)
        total_val = sum(p.get('shrinkage_value', 0) for p in shrink_prods)
        
        loc_entry['total_shrinkage_qty'] = total_qty
        loc_entry['total_shrinkage_value'] = total_val
        
        if total_qty != 0 or total_val != 0:
            all_sites_summary.append({
                "location": loc_name,
                "total_shrinkage_qty": total_qty,
                "total_shrinkage_value": total_val
            })

    print(f"Recalculated {len(all_sites_summary)} active sites.")

    # 4. Update Summary Insight (overall_shrinkage_summary)
    all_sites_summary.sort(key=lambda x: x['total_shrinkage_value'], reverse=True)
    top_10_locs = all_sites_summary[:10]
    
    # Collect all items for top items list
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

    for insight in data.get('insights', []):
        if insight.get('id') == "overall_shrinkage_summary":
            insight['result_data']['top_locations'] = top_10_locs
            insight['result_data']['top_items'] = top_10_items
            insight['severity'] = "Critical" if top_10_locs and top_10_locs[0]['total_shrinkage_value'] > 1000 else "High"

    # 5. Update Global Summary Metrics
    if 'summary_metrics' in data:
        data['summary_metrics']['total_shrinkage_qty'] = sum(l['total_shrinkage_qty'] for l in all_sites_summary)
        data['summary_metrics']['total_shrinkage_value'] = sum(l['total_shrinkage_value'] for l in all_sites_summary)
        data['summary_metrics']['total_locations_impacted'] = len(all_sites_summary)

    # 6. Save Updated JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print("JSON report successfully updated with accurate rankings.")
    if top_10_locs:
        print(f"New Top Site: {top_10_locs[0]['location']} (${top_10_locs[0]['total_shrinkage_value']:.2f})")

if __name__ == "__main__":
    recalculate_insights()
