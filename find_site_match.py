import pandas as pd

def find_site_match():
    try:
        start_df = pd.read_csv('start.csv')
        end_df = pd.read_csv('end.csv')
        trans_df = pd.read_csv('transactionlistweek2.csv', low_memory=False)
        
        # Target products and their Stock depletion
        targets = []
        for p in ['PC00885', 'PC10765', 'PC16463']:
            s = start_df[start_df['Product ID'] == p]['Quantity'].sum()
            e = end_df[end_df['Product ID'] == p]['Quantity'].sum()
            targets.append({'id': p, 'depletion': s - e})
        
        print("Stock Depletion Targets:")
        for t in targets:
            print(f"  {t['id']}: {t['depletion']}")
            
        # Group sales by site and product
        sales_site = trans_df.groupby(['Micro Market', 'Product Code'])['Quantity'].sum().reset_index()
        
        # For each site, check how many products match the depletion exactly
        sites = trans_df['Micro Market'].unique()
        matches = []
        for site in sites:
            site_data = sales_site[sales_site['Micro Market'] == site]
            match_count = 0
            for t in targets:
                sale_qty = site_data[site_data['Product Code'] == t['id']]['Quantity'].sum()
                if sale_qty == t['depletion'] and t['depletion'] > 0:
                    match_count += 1
            if match_count > 0:
                matches.append({'site': site, 'count': match_count})
        
        print("\nSites with at least one exact depletion match:")
        for m in sorted(matches, key=lambda x: x['count'], reverse=True):
            print(f"  {m['site']}: {m['count']} matches")

    except Exception as e:
        print(f"Error: {e}")

find_site_match()
