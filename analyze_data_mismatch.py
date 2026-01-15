import pandas as pd
import json

def debug_mismatch():
    """Debug why price lookup is failing"""
    
    # Load CSV
    df = pd.read_csv('shrinkage_report.csv')
    print("CSV Sample:")
    print(df[['Location', 'Product_ID', 'Unit_Price']].head(3))
    
    # Load JSON
    with open('n8n_consolidated_report_final_fixed.json', 'r') as f:
        report = json.load(f)
    
    ranking = report.get("location_ranking", [])
    
    # Get sample from JSON
    if ranking and ranking[0].get("shrinkage_products"):
        sample_loc = ranking[0]
        sample_prod = sample_loc["shrinkage_products"][0]
        
        print("\nJSON Sample:")
        print(f"  Location: {sample_loc.get('location')}")
        print(f"  Product ID: {sample_prod.get('product_id')}")
        print(f"  Product Name: {sample_prod.get('product_name')}")
    
    # Check if location names match
    csv_locations = set(df['Location'].unique())
    json_locations = set(loc.get('location') for loc in ranking)
    
    print(f"\nCSV locations: {len(csv_locations)}")
    print(f"JSON locations: {len(json_locations)}")
    print(f"Matching locations: {len(csv_locations & json_locations)}")
    
    # Show sample locations from each
    print(f"\nSample CSV locations:")
    for loc in list(csv_locations)[:3]:
        print(f"  - {loc}")
    
    print(f"\nSample JSON locations:")
    for loc in list(json_locations)[:3]:
        print(f"  - {loc}")
    
    # Check product IDs
    csv_products = set(df['Product_ID'].unique())
    json_products = set()
    for loc in ranking:
        for p in loc.get("shrinkage_products", []):
            json_products.add(p.get("product_id"))
    
    print(f"\nCSV product IDs: {len(csv_products)}")
    print(f"JSON product IDs: {len(json_products)}")
    print(f"Matching product IDs: {len(csv_products & json_products)}")

if __name__ == "__main__":
    debug_mismatch()
