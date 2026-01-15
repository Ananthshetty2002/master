import json

with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

missing = []
for loc in data.get('location_ranking', []):
    for p in loc.get('shrinkage_products', []):
        if p.get('unit_price') is None or p.get('unit_price') == 0:
            missing.append({
                'location': loc.get('location'),
                'product_id': p.get('product_id'),
                'product_name': p.get('product_name'),
                'shrinkage_qty': p.get('shrinkage_qty')
            })

with open('all_missing.json', 'w', encoding='utf-8') as f:
    json.dump(missing, f, indent=2)

print(f"Found {len(missing)} missing items.")
