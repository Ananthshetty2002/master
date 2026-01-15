import json

def check_v2_report():
    """Check n8n_shrinkage_report_v2.json for aggregate fields"""
    
    with open('n8n_shrinkage_report_v2.json', 'r', encoding='utf-8') as f:
        v2_report = json.load(f)
    
    ranking = v2_report.get("location_ranking", [])
    
    if ranking:
        sample = ranking[0]
        print("Sample location fields from v2 report:")
        for key in sample.keys():
            val = sample[key]
            if not isinstance(val, list):
                print(f"  - {key}: {val}")
        
        # Check a specific location
        for loc in ranking:
            if "Barstow" in loc.get("location", ""):
                print(f"\nBarstow location:")
                print(f"  Location: {loc.get('location')}")
                print(f"  start_qty: {loc.get('start_qty')}")
                print(f"  sales_units: {loc.get('sales_units')}")
                print(f"  end_qty: {loc.get('end_qty')}")
                print(f"  total_shrinkage_qty: {loc.get('total_shrinkage_qty')}")
                
                # Calculate expected
                start = loc.get('start_qty', 0) or 0
                sales = loc.get('sales_units', 0) or 0
                end = loc.get('end_qty', 0) or 0
                expected = start - sales - end
                print(f"  Expected shrinkage: {expected}")
                break

if __name__ == "__main__":
    check_v2_report()
