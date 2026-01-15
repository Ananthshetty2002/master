import json
import os
import re
import csv
import glob

def build_product_mapping():
    mapping = {}
    work_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    # Mapping sources
    folders = [work_dir, os.path.join(work_dir, 'DEC 8-19'), os.path.join(work_dir, 'DEC 9-22'), os.path.join(work_dir, 'venv', 'DEC 23-31')]
    id_pattern = re.compile(r'^(AVR|PC)\d+$', re.IGNORECASE)
    
    all_csvs = []
    for f in folders:
        if os.path.exists(f):
            all_csvs.extend(glob.glob(os.path.join(f, "*.csv")))

    for csv_file in all_csvs:
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.reader(f)
                filename = os.path.basename(csv_file).lower()
                for row in reader:
                    if len(row) > 2:
                        # Logic to find ID and Name in row
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

def build_location_mapping():
    loc_map = {}
    refined_csv = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage\shrinkage_report_refined.csv"
    if not os.path.exists(refined_csv): return {}
    with open(refined_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            loc = row.get('Location')
            p_id = row.get('Product ID')
            if loc and p_id and loc != 'Stock':
                if p_id not in loc_map: loc_map[p_id] = loc
    return loc_map

def final_aggressive_cleanup():
    work_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    json_path = os.path.join(work_dir, "n8n_consolidated_report_final_fixed.json")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    p_mapping = build_product_mapping()
    l_mapping = build_location_mapping()
    DEFAULT_SITE = "FFI - Moorpark"
    id_pattern = re.compile(r'^(AVR|PC)\d+$', re.IGNORECASE)

    def process_node(obj):
        if isinstance(obj, dict):
            new_obj = {}
            # Standardize keys to lowercase snake_case
            for k, v in obj.items():
                nk = k.lower().replace(' ', '_')
                new_obj[nk] = v
            
            # Key Mapping / Aliases
            if 'site' in new_obj and 'location' not in new_obj:
                new_obj['location'] = new_obj.pop('site')
            if 'micromarket' in new_obj and 'location' not in new_obj:
                new_obj['location'] = new_obj.pop('micromarket')
            if 'product' in new_obj and 'product_name' not in new_obj and not id_pattern.match(str(new_obj['product'])):
                new_obj['product_name'] = new_obj.pop('product')
            if 'product' in new_obj and 'product_id' not in new_obj and id_pattern.match(str(new_obj['product'])):
                new_obj['product_id'] = new_obj.pop('product')

            # Fix "Stock" Location
            loc = str(new_obj.get('location', '')).strip()
            p_id = str(new_obj.get('product_id', '')).strip()
            
            if loc.lower() == 'stock' or not loc or loc == 'None':
                if p_id in l_mapping:
                    new_obj['location'] = l_mapping[p_id]
                elif p_id:
                    new_obj['location'] = DEFAULT_SITE
            
            # Enrich Product Name
            if p_id:
                p_name = new_obj.get('product_name')
                if not p_name or p_name == p_id or id_pattern.match(str(p_name)):
                    if p_id in p_mapping:
                        new_obj['product_name'] = p_mapping[p_id]

            return {k: process_node(v) for k, v in new_obj.items()}
        elif isinstance(obj, list):
            return [process_node(i) for i in obj]
        return obj

    print("Running final aggressive cleanup...")
    clean_data = process_node(data)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, indent=4)
    print("Done. Report is fully standardized.")

if __name__ == "__main__":
    final_aggressive_cleanup()
