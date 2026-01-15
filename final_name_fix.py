import csv
import json
import glob
import os
import re

def get_mappings():
    mapping = {}
    
    # Directory to scan
    work_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    
    # All CSVs in the directory
    files = glob.glob(os.path.join(work_dir, "*.csv"))
    
    print(f"Found {len(files)} CSV files in {work_dir}")

    potential_code_headers = ["Product Code", "Code", "Item Code", "SKU", "product_id"]
    potential_name_headers = ["Product", "Product Name", "Description", "Item Name", "product_name"]

    for file_path in files:
        file_name = os.path.basename(file_path)
        # Skip output files we might have created
        if file_name in ["shrinkage_by_site_product.csv", "shrinkage_by_site_summary.csv", "final_shrinkage_report.csv"]:
            continue
            
        print(f"Scanning {file_name}...")
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.reader(f)
                header_row_idx = -1
                code_col = -1
                name_col = -1
                
                # First pass: find header
                rows = []
                for i, row in enumerate(reader):
                    if i > 100: break # Only check first 100 rows for header
                    rows.append(row)
                    row_clean = [col.strip() for col in row]
                    
                    c_idx = -1
                    for ph in potential_code_headers:
                        if ph in row_clean:
                            c_idx = row_clean.index(ph)
                            break
                    
                    n_idx = -1
                    for ph in potential_name_headers:
                        if ph in row_clean:
                            n_idx = row_clean.index(ph)
                            break
                            
                    if c_idx != -1 and n_idx != -1 and c_idx != n_idx:
                        code_col = c_idx
                        name_col = n_idx
                        header_row_idx = i
                        print(f"  Header found at row {i}: Code Col={c_idx}, Name Col={n_idx}")
                        break
                
                if header_row_idx != -1:
                    # Second pass: read all data
                    f.seek(0)
                    # Skip to header row
                    for _ in range(header_row_idx + 1):
                        next(reader)
                        
                    count = 0
                    for row in reader:
                        if len(row) > max(code_col, name_col):
                            code = row[code_col].strip()
                            name = row[name_col].strip()
                            
                            if not code or not name: continue
                            if code == name: continue
                            
                            # Filter out IDs as names
                            if not re.match(r'^(AVR|PC)\d+$', name):
                                if code not in mapping or len(name) > len(mapping[code]):
                                    mapping[code] = name
                                    count += 1
                    print(f"  Extracted {count} candidate mappings.")
        except Exception as e:
            print(f"  Error reading {file_name}: {e}")
            
    return mapping

def update_report(mapping):
    json_path = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage\n8n_consolidated_report_final.json"
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    stats = {"updated": 0, "total": 0}
    
    def fix_prod(prod):
        stats["total"] += 1
        p_id = prod.get("product_id")
        p_name = prod.get("product_name", "").strip()
        
        # Determine if it needs fixing (missing or generic ID)
        is_generic = (
            not p_name or 
            p_name == p_id or 
            re.match(r'^(AVR|PC)\d+$', p_name)
        )
        
        if is_generic and p_id and p_id in mapping:
            prod["product_name"] = mapping[p_id]
            stats["updated"] += 1

    # Traverse JSON
    if "location_ranking" in data:
        for loc in data["location_ranking"]:
            for p in loc.get("shrinkage_products", []): fix_prod(p)
            opts = loc.get("transfer_opportunities", {})
            for p in opts.get("outbound_suggestions", []): fix_prod(p)
            for p in opts.get("inbound_opportunities", []): fix_prod(p)
            
    if "network_transfer_optimization" in data:
        for p in data["network_transfer_optimization"].get("top_recommendations", []):
            fix_prod(p)
            
    print(f"Update summary: examined {stats['total']} entries, updated {stats['updated']} with names.")
    
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)
    print("Report saved successfully.")

if __name__ == "__main__":
    mappings = get_mappings()
    print(f"Final mapping size: {len(mappings)} products.")
    update_report(mappings)
