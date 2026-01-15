import pandas as pd
import json
import numpy as np

def safe_float(x):
    try:
        if pd.isna(x) or x == '': return 0.0
        return float(x)
    except:
        return 0.0

def grand_reset():
    # 1. Load Source of Truth
    csv_path = 'shrinkage_report_refined.csv'
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    
    # Ensure numerical columns
    cols_to_fix = ['Quantity_Start', 'Quantity_End', 'Sales_Quantity', 'Known_Adjustments_Qty', 'Shrinkage_Qty', 'Implied_Unit_Price']
    for c in cols_to_fix:
        df[c] = df[c].apply(safe_float)

    # 2. Load JSON Target
    json_path = 'n8n_consolidated_report_FINAL_VERIFIED.json' 
    # (Using the last "Verified" one as base, effectively overwriting it)
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Starting Grand Reset...")
    
    # 3. Create Fast Lookup
    # Key: (Location, Product ID) -> Row Series
    # But wait, we might have multiple rows? Usually unique per loc/product.
    # Check uniqueness
    dupes = df.duplicated(subset=['Location', 'Product ID']).sum()
    if dupes > 0:
        print(f"Warning: {dupes} duplicate rows in CSV. Aggregating them.")
        df = df.groupby(['Location', 'Product ID'], as_index=False).agg({
            'Quantity_Start': 'sum',
            'Quantity_End': 'sum',
            'Sales_Quantity': 'sum',
            'Known_Adjustments_Qty': 'sum',
            'Shrinkage_Qty': 'sum',
            'Implied_Unit_Price': 'max', # Price probably same? Use max to avoid 0
            'Product Name': 'first', # If exists
            'Shrinkage_Value': 'sum'
        })
    
    # Re-index for lookup
    df.set_index(['Location', 'Product ID'], inplace=True)
    
    # 4. Process JSON Locations
    updated_prods = 0
    
    for loc_entry in data.get('location_ranking', []):
        loc_name = loc_entry.get('location', '').strip()
        
        # Get all CSV data for this location to calculate correct Location Totals
        # (We need to handle products NOT in JSON if JSON is filtered)
        # But for now, let's update products IN JSON.
        
        products = loc_entry.get('shrinkage_products', [])
        
        loc_shrink_qty_accum = 0
        loc_shrink_val_accum = 0
        loc_sales_accum = 0
        
        # Filter df for this location (optimization)
        try:
            loc_df = df.loc[loc_name] # Returns DataFrame or Series if 1 match
            if isinstance(loc_df, pd.Series): loc_df = loc_df.to_frame().T
            loc_df_idx = loc_df.set_index('Product ID') if 'Product ID' in loc_df.columns else loc_df # Already indexed by Product ID if from multi-index?
            # Actually df.loc[loc_name] drops Location level, so index is Product ID.
        except KeyError:
            # Location not in CSV?
            # print(f"Location not in CSV: {loc_name}")
            continue

        for p in products:
            pid = str(p.get('product_id', '')).strip()
            
            if pid in loc_df.index:
                row = loc_df.loc[pid]
                if isinstance(row, pd.DataFrame): row = row.iloc[0] # Handle unexpected dupes
                
                # EXTRACT
                start = row['Quantity_Start']
                end = row['Quantity_End']
                sales = row['Sales_Quantity']
                adj = row['Known_Adjustments_Qty']
                csv_shrink = row['Shrinkage_Qty']
                price = row['Implied_Unit_Price']
                
                # RECALCULATE LOGIC
                # Formula: max(0, Start - Sales - Adj - End)
                calc_shrink = max(0.0, start - sales - adj - end)
                
                # Use Calculated Shrink (User wants "correct" shrinkage)
                # But if CSV Shrink differs significantly?
                # Trust Formula as per my finding of 99% match.
                
                final_shrink = calc_shrink
                final_val = round(final_shrink * price, 4)
                
                # UPDATE JSON
                p['shrinkage_qty'] = final_shrink
                p['sales_units'] = sales
                p['unit_price'] = price
                p['shrinkage_value'] = final_val
                
                updated_prods += 1
                
                # Accumulate for Location Totals (from JSON products only)
                loc_shrink_qty_accum += final_shrink
                loc_shrink_val_accum += final_val
                loc_sales_accum += sales
            
            else:
                # Product not in CSV - keep existing or zero out?
                # User said "Shrinkage qty not correct for all".
                # Safest: Keep existing if we can't verify, or mark?
                pass
        
        # Update Location Level Stats
        # Ideally, start/end/sales at location level should be SUM of ALL CSV products for that location
        # regardless of whether they are in the JSON list (since JSON might verify only top shrinkage items).
        # Let's use the FULL CSV sums for Location Accuracy.
        
        loc_entry['start_qty'] = float(loc_df['Quantity_Start'].sum())
        loc_entry['end_qty'] = float(loc_df['Quantity_End'].sum())
        loc_entry['sales_units'] = float(loc_df['Sales_Quantity'].sum())
        
        # Calculated Location Totals
        # Tot Shrink = Sum of Product Shrinks?
        # Or Location Start - Location Sales - Location Adj - Location End?
        # Let's sum the recalculated product shrinks for the whole CSV location
        
        # Recalculate whole location from CSV to be consistent
        loc_calc_shrinks = (loc_df['Quantity_Start'] - loc_df['Sales_Quantity'] - loc_df['Known_Adjustments_Qty'] - loc_df['Quantity_End']).clip(lower=0)
        loc_entry['total_shrinkage_qty'] = float(loc_calc_shrinks.sum())
        
        # Value sum might be tricky if price missing?
        loc_calc_vals = loc_calc_shrinks * loc_df['Implied_Unit_Price']
        loc_entry['total_shrinkage_value'] = float(loc_calc_vals.sum())

    # 5. Save
    print(f"Grand Reset Complete. Updated {updated_prods} products.")
    new_path = 'n8n_consolidated_report_GRAND_RESET.json'
    with open(new_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {new_path}")

if __name__ == "__main__":
    grand_reset()
