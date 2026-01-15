import json
import pandas as pd

def identify_null_products():
    """Identify and export the 88 products with null shrinkage values"""
    
    with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    ranking = report.get("location_ranking", [])
    
    null_products = []
    
    for loc_entry in ranking:
        loc_name = loc_entry.get("location")
        products = loc_entry.get("shrinkage_products", [])
        
        for p in products:
            if p.get("shrinkage_value") is None:
                null_products.append({
                    "location": loc_name,
                    "product_id": p.get("product_id"),
                    "product_name": p.get("product_name"),
                    "shrinkage_qty": p.get("shrinkage_qty"),
                    "sales_units": p.get("sales_units")
                })
    
    print(f"Found {len(null_products)} products with null shrinkage_value")
    
    # Save to CSV for analysis
    df = pd.DataFrame(null_products)
    df.to_csv('null_value_products.csv', index=False)
    print(f"Saved to null_value_products.csv")
    
    # Show unique products
    unique_products = df[['product_id', 'product_name']].drop_duplicates()
    print(f"\nUnique products: {len(unique_products)}")
    print("\nSample products:")
    print(unique_products.head(10))
    
    return null_products

if __name__ == "__main__":
    null_prods = identify_null_products()
