
import json

def check_final():
    with open('n8n_consolidated_report_final_fixed.json', 'r') as f:
        data = json.load(f)
        ranking = data.get("location_ranking", [])
        
        for loc in ranking:
            if "Altura" in loc.get("location", ""):
                print(f"Found Entry: {loc.get('location')}")
                prods = loc.get("shrinkage_products", [])
                print(f"Product Count: {len(prods)}")

if __name__ == "__main__":
    check_final()
