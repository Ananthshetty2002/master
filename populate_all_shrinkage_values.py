import pandas as pd
import json
import glob
import os

def build_comprehensive_price_lookup():
    """Build price lookup from ALL available sources"""
    
    print("="*80)
    print("BUILDING COMPREHENSIVE PRICE LOOKUP")
    print("="*80)
    
    product_prices = {}
    
    # Source 1: shrinkage_report.csv
    print("\n1. Processing shrinkage_report.csv...")
    try:
        df = pd.read_csv('shrinkage_report.csv')
        print(f"   Loaded {len(df)} rows")
        
        for _, row in df.iterrows():
            prod_id = str(row.get('Product ID', '')).strip()
            shrink_val = row.get('Shrinkage_Value')
            shrink_qty = row.get('Shrinkage_Qty')
            
            if prod_id and pd.notna(shrink_val) and pd.notna(shrink_qty) and float(shrink_qty) > 0:
                unit_price = float(shrink_val) / float(shrink_qty)
                if unit_price > 0:
                    product_prices[prod_id] = unit_price
        
        print(f"   Extracted {len(product_prices)} prices")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Source 2: Sales By Products Reports
    print("\n2. Processing Sales By Products reports...")
    sales_files = glob.glob('Sales By Products Report*.csv')
    print(f"   Found {len(sales_files)} files")
    
    for file in sales_files:
        try:
            df = pd.read_csv(file, low_memory=False)
            
            for _, row in df.iterrows():
                # Try different column name variations
                prod_id = None
                for col in ['Product ID', 'ProductID', 'Product_ID', 'product_id']:
                    if col in df.columns:
                        prod_id = str(row.get(col, '')).strip()
                        if prod_id:
                            break
                
                # Try to find price
                price = None
                for col in ['Unit Price', 'Price', 'Unit_Price', 'price', 'Amount']:
                    if col in df.columns:
                        val = row.get(col)
                        if pd.notna(val) and float(val) > 0:
                            price = float(val)
                            break
                
                # If no direct price, try calculating from total/quantity
                if not price:
                    total_col = None
                    qty_col = None
                    for col in ['Total', 'Total Amount', 'Sales_Value']:
                        if col in df.columns:
                            total_col = col
                            break
                    for col in ['Quantity', 'Qty', 'Sales_Units']:
                        if col in df.columns:
                            qty_col = col
                            break
                    
                    if total_col and qty_col:
                        total = row.get(total_col)
                        qty = row.get(qty_col)
                        if pd.notna(total) and pd.notna(qty) and float(qty) > 0:
                            price = float(total) / float(qty)
                
                if prod_id and price and price > 0:
                    if prod_id not in product_prices:
                        product_prices[prod_id] = price
        
        except Exception as e:
            print(f"   Error in {file}: {e}")
    
    print(f"   Total unique products with prices: {len(product_prices)}")
    
    return product_prices

def populate_all_shrinkage_values():
    """Populate ALL shrinkage values in the JSON report"""
    
    # Build price lookup
    prices = build_comprehensive_price_lookup()
    
    if not prices:
        print("\nERROR: No prices found!")
        return 0, 0
    
    # Load JSON
    print("\n" + "="*80)
    print("POPULATING JSON REPORT")
    print("="*80)
    
    print("\nLoading JSON...")
    with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    ranking = report.get("location_ranking", [])
    print(f"Loaded {len(ranking)} locations")
    
    # Update products
    print("\nUpdating products...")
    updated = 0
    not_found = 0
    
    for loc_entry in ranking:
        products = loc_entry.get("shrinkage_products", [])
        
        for p in products:
            prod_id = str(p.get("product_id", "")).strip()
            shrinkage_qty = float(p.get("shrinkage_qty", 0) or 0)
            
            if prod_id in prices:
                unit_price = prices[prod_id]
                shrinkage_value = shrinkage_qty * unit_price
                
                p["unit_price"] = round(unit_price, 2)
                p["shrinkage_value"] = round(shrinkage_value, 2)
                updated += 1
            else:
                not_found += 1
        
        # Recalculate location total
        total = sum(float(p.get("shrinkage_value", 0) or 0) for p in products)
        loc_entry["total_shrinkage_value"] = round(total, 2)
    
    print(f"Updated: {updated}")
    print(f"Not found: {not_found}")
    print(f"Coverage: {updated/(updated+not_found)*100:.1f}%")
    
    # Save with backup
    print("\nSaving...")
    
    # Create backup first
    if os.path.exists('n8n_consolidated_report_final_fixed.json'):
        import shutil
        shutil.copy('n8n_consolidated_report_final_fixed.json', 
                   'n8n_consolidated_report_final_fixed.json.backup')
        print("  Backup created")
    
    # Save
    with open('n8n_consolidated_report_final_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("  Saved!")
    
    # Verify
    print("\nVerifying save...")
    with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
        verify = json.load(f)
    
    sample = verify['location_ranking'][0]['shrinkage_products'][0]
    print(f"  Sample: {sample.get('product_name')}")
    print(f"  Value: ${sample.get('shrinkage_value')}")
    print(f"  Price: ${sample.get('unit_price')}")
    
    print("\n" + "="*80)
    print("COMPLETE!")
    print("="*80)
    
    return updated, not_found

if __name__ == "__main__":
    updated, not_found = populate_all_shrinkage_values()
    print(f"\nFinal: {updated} updated, {not_found} not found")
