import json
from collections import defaultdict

def regenerate_insights():
    # 1. Load Ground Truth Data (Numerical)
    with open('n8n_consolidated_report_GRAND_RESET.json', 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    # ... (rest is same until save)
    
    # 2. Load Existing Insights to Preserve Non-Numerical Wisdom (Staff Risk etc.)
    with open('analyzed_metrics.json', 'r', encoding='utf-8') as f:
        old_insights = json.load(f)
    
    # Create a mapping of Insight Title -> Old Data for preservation
    insight_cache = {i.get('location'): i for i in old_insights}
    
    # Data Structures for Calculations
    locs = report_data['location_ranking']
    all_products = []
    prod_agg = defaultdict(lambda: {'qty': 0, 'val': 0, 'name': ''})
    
    for l in locs:
        for p in l['shrinkage_products']:
            p['location'] = l['location'] # Add loc context
            all_products.append(p)
            
            p_id = p['product_id']
            prod_agg[p_id]['qty'] += p.get('shrinkage_qty', 0)
            prod_agg[p_id]['val'] += p.get('shrinkage_value', 0)
            prod_agg[p_id]['name'] = p.get('product_name', p_id)

    new_insights = []

    # --- SEGMENT 1: Location Ranking by Percentage of Inventory Lost ---
    # Metric: total_shrinkage_qty / start_qty
    loc_perc_ranking = []
    for l in locs:
        start = l.get('start_qty', 0)
        shrink = l.get('total_shrinkage_qty', 0)
        perc = (shrink / start * 100) if start > 0 else 0
        loc_perc_ranking.append({
            'location': l['location'],
            'shrinkage_qty': shrink,
            'start_qty': start,
            'loss_percentage': f"{round(perc, 2)}%"
        })
    loc_perc_ranking.sort(key=lambda x: float(x['loss_percentage'].replace('%','')), reverse=True)
    new_insights.append({
        "location": "Location Ranking by Percentage of Inventory Lost",
        "data": loc_perc_ranking[:20]
    })

    # --- SEGMENT 2: Top 10 High Shrinkage Items by Quantity (Cross-Site) ---
    top_items_qty = sorted(prod_agg.items(), key=lambda x: x[1]['qty'], reverse=True)
    new_insights.append({
        "location": "Top 10 High Shrinkage Items by Quantity (Cross-Site)",
        "data": [{"product_id": k, "product_name": v['name'], "total_shrinkage_qty": round(v['qty'], 2)} for k, v in top_items_qty[:10]]
    })

    # --- SEGMENT 3: Financial Impact: Top 10 Products by Total Shrinkage Value ---
    top_items_val = sorted(prod_agg.items(), key=lambda x: x[1]['val'], reverse=True)
    new_insights.append({
        "location": "Financial Impact: Top 10 Products by Total Shrinkage Value",
        "data": [{"product_id": k, "product_name": v['name'], "total_shrinkage_value": round(v['val'], 2)} for k, v in top_items_val[:10]]
    })

    # --- SEGMENT 4: Ghost Disappearances: High Loss Items with Zero Recorded Sales ---
    # Criteria: sales_units == 0 and shrinkage_qty > 0
    ghosts = [p for p in all_products if p.get('sales_units', 0) == 0 and p.get('shrinkage_qty', 0) > 0]
    ghosts_sorted = sorted(ghosts, key=lambda x: x.get('shrinkage_qty', 0), reverse=True)
    new_insights.append({
        "location": "Ghost Disappearances: High Loss Items with Zero Recorded Sales",
        "data": [{"product_id": p['product_id'], "product_name": p['product_name'], "location": p['location'], "shrinkage_qty": p['shrinkage_qty']} for p in ghosts_sorted[:20]]
    })

    # --- SEGMENT 5: High Loss Rates: Items with Shrinkage > 50% of Starting Stock ---
    high_loss = []
    for p in all_products:
        start = p.get('quantity_start', 0)
        shrink = p.get('shrinkage_qty', 0)
        if start > 0 and (shrink / start) > 0.5:
            high_loss.append({
                "product_id": p['product_id'],
                "product_name": p['product_name'],
                "location": p['location'],
                "loss_rate": f"{round(shrink/start*100, 2)}%"
            })
    new_insights.append({
        "location": "High Loss Rates: Items with Shrinkage > 50% of Starting Stock",
        "data": sorted(high_loss, key=lambda x: float(x['loss_rate'].replace('%','')), reverse=True)[:20]
    })

    # --- SEGMENT 6-8: Preserve if exists (Daily Waste, Risk scores) ---
    for title in ["Daily Waste Cost Trends & Average", "Risk Band Summary (Risk Band vs Average Loss)", "Staff Risk Score Index", "Par Level Recommendations to Reduce Waste"]:
        if title in insight_cache:
            new_insights.append(insight_cache[title])

    # 3. Save Regenerated Insights
    with open('analyzed_metrics_RE-FIXED.json', 'w', encoding='utf-8') as f:
        json.dump(new_insights, f, indent=2)
    
    # 4. Final step: Embed EVERYTHING into a single file
    report_data['overall_shrinkage_summary'] = new_insights
    with open('n8n_consolidated_report_FINAL_VERIFIED_V2.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2)

    print("Regeneration Complete.")
    print("Final report saved to: n8n_consolidated_report_FINAL_VERIFIED_V2.json")

if __name__ == "__main__":
    regenerate_insights()
