
import json

def calc():
    with open('found_entry.json', 'r') as f:
        data = json.load(f)[0]
    
    products = data.get("shrinkage_products", [])
    target_loc = data.get("location")
    
    misplaced_shrink = 0
    misplaced_count = 0
    
    for p in products:
        p_loc = p.get("location")
        if p_loc != target_loc:
            qty = p.get("shrinkage_qty", 0)
            print(f"Misplaced: {p_loc} - Qty {qty} ({p.get('product_name')})")
            misplaced_shrink += qty
            misplaced_count += 1
            
    print(f"Total Misplaced Shrink: {misplaced_shrink}")
    print(f"Total Misplaced Count: {misplaced_count}")
    print(f"Original Shrink: {data.get('total_shrinkage_qty')}")
    print(f"Corrected Shrink: {data.get('total_shrinkage_qty') - misplaced_shrink}")
    print(f"Expected Shrink (Start-Sales-End): {data.get('start_qty') - data.get('sales_units') - data.get('end_qty')}")

if __name__ == "__main__":
    calc()
