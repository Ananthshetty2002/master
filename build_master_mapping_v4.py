import pandas as pd
import os
import json

def clean_id(val):
    if pd.isna(val) or val == '': return ""
    v = str(val).strip().split('.')[0]
    return v if v.isdigit() else ""

def build_mapping():
    mapping = {}
    
    # List of all potential source files and their column mappings
    # We use a broad approach: check any file that looks like a report
    potential_files = [
        'ProductRankReportCSV.csv',
        'venv/DEC 23-31/Product Rank Report (1).csv',
        'Sales By Products Report (1) (1).csv',
        'Sales By Products Report (2) (1).csv',
        'Sales By Products Report (3) (1).csv',
        'DEC 8-19/Sales By Products Report (4) (1).csv',
        'shrinkage_report_refined.csv'
    ]

    # Column name pairs (ID column, Name column)
    id_aliases = ['rank', 'product', 'product id', 'item id']
    name_aliases = ['item description', 'product name', 'product_name', 'description']

    for f_path in potential_files:
        if not os.path.exists(f_path):
            print(f"Skipping {f_path}: Not found.")
            continue
        
        print(f"Checking {f_path}...")
        try:
            # Load with no header initially to find the real header row
            df_raw = pd.read_csv(f_path, header=None, low_memory=False, nrows=50)
            header_idx = -1
            id_col_idx = -1
            name_col_idx = -1

            for i, row in df_raw.iterrows():
                row_str = [str(x).lower() for x in row.values]
                # Find a row that contains both an ID-like and Name-like header
                found_id = -1
                found_name = -1
                for j, cell in enumerate(row_str):
                    if any(alias in cell for alias in id_aliases):
                        found_id = j
                    if any(alias in cell for alias in name_aliases):
                        found_name = j
                
                if found_id != -1 and found_name != -1:
                    header_idx = i
                    id_col_idx = found_id
                    name_col_idx = found_name
                    break
            
            if header_idx != -1:
                print(f"  Found header at row {header_idx}, ID col {id_col_idx}, Name col {name_col_idx}")
                df = pd.read_csv(f_path, skiprows=header_idx)
                # Use positional indexing since names might have spaces or weird chars
                for _, row in df.iterrows():
                    rid = clean_id(row.iloc[id_col_idx])
                    name = str(row.iloc[name_col_idx]).strip()
                    if rid and name and name.lower() != 'nan':
                        # Prefer longer names (often more descriptive)
                        if rid not in mapping or len(name) > len(mapping[rid]):
                            mapping[rid] = name
            else:
                # Fallback: try to find anything that looks like (Number, String) in first few cols
                print(f"  Could not find explicit headers in {f_path}, trying heuristic...")
                df = pd.read_csv(f_path, header=None, low_memory=False)
                for _, row in df.iterrows():
                    for j in range(len(row)-1):
                        c1 = clean_id(row.iloc[j])
                        c2 = str(row.iloc[j+1]).strip()
                        if c1 and c2 and not c2.isdigit() and len(c2) > 3 and c2.lower() != 'nan':
                            if c1 not in mapping or len(c2) > len(mapping[c1]):
                                mapping[c1] = c2
        except Exception as e:
            print(f"  Error processing {f_path}: {e}")

    return mapping

if __name__ == "__main__":
    master_map = build_mapping()
    print(f"Final mapping size: {len(master_map)}")
    
    with open('master_product_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(master_map, f, indent=2)
    
    # Verification
    test_ids = ['126', '94', '200', '930', '186', '306', '192', '300', '90', '98', '96', '84', '138', '360', '147', '112', '288', '416', '157', '194', '230']
    print("\nVerification of key IDs:")
    for tid in test_ids:
        print(f"  {tid}: {master_map.get(tid, '!!! MISSING !!!')}")
