import pandas as pd
import glob
import os
import json

def analyze_trends():
    files = sorted(glob.glob('transaction*week*.csv'))
    print(f"Found {len(files)} transaction files.")
    
    weekly_stats = []
    
    for f in files:
        try:
            print(f"Processing {f}...")
            # Use 'Created On' as date (index 0) and 'Total Sales' (index 17) based on inspection
            df = pd.read_csv(f, usecols=['Created On', 'Total Sales', 'Product Desc', 'Micro Market'], low_memory=False)
            
            # Basic cleanup
            df['Total Sales'] = pd.to_numeric(df['Total Sales'], errors='coerce').fillna(0)
            df['Date'] = pd.to_datetime(df['Created On'], errors='coerce')
            
            if df['Date'].dropna().empty:
                print(f"  Warning: No valid dates in {f}")
                continue
                
            start_date = df['Date'].min()
            end_date = df['Date'].max()
            total_sales = df['Total Sales'].sum()
            
            # Top products by sales volume
            top_products = df.groupby('Product Desc')['Total Sales'].sum().sort_values(ascending=False).head(5).to_dict()
            
            weekly_stats.append({
                'file': f,
                'start_date': str(start_date.date()),
                'end_date': str(end_date.date()),
                'total_sales': float(total_sales),
                'top_products': top_products,
                'transaction_count': len(df)
            })
            
        except Exception as e:
            print(f"  Error processing {f}: {e}")

    # Output results
    with open('weekly_trend_analysis.json', 'w') as f:
        json.dump(weekly_stats, f, indent=2)
        
    print("\nAnalysis Complete. Summary:")
    for w in weekly_stats:
        print(f"Week ({w['start_date']} to {w['end_date']}): ${w['total_sales']:.2f} Sales")

if __name__ == "__main__":
    analyze_trends()
