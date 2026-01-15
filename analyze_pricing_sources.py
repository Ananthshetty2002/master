import pandas as pd
import json

def check_pricing_sources():
    """Check available pricing data in CSV files"""
    
    print("Checking shrinkage_report.csv...")
    try:
        df = pd.read_csv('shrinkage_report.csv')
        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Check for price columns
        price_cols = [col for col in df.columns if 'price' in col.lower() or 'value' in col.lower()]
        print(f"\nPrice-related columns: {price_cols}")
        
        # Show sample
        if len(df) > 0:
            print(f"\nSample row:")
            sample = df.iloc[0]
            for col in df.columns:
                print(f"  {col}: {sample[col]}")
        
        # Check for nulls in price column
        if price_cols:
            for col in price_cols:
                null_count = df[col].isna().sum()
                print(f"\n{col}: {null_count} nulls out of {len(df)} ({null_count/len(df)*100:.1f}%)")
    
    except Exception as e:
        print(f"Error reading shrinkage_report.csv: {e}")
    
    print("\n" + "="*80)
    print("Checking product_prices.csv...")
    try:
        df_prices = pd.read_csv('product_prices.csv')
        print(f"Rows: {len(df_prices)}")
        print(f"Columns: {list(df_prices.columns)}")
        
        if len(df_prices) > 0:
            print(f"\nSample:")
            print(df_prices.head())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_pricing_sources()
