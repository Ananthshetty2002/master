import pandas as pd
import glob
import os
import json

def clean_id(val):
    if pd.isna(val): return ""
    v = str(val).strip().split('.')[0]
    return v if v.lower() != 'nan' else ""

def build_mapping():
    mapping = {}
    
    # Files to check
    sources = [
        {'path': 'ProductRankReportCSV.csv', 'id_col': 'Rank', 'name_col': 'Item Description', 'skip': 0},
        {'path': 'venv/DEC 23-31/Product Rank Report (1).csv', 'id_col': 'Rank', 'name_col': 'Item Description', 'skip': 0},
        {'path': 'Sales By Products Report (1) (1).csv', 'id_col': 'Product', 'name_col': 'Product Name', 'skip': 5},
        {'path': 'Sales By Products Report (2) (1).csv', 'id_col': 'Product', 'name_col': 'Product Name', 'skip': 5},
        {'path': 'Sales By Products Report (3) (1).csv', 'id_col': 'Product', 'name_col': 'Product Name', 'skip': 5},
        {'path': 'DEC 8-19/Sales By Products Report (4) (1).csv', 'id_col': 'Product', 'name_col': 'Product Name', 'skip': 5},
        {'path': 'shrinkage_report_refined.csv', 'id_col': 'Product', 'name_col': 'Product_Name', 'skip': 0}
    ]

    for src in sources:
        p = src['path']
        if not os.path.exists(p): 
            print(f"Skipping {p}: Not found.")
            continue
        
        print(f"Processing {p}...")
        try:
            # Check for generic Rank header first if skip is 0
            skip = src['skip']
            df = pd.read_csv(p, low_memory=False, skiprows=skip)
            
            # If id_col not found, search for it
            id_col = src['id_col']
            name_col = src['name_col']
            
            if id_col not in df.columns or name_col not in df.columns:
                # Search for headers in first 20 rows
                df_raw = pd.read_csv(p, header=None, low_memory=False, nrows=20)
                found = False
                for i in range(len(df_raw)):
                    row = [str(x).lower() for x in df_raw.iloc[i].values]
                    if any(id_col.lower() in r for r in row) and any(name_col.lower() in r for r in row):
                        df = pd.read_csv(p, skiprows=i+1)
                        # Re-verify columns
                        potential_id = [c for c in df.columns if id_col.lower() in c.lower()]
                        potential_name = [c for c in df.columns if name_col.lower() in c.lower()]
                        if potential_id and potential_name:
                            id_col = potential_id[0]
                            name_col = potential_name[0]
                            found = True
                            break
                if not found:
                    print(f"  Warning: Could not find columns {id_col} and {name_col} in {p}")
                    continue

            for _, row in df.iterrows():
                rid = clean_id(row[id_col])
                name = str(row[name_col]).strip()
                if rid.isdigit() and name != 'nan' and name != '':
                    if rid not in mapping or len(name) > len(mapping[rid]):
                        mapping[rid] = name
        except Exception as e:
            print(f"  Error processing {p}: {e}")

    return mapping

if __name__ == "__main__":
    master_map = build_mapping()
    print(f"Final mapping size: {len(master_map)}")
    
    with open('master_product_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(master_map, f, indent=2)
    
    # Verify the specific IDs from user
    ids_to_check = ['126', '94', '200', '930', '186', '306', '192', '300', '90', '98', '96', '84', '138', '360', '147', '112', '288', '416', '157', '194', '230']
    print("\nCheck results for User IDs:")
    for i in ids_to_check:
        print(f"  {i}: {master_map.get(i, 'NOT FOUND')}")
