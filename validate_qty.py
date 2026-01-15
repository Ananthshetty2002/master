
import json

def verify():
    with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ranking = data.get("location_ranking", [])
    
    for loc in ranking:
        if "Holiday Inn Express & Suites Barstow" in loc.get("location"):
            print(f"Total Shrink Qty: {loc.get('total_shrinkage_qty')}")

if __name__ == "__main__":
    verify()
