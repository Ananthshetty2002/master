
import json

def check_v2():
    with open('n8n_shrinkage_report_v2.json', 'r') as f:
        data = json.load(f)
        ranking = data.get("location_ranking", [])
        
        for loc in ranking:
            if "Altura" in loc.get("location", ""):
                print(f"Location: {loc.get('location')}")
                prods = loc.get("shrinkage_products", [])
                print(f"Product Count: {len(prods)}")
                if prods:
                    print(f"Sample Product: {prods[0]}")
                break

if __name__ == "__main__":
    check_v2()
