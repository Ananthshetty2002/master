import json
import os
import re
import csv
import glob
import pandas as pd

def build_product_mapping():
    mapping = {}
    work_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    id_pattern = re.compile(r'^(AVR|PC)\d+$', re.IGNORECASE)
    csv_files = glob.glob(os.path.join(work_dir, "**", "*.csv"), recursive=True)
    for csv_file in csv_files:
        try:
            filename = os.path.basename(csv_file).lower()
            if "product rank" in filename or "product transaction" in filename or "rankreport" in filename:
                with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) > 2:
                            c1, c2 = row[1].strip(), row[2].strip()
                            if id_pattern.match(c1) and not id_pattern.match(c2):
                                code, name = c1, c2
                            elif id_pattern.match(c2) and not id_pattern.match(c1):
                                code, name = c2, c1
                            else: continue
                            if code not in mapping or len(name) > len(mapping[code]):
                                mapping[code] = name
        except: continue
    return mapping

def add_spoilage_items():
    work_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    json_path = os.path.join(work_dir, "n8n_consolidated_report_final_fixed.json")
    
    # Sources
    sources = [
        os.path.join(work_dir, "pilot_shrink_log.csv"),
        os.path.join(work_dir, "venv", "DEC 23-31", "Overage Spoilage Shrinkage ReportUltraserv Automated Services 2025-12-04.csv")
    ]
    
    if not os.path.exists(json_path):
        print("JSON report not found.")
        return

    print("Building product mapping...")
    p_mapping = build_product_mapping()
    
    all_dfs = []
    for s in sources:
        if os.path.exists(s):
            print(f"Loading {s}...")
            # We need to handle potential encoding issues or header variations
            # But based on checks, they are similar enough
            df = pd.read_csv(s)
            # Normalize column names
            df.columns = [c.strip() for c in df.columns]
            rename_map = {
                'Micromarket': 'location',
                'Product Code': 'product_id',
                'Quantity': 'quantity',
                'Total Product Cost': 'cost',
                'Total Product cost': 'cost',
                'Change Type': 'type'
            }
            # Handle case where columns might be slightly different
            df.rename(columns=rename_map, inplace=True)
            all_dfs.append(df)

    if not all_dfs:
        print("No spoilage sources found.")
        return

    full_df = pd.concat(all_dfs, ignore_index=True)
    
    # Filter for Spoilage
    spoilage_df = full_df[full_df['type'].str.contains('Spoilage', case=False, na=False)].copy()
    
    # Group by location
    spoilage_by_loc = {}
    for loc, group in spoilage_df.groupby('location'):
        items = []
        for _, row in group.iterrows():
            pid = str(row['product_id']).strip()
            qty = float(row['quantity'])
            cost = float(row['cost']) if not pd.isna(row['cost']) else 0.0
            
            items.append({
                "product_id": pid,
                "product_name": p_mapping.get(pid, pid),
                "quantity": qty,
                "unit_cost": round(cost / qty, 2) if qty != 0 else 0,
                "total_cost": round(cost, 2)
            })
        spoilage_by_loc[loc] = items

    print(f"Loaded spoilage for {len(spoilage_by_loc)} locations from merged sources.")

    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Update location_ranking
    updated_locs = 0
    for loc_entry in data.get('location_ranking', []):
        loc_name = loc_entry.get('location')
        if loc_name in spoilage_by_loc:
            loc_entry['spoilage_items'] = spoilage_by_loc[loc_name]
            updated_locs += 1
        else:
            loc_entry['spoilage_items'] = []

    print(f"Updated {updated_locs} locations in JSON with spoilage data.")

    # Save JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print("Report updated and saved.")

if __name__ == "__main__":
    add_spoilage_items()
