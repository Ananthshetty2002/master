
import json

def verify_sums():
    with open('found_entry.json', 'r') as f:
        data = json.load(f)
    
    entry = data[0]
    products = entry.get('shrinkage_products', [])
    
    sum_shrink = sum(p.get('shrinkage_qty', 0) for p in products)
    sum_sales = sum(p.get('sales_units', 0) for p in products)
    
    with open('sums_result.txt', 'w') as out:
        out.write(f"Reported Item Count: {len(products)}\n")
        out.write(f"Reported Top Level:\n")
        out.write(f"  Shrink: {entry.get('total_shrinkage_qty')}\n")
        out.write(f"  Sales: {entry.get('sales_units')}\n")
        out.write(f"  Start: {entry.get('start_qty')}\n")
        out.write(f"  End: {entry.get('end_qty')}\n")
        out.write(f"Calculated Sum from Products:\n")
        out.write(f"  Shrink Sum: {sum_shrink}\n")
        out.write(f"  Sales Sum: {sum_sales}\n")
        
        locations = set(p.get('location') for p in products)
        out.write(f"Distinct Locations in Products: {list(locations)}\n")

if __name__ == "__main__":
    verify_sums()
