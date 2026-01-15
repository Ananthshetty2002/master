
import json

def verify():
    with open('n8n_consolidated_report.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ranking = data.get("location_ranking", [])
    
    found = False
    for loc in ranking:
        if "Barstow" in loc.get("location", ""):
            print("Found Entry:")
            print(f"Location: {loc.get('location')}")
            print(f"Total Shrink Qty: {loc.get('total_shrinkage_qty')}")
            
            prods = loc.get("shrinkage_products", [])
            print(f"Product Count: {len(prods)}")
            
            calc_shrink = sum(p.get("shrinkage_qty", 0) for p in prods)
            print(f"Calculated Shrink Sum: {calc_shrink}")
            
            found = True
            break
            
    if not found:
        print("Barstow not found")

if __name__ == "__main__":
    verify()
