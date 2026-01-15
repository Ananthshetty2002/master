import pandas as pd
import json
import glob

def extract_prices_from_sales():
    """Extract product prices from Sales By Products reports"""
    
    print("Finding Sales By Products CSV files...")
    sales_files = glob.glob('Sales By Products Report*.csv')
    print(f"Found {len(sales_files)} files")
    
    if not sales_files:
        print("No sales files found!")
        return {}
    
    # Extract prices from all sales files
    product_prices = {}
    
    for file in sales_files:
        print(f"\nProcessing {file}...")
        try:
            df = pd.read_csv(file)
            print(f"  Rows: {len(df)}")
            
            # Look for price columns
            price_cols = [c for c in df.columns if 'price' in c.lower() or 'amount' in c.lower()]
            print(f"  Price columns: {price_cols}")
            
            # Try to extract prices
            for _, row in df.iterrows():
                prod_id = str(row.get('Product ID', row.get('ProductID', ''))).strip()
                
                # Try different price column names
                price = None
                for col in ['Unit Price', 'Price', 'Unit_Price', 'price']:
                    if col in df.columns:
                        price = row.get(col)
                        if pd.notna(price) and price > 0:
                            break
                
                if prod_id and price and pd.notna(price):
                    if prod_id in product_prices:
                        # Average multiple prices
                        product_prices[prod_id] = (product_prices[prod_id] + float(price)) / 2
                    else:
                        product_prices[prod_id] = float(price)
        
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"\nExtracted prices for {len(product_prices)} unique products")
    return product_prices

def populate_from_sales():
    """Populate remaining null values using Sales report prices"""
    
    print("="*80)
    print("POPULATING FROM SALES REPORTS")
    print("="*80)
    
    # Extract prices
    sales_prices = extract_prices_from_sales()
    
    if not sales_prices:
        print("\nNo prices found in sales reports!")
        return 0, 0
    
    # Load JSON
    print("\nLoading JSON...")
    with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    ranking = report.get("location_ranking", [])
    
    # Update only null products
    updated = 0
    still_null = 0
    
    for loc_entry in ranking:
        products = loc_entry.get("shrinkage_products", [])
        
        for p in products:
            if p.get("shrinkage_value") is None:  # Only update nulls
                prod_id = str(p.get("product_id", "")).strip()
                shrinkage_qty = p.get("shrinkage_qty", 0) or 0
                
                if prod_id in sales_prices:
                    unit_price = sales_prices[prod_id]
                    shrinkage_value = shrinkage_qty * unit_price
                    
                    p["unit_price"] = round(unit_price, 2)
                    p["shrinkage_value"] = round(shrinkage_value, 2)
                    updated += 1
                else:
                    still_null += 1
        
        # Recalculate total
        total = sum(p.get("shrinkage_value", 0) or 0 for p in products)
        loc_entry["total_shrinkage_value"] = round(total, 2)
    
    print(f"\nUpdated: {updated}")
    print(f"Still null: {still_null}")
    
    # Save
    print("\nSaving...")
    with open('n8n_consolidated_report_final_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("Done!")
    
    return updated, still_null

if __name__ == "__main__":
    updated, still_null = populate_from_sales()
