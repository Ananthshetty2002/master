import pandas as pd

def find_overlap():
    print("--- Finding Overlap ---")
    try:
        start_df = pd.read_csv('start.csv')
        trans_df = pd.read_csv('transactionlistweek2.csv', low_memory=False)
        
        inventory_products = set(start_df['Product ID'].unique())
        print(f"Total Unique Products in Inventory: {len(inventory_products)}")
        
        results = []
        for market in trans_df['Micro Market'].unique():
            if pd.isna(market): continue
            market_products = set(trans_df[trans_df['Micro Market'] == market]['Product Code'].unique())
            overlap = inventory_products.intersection(market_products)
            results.append({
                'Micro Market': market,
                'Overlap Count': len(overlap),
                'Market Unique Products': len(market_products)
            })
            
        results_df = pd.DataFrame(results).sort_values(by='Overlap Count', ascending=False)
        print("\nTop Overlapping Micro Markets:")
        print(results_df.head(20).to_string(index=False))
        
        # Save to file
        results_df.to_csv('overlap_results.csv', index=False)
        
    except Exception as e:
        print(f"Error: {e}")

find_overlap()
