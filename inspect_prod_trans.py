
import pandas as pd

file_path = "c:/Users/IV-UDP-DT-0122/Downloads/shrinkage/Product Transaction Report (2).csv"

try:
    print(f"Reading {file_path}...")
    # Read strict number of rows to avoid memory issues, but enough to see data
    df = pd.read_csv(file_path, low_memory=False)
    
    print("Columns:", list(df.columns))
    
    if "Location" in df.columns:
        unique_locs = df["Location"].dropna().unique()
        print(f"Unique Locations ({len(unique_locs)}):")
        print(unique_locs[:20]) # Print first 20
        
        # Check specific keywords
        westin = df[df['Location'].astype(str).str.contains("Westin", case=False, na=False)]
        print(f"Rows with 'Westin' in Location: {len(westin)}")
        if not westin.empty:
            print(westin.head(2))

    if "Transfer Type" in df.columns:
        print("Unique Transfer Types:", df["Transfer Type"].dropna().unique())
        
except Exception as e:
    print(f"Error: {e}")
