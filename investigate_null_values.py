import json

def check_null_shrinkage_values():
    """Check for null shrinkage_value fields in the report"""
    
    with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    ranking = report.get("location_ranking", [])
    
    total_products = 0
    null_value_count = 0
    null_examples = []
    
    for loc_entry in ranking:
        products = loc_entry.get("shrinkage_products", [])
        
        for p in products:
            total_products += 1
            shrink_val = p.get("shrinkage_value")
            
            if shrink_val is None:
                null_value_count += 1
                if len(null_examples) < 10:
                    null_examples.append({
                        "location": loc_entry.get("location"),
                        "product_name": p.get("product_name"),
                        "product_id": p.get("product_id"),
                        "shrinkage_qty": p.get("shrinkage_qty"),
                        "shrinkage_value": shrink_val,
                        "unit_price": p.get("unit_price")
                    })
    
    print(f"Total products: {total_products}")
    print(f"Products with null shrinkage_value: {null_value_count}")
    print(f"Percentage: {(null_value_count/total_products*100):.1f}%")
    
    if null_examples:
        print(f"\nFirst {len(null_examples)} examples:")
        for ex in null_examples:
            print(f"\n  Location: {ex['location']}")
            print(f"  Product: {ex['product_name']} ({ex['product_id']})")
            print(f"  Shrinkage Qty: {ex['shrinkage_qty']}")
            print(f"  Shrinkage Value: {ex['shrinkage_value']}")
            print(f"  Unit Price: {ex['unit_price']}")
    
    # Check source data
    print("\n" + "="*80)
    print("Checking source data...")
    
    with open('n8n_shrinkage_report_minified.json', 'r', encoding='utf-8') as f:
        minified = json.load(f)
    
    source_products = minified.get("data", [])
    
    # Find one of the null examples in source
    if null_examples:
        example = null_examples[0]
        for sp in source_products:
            if sp.get("product_id") == example["product_id"] and sp.get("location") == example["location"]:
                print(f"\nSource data for {example['product_name']}:")
                print(f"  shrinkage_value: {sp.get('shrinkage_value')}")
                print(f"  unit_price: {sp.get('unit_price')}")
                print(f"  shrinkage_qty: {sp.get('shrinkage_qty')}")
                break

if __name__ == "__main__":
    check_null_shrinkage_values()
