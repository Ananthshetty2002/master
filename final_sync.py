import csv
import json
import os
import re

def get_best_mapping():
    mapping = {}
    work_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    
    # 1. Product Rank Report (confirmed format: Rank, Name, Code)
    rank_file = os.path.join(work_dir, "Product Rank Report (1).csv")
    if os.path.exists(rank_file):
        with open(rank_file, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > 2:
                    name = row[1].strip()
                    code = row[2].strip()
                    if code and name and not re.match(r'^(AVR|PC)\d+$', name):
                        mapping[code] = name

    # 2. Transaction Reports (confirmed format: Customer, Code, Name, ...)
    trans_files = ["Product Transaction Report (2).csv", "Product Transaction Report (3).csv"]
    for tf in trans_files:
        path = os.path.join(work_dir, tf)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) > 2:
                        code = row[1].strip()
                        name = row[2].strip()
                        if code and name and not re.match(r'^(AVR|PC)\d+$', name):
                            if code not in mapping or len(name) > len(mapping[code]):
                                mapping[code] = name
    return mapping

def perform_final_sync():
    mapping = get_best_mapping()
    json_path = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage\n8n_consolidated_report_final.json"
    
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    def fix_recursive(obj):
        updated = 0
        if isinstance(obj, dict):
            # Check if this dict is a product
            p_id = obj.get("product_id")
            p_name = obj.get("product_name")
            if p_id and p_name is not None:
                p_id = str(p_id).strip()
                p_name = str(p_name).strip()
                # If name is currenty just a code or matches ID
                if not p_name or p_name == p_id or re.match(r'^(AVR|PC)\d+$', p_name):
                    if p_id in mapping:
                        obj["product_name"] = mapping[p_id]
                        updated = 1
                    elif p_name in mapping:
                        obj["product_name"] = mapping[p_name]
                        updated = 1
            
            # Recurse
            for v in obj.values():
                updated += fix_recursive(v)
        elif isinstance(obj, list):
            for item in obj:
                updated += fix_recursive(item)
        return updated

    total_updated = fix_recursive(data)
    print(f"Final sync: Updated {total_updated} instances.")
    
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    perform_final_sync()
