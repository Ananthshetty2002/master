import pandas as pd

FILE = "Product Transaction Report (2).csv"

try:
    print(f"Loading {FILE}...")
    df = pd.read_csv(FILE, low_memory=False, nrows=500000) # Load partial to be fast but enough to see types
    
    print("\n--- Columns ---")
    print(df.columns.tolist())
    
    print("\n--- Sample Row ---")
    print(df.iloc[0].to_dict())
    
    if 'Transfer Type' in df.columns:
        print("\n--- Unique Transfer Types ---")
        print(df['Transfer Type'].unique())
        
    if 'Change Type' in df.columns:
        print("\n--- Unique Change Types ---")
        print(df['Change Type'].unique())
        
except Exception as e:
    print(f"Error: {e}")
