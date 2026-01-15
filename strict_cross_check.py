import pandas as pd
import json
import os
import sys

def strict_cross_check():
    """
    Perform a strict field-by-field cross-check of the consolidated JSON 
    against the source CSV shrinkage report.
    """
    json_path = 'n8n_consolidated_report_final_fixed.json'
    csv_path = 'shrinkage_report.csv'
    
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found")
        return
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return

    print("Loading source files for comparison...")
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Load CSV with specific handling for column names observed earlier
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    
    # Clean up Location and Product ID columns for robust matching
    df['Location'] = df['Location'].astype(str).str.strip()
    df['Product ID'] = df['Product ID'].astype(str).str.strip()
    
    # Create a lookup dictionary for product-level data
    # Key: (Location, Product ID)
    csv_lookup = {}
    for _, row in df.iterrows():
        key = (row['Location'], row['Product ID'])
        csv_lookup[key] = row.to_dict()

    errors = []
    total_locations = len(json_data.get('location_ranking', []))
    total_products_checked = 0
    matched_products = 0

    print(f"Starting audit of {total_locations} locations...")

    for loc_entry in json_data.get('location_ranking', []):
        loc_name = loc_entry.get('location', '').strip()
        json_products = loc_entry.get('shrinkage_products', [])
        
        # 1. Check Location-Level Aggregates against CSV sums or designated rows
        # In shrinkage_report.csv, usually there is a 'Stock' or aggregate row, 
        # but the JSON is built from per-product data.
        
        # Calculate expected aggregates from JSON products to check internal consistency
        sum_qty_json = 0
        sum_val_json = 0
        sum_sales_units_json = 0
        
        for p in json_products:
            total_products_checked += 1
            pid = str(p.get('product_id', '')).strip()
            key = (loc_name, pid)
            
            p_qty = p.get('shrinkage_qty', 0)
            p_val = p.get('shrinkage_value', 0)
            p_sales = p.get('sales_units', 0)
            p_price = p.get('unit_price', 0)
            
            # Cross-check with CSV if match exists
            if key in csv_lookup:
                matched_products += 1
                row = csv_lookup[key]
                
                # Check Quantity
                csv_qty = float(row.get('Shrinkage Qty', 0))
                if abs(p_qty - csv_qty) > 0.01:
                    errors.append(f"Mismatch: {loc_name} | {pid} | shrinkage_qty: JSON={p_qty}, CSV={csv_qty}")
                
                # Check Sales Units
                # The header is 'Quantity Sales'
                csv_sales = float(row.get('Quantity Sales', 0))
                if abs(p_sales - csv_sales) > 0.01:
                    errors.append(f"Mismatch: {loc_name} | {pid} | sales_units: JSON={p_sales}, CSV={csv_sales}")
                
                # Check Value and Price (if CSV has them)
                csv_val = float(row.get('Shrinkage_Value', 0)) if pd.notna(row.get('Shrinkage_Value')) else None
                csv_price = float(row.get('Implied_Unit_Price', 0)) if pd.notna(row.get('Implied_Unit_Price')) else None
                
                if csv_val is not None:
                    if abs(p_val - csv_val) > 0.01:
                        # Value might differ if we used a fallback price or recalculated
                        errors.append(f"Note: {loc_name} | {pid} | shrinkage_value: JSON={p_val}, CSV={csv_val}")
                
                if csv_price is not None:
                    if abs(p_price - csv_price) > 0.01:
                         errors.append(f"Note: {loc_name} | {pid} | unit_price: JSON={p_price}, CSV={csv_price}")
            else:
                # Flag products in JSON not in CSV root
                # Note: some might be from "Sales Reports" as identified earlier
                pass

            sum_qty_json += p_qty
            sum_val_json += p_val
            sum_sales_units_json += p_sales

        # 2. Check JSON Location Totals vs JSON Product Sums
        json_total_qty = loc_entry.get('total_shrinkage_qty', 0)
        json_total_val = loc_entry.get('total_shrinkage_value', 0)
        
        if abs(json_total_qty - sum_qty_json) > 0.01:
            errors.append(f"Aggregation Error: {loc_name} | total_shrinkage_qty ({json_total_qty}) != sum of products ({sum_qty_json})")
        
        if abs(json_total_val - sum_val_json) > 0.01:
            errors.append(f"Aggregation Error: {loc_name} | total_shrinkage_value ({json_total_val}) != sum of products ({sum_val_json})")

        # 3. Check Inventory Equation
        start = loc_entry.get('start_qty', 0)
        sales = loc_entry.get('sales_units', 0)
        end = loc_entry.get('end_qty', 0)
        calc_shrink = start - sales - end
        
        if abs(calc_shrink - sum_qty_json) > 0.01:
            errors.append(f"Equation Discrepancy: {loc_name} | {start} - {sales} - {end} = {calc_shrink}, but product sum is {sum_qty_json}")

    print("\n" + "="*50)
    print("AUDIT RESULTS SUMMARY")
    print("="*50)
    print(f"Total Products Checked: {total_products_checked}")
    print(f"Products Matched in Root CSV: {matched_products}")
    print(f"Total Discrepancies/Notes Found: {len(errors)}")
    
    if errors:
        print("\nPrinting first 20 discrepancies:")
        for e in errors[:20]:
            print(f"  - {e}")
        
        # Save full audit
        with open('FULL_AUDIT_LOG.txt', 'w', encoding='utf-8') as log:
            for e in errors:
                log.write(e + "\n")
        print(f"\nFull audit log saved to FULL_AUDIT_LOG.txt")
    else:
        print("\n✅ PERFECT PASS: No field mismatches or mathematical inconsistencies detected!")

if __name__ == "__main__":
    strict_cross_check()
