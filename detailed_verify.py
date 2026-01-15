
import json

def verify():
    with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ranking = data.get("location_ranking", [])
    
    for loc in ranking:
        if "Holiday Inn Express & Suites Barstow" in loc.get("location"):
            print("Found Entry:")
            loc_name = loc.get("location")
            print(f"Location Name: '{loc_name}'")
            print(f"Total Shrink Qty: {loc.get('total_shrinkage_qty')}")
            
            prods = loc.get("shrinkage_products", [])
            print(f"Product Count: {len(prods)}")
            
            misplaced_count = 0
            if prods:
                p = prods[0]
                p_loc = p.get("location")
                print(f"Sample Product Location: '{p_loc}'")
                if p_loc != loc_name:
                    print(f"Mismatch! '{p_loc}' != '{loc_name}'")
                    print(f"Lengths: {len(p_loc)} vs {len(loc_name)}")
                    # print byte values if needed
            
            for p in prods:
                if p.get("location") != loc_name:
                    misplaced_count += 1
            print(f"Total Misplaced: {misplaced_count}")

if __name__ == "__main__":
    verify()
