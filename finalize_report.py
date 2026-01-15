import pandas as pd
import json
import os

def main():
    # Load primary data
    df_ref = pd.read_csv('shrinkage_report_refined.csv')
    df_ref.columns = [str(c).strip() for c in df_ref.columns]

    # Load secondary periods - carefully identification by index if headers are messy
    def get_data_by_index(path, skip):
        if not os.path.exists(path): return None
        try:
            df = pd.read_csv(path, skiprows=skip)
            # Standardize columns by finding where the actual data starts
            # Column 0: Location, 1: Product, 4: Start, 6: End
            return df
        except: return None

    df_late = get_data_by_index('venv/DEC 23-31/new_dec_stock_analysis.csv', 8)
    df_nov = get_data_by_index('DEC 8-19/CSVStock Analysis Report.csv', 8)

    with open('december_2025_verified_report.json', 'r', encoding='utf-8') as f:
        report = json.load(f)

    def populate(report, key, df):
        if df is None: return
        locs = []; prods = {}
        
        # Filter out rows where both loc and prod are missing
        # We'll use iloc to be safe from column naming issues
        # Assume col 0 is Location, col 1 is Product
        for i in range(len(df)):
            row = df.iloc[i]
            loc = str(row.iloc[0]).strip()
            prod = str(row.iloc[1]).strip()
            
            if pd.isna(row.iloc[0]) or loc == 'nan' or loc == '' or pd.isna(row.iloc[1]) or prod == 'nan':
                continue
            
            # Start Qty is likely col 4, End Qty is col 6
            start = float(row.iloc[4]) if pd.notna(row.iloc[4]) else 0
            end = float(row.iloc[6]) if pd.notna(row.iloc[6]) else 0
            
            # Add to products
            if prod not in prods:
                prods[prod] = {'product_id': prod, 'start_qty': 0, 'end_qty': 0}
            prods[prod]['start_qty'] += start
            prods[prod]['end_qty'] += end
            
            # Add to locations (grouping)
            found_loc = next((x for x in locs if x['location'] == loc), None)
            if not found_loc:
                found_loc = {'location': loc, 'start_qty': 0, 'end_qty': 0, 'present_stock': 0}
                locs.append(found_loc)
            found_loc['start_qty'] += start
            found_loc['end_qty'] += end
            found_loc['present_stock'] += end

        if 'section_5_multi_period_inventory' not in report:
            report['section_5_multi_period_inventory'] = {}
        
        report['section_5_multi_period_inventory'][key] = {
            'label': key.replace('_', ' ').upper(),
            'locations': locs,
            'products': list(prods.values())
        }

    populate(report, 'late_december', df_late)
    populate(report, 'november_baseline', df_nov)

    # Primary period from Refined
    locs_p = []; prods_p = {}
    for loc in df_ref['Location'].unique():
        if pd.isna(loc): continue
        d = df_ref[df_ref['Location'] == loc]
        locs_p.append({
            'location': str(loc),
            'start_qty': float(d['Quantity_Start'].sum()),
            'end_qty': float(d['Quantity_End'].sum()),
            'present_stock': float(d['Quantity_End'].sum())
        })
    for _, row in df_ref.iterrows():
        pid = str(row['Product ID']).strip()
        if pid not in prods_p: prods_p[pid] = {'product_id': pid, 'start_qty': 0, 'end_qty': 0}
        prods_p[pid]['start_qty'] += float(row['Quantity_Start'])
        prods_p[pid]['end_qty'] += float(row['Quantity_End'])

    report['section_5_multi_period_inventory']['december_3_to_31'] = {
        'label': 'DECEMBER 3-31 2025',
        'locations': locs_p,
        'products': list(prods_p.values())
    }

    with open('december_2025_verified_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print("Multi-period inventory snapshots finalized via index indexing.")

if __name__ == "__main__":
    main()
