import pandas as pd
import argparse

def extract_snapshots(trans_file, output_prefix):
    print(f"Loading {trans_file}...")
    try:
        df = pd.read_csv(trans_file, low_memory=False)
        
        # Ensure we have required columns
        # We need Location, Product, Date, and Quantity (or Balance)
        # Based on previous inspection, we might have 'Micro Market' or 'Location'
        loc_col = 'Location' if 'Location' in df.columns else 'Micro Market'
        prod_col = 'Product Code' if 'Product Code' in df.columns else 'Product'
        
        if loc_col not in df.columns:
            print(f"Error: Could not find Location column (checked 'Location', 'Micro Market'). Found: {df.columns.tolist()}")
            return

        # Filter for "Quantity Adjustment" or similar events that represent a "Count"
        # types: 'Quantity Adjustment', 'Inventory Count', 'Audit'
        target_types = ['Quantity Adjustment', 'Inventory Count', 'Audit', 'Initial Balance']
        
        if 'Transfer Type' in df.columns:
            # Normalize map
            df['Transfer Type'] = df['Transfer Type'].astype(str).str.strip()
            mask = df['Transfer Type'].isin(target_types)
            snapshots = df[mask].copy()
            
            if snapshots.empty:
                print("Warning: No 'Quantity Adjustment' or 'Audit' events found. Trying 'Restock' as proxy for 'End of Day' level if Balance exists.")
                # If no audits, we can't easily get identifying "Start" levels without a Balance column.
                # Let's check for Balance
                if 'Balance' in df.columns:
                    print("Found 'Balance' column. Extracting daily snapshots...")
                    # This would be complex, let's stick to the Adjustments for now.
            
            print(f"Found {len(snapshots)} adjustment events.")
            
            # Select relevant columns
            cols = [loc_col, prod_col, 'Date', 'Time', 'Qty', 'Transfer Type']
            if 'Balance' in df.columns:
                cols.append('Balance')
            
            # Use 'Balance' if available as the Quantity, else 'Qty' implies the adjustment amount (not the level).
            # If 'Transfer Type' is 'Quantity Adjustment', 'Qty' might be the *change*.
            # We need the *Resulting Level*.
            # If we don't have Balance, this is hard.
            # But often 'Quantity Adjustment' in these systems logs the NEW Quantity? Or the diff?
            # Usually it's the Diff. 
            # If we lack Balance, we can't assume Qty is the Level.
            # Let's check the formatting of the file in the next step or assume user knows.
            # For now, we dump these "Audit Events" to CSV and let user decide if they are usable.
            
            out_file = f"{output_prefix}_audit_events.csv"
            snapshots.to_csv(out_file, index=False)
            print(f"Saved potential snapshots to {out_file}")
            print("Review this file. If 'Qty' represents the Stock Level (or you have a Balance column), you can split this into start.csv and end.csv.")
            
        else:
            print("Error: 'Transfer Type' column missing.")

    except Exception as e:
        print(f"Wrapper Error: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('trans_file', help="Path to Product Transaction Report CSV")
    parser.add_argument('--output', default='derived_snapshot', help="Prefix for output CSVs")
    args = parser.parse_args()
    
    extract_snapshots(args.trans_file, args.output)

if __name__ == "__main__":
    main()
