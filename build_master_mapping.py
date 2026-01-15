import pandas as pd
import glob
import os
import json

def clean_id(val):
    return str(val).strip().split('.')[0]

def build_mapping():
    mapping = {}
    
    # 1. Try Rank Reports
    rank_files = [
        'ProductRankReportCSV.csv',
        'venv/DEC 23-31/Product Rank Report (1).csv'
    ]
    for f in rank_files:
        if not os.path.exists(f): continue
        print(f"Loading {f}...")
        try:
            # Try to find header by searching for 'Rank'
            df = pd.read_csv(f, low_memory=False, header=None)
            header_row = -1
            for i in range(min(20, len(df))):
                row_vals = [str(x).lower() for x in df.iloc[i].values]
                if 'rank' in row_vals and 'item description' in row_vals:
                    header_row = i
                    break
            
            if header_row != -1:
                df = pd.read_csv(f, skiprows=header_row)
                for _, row in df.iterrows():
                    rid = clean_id(row['Rank'])
                    name = str(row['Item Description']).strip()
                    if rid.isdigit() and name != 'nan' and name != '':
                        mapping[rid] = name
            else:
                # Try simple read if header search fails
                df = pd.read_csv(f)
                if 'Rank' in df.columns and 'Item Description' in df.columns:
                     for _, row in df.iterrows():
                        rid = clean_id(row['Rank'])
                        name = str(row['Item Description']).strip()
                        if rid.isdigit() and name != 'nan' and name != '':
                            mapping[rid] = name
        except Exception as e:
            print(f"  Error loading {f}: {e}")

    # 2. Try Sales Reports
    sales_files = glob.glob('*Sales By Products Report*.csv') + glob.glob('DEC 8-19/*Sales By Products Report*.csv')
    for f in sales_files:
        if not os.path.exists(f): continue
        print(f"Loading {f}...")
        try:
            df = pd.read_csv(f, low_memory=False)
            # Look for Product and Product Name
            if 'Product' in df.columns and 'Product Name' in df.columns:
                for _, row in df.iterrows():
                    pid = clean_id(row['Product'])
                    name = str(row['Product Name']).strip()
                    if pid.isdigit() and name != 'nan' and name != '':
                        mapping[pid] = name
        except Exception as e:
            print(f"  Error loading {f}: {e}")

    # 3. Try Shrinkage Report Refined
    if os.path.exists('shrinkage_report_refined.csv'):
        print("Loading shrinkage_report_refined.csv...")
        try:
            df = pd.read_csv('shrinkage_report_refined.csv')
            if 'Product' in df.columns and 'Product_Name' in df.columns:
                for _, row in df.iterrows():
                    pid = clean_id(row['Product'])
                    name = str(row['Product_Name']).strip()
                    if pid.isdigit() and name != 'nan' and name != '':
                        mapping[pid] = name
        except Exception as e:
            print(f"  Error loading shrinkage_report_refined.csv: {e}")

    return mapping

if __name__ == "__main__":
    master_map = build_mapping()
    print(f"Final mapping size: {len(master_map)}")
    
    # Save to JSON for separate_inventory_dates.py to use
    with open('master_product_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(master_map, f, indent=2)
    
    # Check the user's missing IDs
    missing = ['126', '94', '200', '930', '186', '306', '192', '300', '90', '98', '96', '84', '138', '360', '147', '112', '288', '416', '157', '194', '230']
    print("\nVerification for user's IDs:")
    for m in missing:
        print(f"  ID {m}: {master_map.get(m, '!!! STILL MISSING !!!')}")
