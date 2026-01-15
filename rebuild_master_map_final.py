import pandas as pd
import json
import os
import glob

def clean_id(val):
    if pd.isna(val): return ""
    v = str(val).strip().split('.')[0]
    return v if v.isdigit() else ""

def build_mapping():
    mapping = {}
    
    # Sources and their typical structures
    # (filepath, id_col_name, name_col_name, skip_rows)
    sources = [
        ('ProductRankReportCSV.csv', 'Rank', 'Item Description', 0),
        ('venv/DEC 23-31/Product Rank Report (1).csv', 'Rank', 'Item Description', 0),
        ('shrinkage_report_refined.csv', 'Product ID', 'Product_Name', 0),
        ('Sales By Products Report (1) (1).csv', 'Product', 'Product Name', 5),
        ('Sales By Products Report (2) (1).csv', 'Product', 'Product Name', 5),
        ('Sales By Products Report (3) (1).csv', 'Product', 'Product Name', 5),
        ('DEC 8-19/Sales By Products Report (4) (1).csv', 'Product', 'Product Name', 5)
    ]

    for f_path, id_col, name_col, skip in sources:
        if not os.path.exists(f_path):
            print(f"Skipping {f_path}: File not found.")
            continue
        
        print(f"Processing {f_path}...")
        try:
            # Try to read with the specified skip
            df = pd.read_csv(f_path, skiprows=skip, low_memory=False)
            
            # If columns not found, try to auto-detect the header row
            if id_col not in df.columns or name_col not in df.columns:
                print(f"  Columns not found with skip {skip}. Auto-detecting...")
                df_raw = pd.read_csv(f_path, header=None, low_memory=False, nrows=20)
                found = False
                for i in range(len(df_raw)):
                    row = [str(cell).strip().lower() for cell in df_raw.iloc[i]]
                    if id_col.lower() in row and name_col.lower() in row:
                        df = pd.read_csv(f_path, skiprows=i)
                        found = True
                        break
                if not found:
                    # Try fuzzy match for columns
                    cols_lower = [str(c).lower() for c in df.columns]
                    if any(id_col.lower() in c for c in cols_lower) and any(name_col.lower() in c for c in cols_lower):
                        id_col = [c for c in df.columns if id_col.lower() in str(c).lower()][0]
                        name_col = [c for c in df.columns if name_col.lower() in str(c).lower()][0]
                    else:
                        print(f"  Failed to find {id_col} or {name_col} in {f_path}")
                        continue

            for _, row in df.iterrows():
                pid = clean_id(row[id_col])
                name = str(row[name_col]).strip()
                if pid and name and name.lower() != 'nan' and not name.isdigit():
                    # Update if not present or if we find a better (longer) name
                    if pid not in mapping or len(name) > len(mapping[pid]):
                        mapping[pid] = name
        except Exception as e:
            print(f"  Error processing {f_path}: {e}")

    # Finally, check Section 4 of the verified report itself for any mappings
    if os.path.exists('december_2025_verified_report.json'):
        print("Extracting from Section 4 of current report...")
        try:
            with open('december_2025_verified_report.json', 'r', encoding='utf-8') as f:
                report = json.load(f)
            if 'section_4_detailed_shrinkage_data' in report:
                for loc in report['section_4_detailed_shrinkage_data']['per_location_analysis']:
                    for prod in loc.get('shrinkage_products', []):
                        pid = clean_id(prod.get('product_id'))
                        name = prod.get('product_name')
                        if pid and name and not name.isdigit():
                            if pid not in mapping or len(name) > len(mapping[pid]):
                                mapping[pid] = name
        except Exception as e:
            print(f"  Error extracting from report: {e}")

    return mapping

if __name__ == "__main__":
    master_map = build_mapping()
    print(f"Final mapping size: {len(master_map)}")
    
    with open('master_product_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(master_map, f, indent=2)
    
    # Check the "Numeric in Phase 2" IDs
    ids_to_check = ['126', '930', '1498', '1318', '1685', '230']
    print("\nResolution results for Phase 2 problematic IDs:")
    for mid in ids_to_check:
        print(f"  ID {mid}: {master_map.get(mid, '!!! STILL MISSING !!!')}")
