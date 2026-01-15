
import json

def verify_sums():
    with open('found_entry.json', 'r') as f:
        data = json.load(f)
    
    entry = data[0]
    products = entry.get('shrinkage_products', [])
    
    sum_shrink = sum(p.get('shrinkage_qty', 0) for p in products)
    sum_sales = sum(p.get('sales_units', 0) for p in products)
    
    print(f"Reported Item Count: {len(products)}")
    print(f"Reported Top Level: Shrink {entry.get('total_shrinkage_qty')}, Sales {entry.get('sales_units')}, Start {entry.get('start_qty')}, End {entry.get('end_qty')}")
    print(f"Calculated Sum from Products: Shrink {sum_shrink}, Sales {sum_sales}")
    
    locations = list(set(p.get('location') for p in products))
    print(f"Distinct Locations in Products: {len(locations)}")
    print(f"Sample Locations: {locations[:5]}")

if __name__ == "__main__":
    verify_sums()
