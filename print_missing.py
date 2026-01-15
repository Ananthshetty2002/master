import json

with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for loc in data.get('location_ranking', []):
    for p in loc.get('shrinkage_products', []):
        if p.get('unit_price') is None or p.get('unit_price') == 0:
            print(f"LOC: {loc.get('location')}")
            print(f"PROD: {json.dumps(p)}")
