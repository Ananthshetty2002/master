import json

with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for loc in data.get('location_ranking', []):
    for p in loc.get('shrinkage_products', []):
        if p.get('unit_price') is None or p.get('unit_price') == 0:
            print(f"Location: {loc.get('location')}")
            print(f"Product: {p.get('product_name')} ({p.get('product_id')})")
            print(f"Shrinkage Qty: {p.get('shrinkage_qty')}")
            print("-" * 20)
