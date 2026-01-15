import json

def analyze_source():
    """Analyze source data to understand aggregate field structure"""
    
    with open('n8n_shrinkage_report_minified.json', 'r', encoding='utf-8') as f:
        minified = json.load(f)
    
    products = minified.get("data", [])
    
    # Check what fields are available
    if products:
        sample = products[0]
        print("Sample product fields:")
        for key in sample.keys():
            print(f"  - {key}: {sample[key]}")
    
    # Group by location and check aggregates
    by_location = {}
    for p in products:
        loc = p.get("location")
        if loc not in by_location:
            by_location[loc] = []
        by_location[loc].append(p)
    
    print(f"\nTotal locations in source: {len(by_location)}")
    
    # Check if we can calculate aggregates
    sample_loc = list(by_location.keys())[0]
    sample_prods = by_location[sample_loc]
    
    print(f"\nSample location: {sample_loc}")
    print(f"Products: {len(sample_prods)}")
    
    # Try to calculate aggregates
    total_shrink = sum(p.get("shrinkage_qty", 0) or 0 for p in sample_prods)
    total_sales = sum(p.get("sales_units", 0) or 0 for p in sample_prods)
    
    print(f"Total shrinkage_qty: {total_shrink}")
    print(f"Total sales_units: {total_sales}")
    
    # Check if start/end qty exist at product level
    has_start = any("start" in str(k).lower() for k in sample_prods[0].keys())
    has_end = any("end" in str(k).lower() for k in sample_prods[0].keys())
    
    print(f"\nProduct-level start qty field: {has_start}")
    print(f"Product-level end qty field: {has_end}")

if __name__ == "__main__":
    analyze_source()
