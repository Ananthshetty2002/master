import pandas as pd
import json

def debug_lookup():
    """Debug why lookup is failing"""
    
    # Load CSV
    df = pd.read_csv('shrinkage_report.csv')
    
    # Get first row
    first_row = df.iloc[0]
    csv_loc = str(first_row.get('Location', '')).strip()
    csv_prod = str(first_row.get('Product ID', '')).strip()
    
    print("CSV First Row:")
    print(f"  Location: '{csv_loc}'")
    print(f"  Product ID: '{csv_prod}'")
    print(f"  Unit_Price: {first_row.get('Unit_Price')}")
    
    # Load JSON
    with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # Get first product
    first_loc = report['location_ranking'][0]
    first_prod = first_loc['shrinkage_products'][0]
    
    json_loc = str(first_loc.get('location', '')).strip()
    json_prod = str(first_prod.get('product_id', '')).strip()
    
    print("\nJSON First Product:")
    print(f"  Location: '{json_loc}'")
    print(f"  Product ID: '{json_prod}'")
    
    # Check if they match
    print("\nDo they match?")
    print(f"  Location match: {csv_loc == json_loc}")
    print(f"  Product ID match: {csv_prod == json_prod}")
    
    # Try to find this JSON product in CSV
    print("\nSearching for JSON product in CSV...")
    matches = df[(df['Location'] == json_loc) & (df['Product ID'] == json_prod)]
    print(f"  Found {len(matches)} matches")
    
    if len(matches) > 0:
        print("  Match found!")
        print(matches[['Location', 'Product ID', 'Unit_Price']].iloc[0])

if __name__ == "__main__":
    debug_lookup()
