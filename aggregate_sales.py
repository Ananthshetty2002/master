import pandas as pd
import glob
import os

OUTPUT_FILE = "sales.csv"
FILES_PATTERN = "transaction*week*.csv"

def aggregate_sales():
    print("Searching for sales files...")
    all_files = glob.glob(FILES_PATTERN)
    
    if not all_files:
        print("No sales files found!")
        return

    df_list = []
    print(f"Found {len(all_files)} files. Processing...")
    
    for f in all_files:
        try:
            # We only need relevant columns: Location, Product, Qty, Total Sales
            # Let's inspect headers on fly or just load loosely
            # Based on previous knowledge: 'Micromarket', 'Product Code', 'Qty', 'Total Sales'
            
            df = pd.read_csv(f, low_memory=False)
            
            # Normalize Columns
            rename_map = {
                'Micromarket': 'Location', 'Micro Market': 'Location', 'Site': 'Location',
                'Product Code': 'Product ID', 'Product': 'Product ID',
                'Qty': 'Quantity', 'Qty Sold': 'Quantity',
                'Total Sales': 'Value', 'Sales': 'Value', 'Total Price': 'Value'
            }
            df.rename(columns=rename_map, inplace=True)
            
            # Remove duplicate columns if any (e.g. if both 'Qty' and 'Quantity' existed and both mapped to 'Quantity')
            df = df.loc[:, ~df.columns.duplicated()]
            
            # Keep only needed
            needed = ['Location', 'Product ID', 'Quantity', 'Value']
            available = [c for c in needed if c in df.columns]
            
            if 'Location' in available and 'Product ID' in available:
                df_subset = df[available]
                df_list.append(df_subset)
            else:
                print(f"Skipping {os.path.basename(f)}: Missing location or product column.")
                
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    if df_list:
        full_sales = pd.concat(df_list, ignore_index=True)
        # Aggregate logic: Sum Qty and Value per Location/Product
        # Ensure numeric
        full_sales['Quantity'] = pd.to_numeric(full_sales['Quantity'], errors='coerce').fillna(0)
        full_sales['Value'] = pd.to_numeric(full_sales['Value'], errors='coerce').fillna(0)
        
        agg = full_sales.groupby(['Location', 'Product ID']).agg({
            'Quantity': 'sum',
            'Value': 'sum'
        }).reset_index()
        
        agg.to_csv(OUTPUT_FILE, index=False)
        print(f"Successfully created {OUTPUT_FILE} with {len(agg)} records.")
    else:
        print("Failed to aggregate data.")

if __name__ == "__main__":
    aggregate_sales()
