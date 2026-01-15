
import json

def verify():
    with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ranking = data.get("location_ranking", [])
    
    for loc in ranking:
        if "Holiday Inn Express & Suites Barstow" in loc.get("location"):
            print("Found Entry:")
            print(f"Location: {loc.get('location')}")
            print(f"Total Shrink Qty: {loc.get('total_shrinkage_qty')}")
            print(f"Start Qty: {loc.get('start_qty')}")
            print(f"End Qty: {loc.get('end_qty')}")
            print(f"Sales Units: {loc.get('sales_units')}")
            expected = loc.get('start_qty') - loc.get('sales_units') - loc.get('end_qty')
            print(f"Expected (Start-Sales-End): {expected}")
            
            # Check products
            prods = loc.get("shrinkage_products", [])
            print(f"Product Count: {len(prods)}")
            misplaced = [p for p in prods if p.get("location") != loc.get("location")]
            print(f"Misplaced Products: {len(misplaced)}")

if __name__ == "__main__":
    verify()
