import pandas as pd

INPUT_FILE = "derived_snapshot_audit_events.csv"
START_FILE = "start.csv"
END_FILE = "end.csv"

# Define Date Targets (Based on the data inspection: Oct 2025 seems to be the range)
# We will take the earliest available date for each location/product as START
# and the latest available date as END.
# Or simple cutoffs: 
# Start: First week of Oct
# End: Last week of Oct

def process_snapshots():
    print(f"Loading {INPUT_FILE}...")
    try:
        df = pd.read_csv(INPUT_FILE)
        
        # Ensure Date is datetime
        df['Trans.Date'] = pd.to_datetime(df['Trans.Date'])
        
        # Sort by date
        df = df.sort_values('Trans.Date')
        
        print(f"Data matches range: {df['Trans.Date'].min()} to {df['Trans.Date'].max()}")
        
        # Strategy:
        # Start Inventory = Snapshot on or closest after 2025-10-01
        # End Inventory = Snapshot on or closest before 2025-10-31
        
        # For simplicity in this demo:
        # We will split the data into "Early Oct" and "Late Oct"
        # Start: Date <= 2025-10-07 (First week)
        # End: Date >= 2025-10-25 (Last week)
        # This assumes there are audits at these times. 
        # If multiple audits exist for one product, we keep the LATEST of the group (representing the final confirmed count for that period).
        
        start_mask = df['Trans.Date'] <= '2025-10-07'
        end_mask = df['Trans.Date'] >= '2025-10-25'
        
        start_df = df[start_mask].sort_values('Trans.Date').drop_duplicates(subset=['Location', 'Product Code'], keep='last')
        end_df = df[end_mask].sort_values('Trans.Date').drop_duplicates(subset=['Location', 'Product Code'], keep='last')
        
        # Prepare for Agent (Needs: Location, Product ID, Quantity)
        # Mapping: 'Product Code' -> 'Product ID', 'Qty' -> 'Quantity'
        
        output_cols = ['Location', 'Product Code', 'Qty']
        rename_map = {'Product Code': 'Product ID', 'Qty': 'Quantity'}
        
        start_ready = start_df[output_cols].rename(columns=rename_map)
        end_ready = end_df[output_cols].rename(columns=rename_map)
        
        print(f"Generated {len(start_ready)} Start records and {len(end_ready)} End records.")
        
        start_ready.to_csv(START_FILE, index=False)
        end_ready.to_csv(END_FILE, index=False)
        
        print(f"Saved to {START_FILE} and {END_FILE}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_snapshots()
