import json

with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

found = False
for loc in data.get('location_ranking', []):
    for p in loc.get('shrinkage_products', []):
        if 'dodger' in p.get('product_name', '').lower() or '11054' in str(p.get('product_id', '')):
            print(f"Location: {loc.get('location')}")
            print(f"Product: {json.dumps(p, indent=2)}")
            found = True

if not found:
    print("Not found.")
