import pandas as pd
import json
import os

# Load Master Rank/ID Mapping
def load_master_mapping():
    mapping = {}
    try:
        if os.path.exists('master_product_mapping.json'):
            with open('master_product_mapping.json', 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            print(f"Loaded master mapping with {len(mapping)} products.")
        else:
            print("master_product_mapping.json not found. Creating one on the fly...")
            # Fallback to local rank report if master doesn't exist
            df = pd.read_csv('ProductRankReportCSV.csv')
            for _, row in df.iterrows():
                rid = str(row['Rank']).strip().split('.')[0]
                mapping[rid] = str(row['Item Description']).strip()
    except Exception as e:
        print(f"Error loading mapping: {e}")
    return mapping

MASTER_MAPPING = load_master_mapping()

def extract_period_data(path, skip, l_idx, p_idx, s_idx, e_idx):
    if not os.path.exists(path): return None
    try:
        # Read the file
        df = pd.read_csv(path, skiprows=skip, low_memory=False, header=None)
        extracted_locs = []
        extracted_prods = {}
        
        print(f"  Processing {path} (Loc:{l_idx}, Prod:{p_idx}, Start:{s_idx}, End:{e_idx})")

        current_loc = "Stock" 
        for i in range(len(df)):
            row = df.iloc[i]
            if len(row) <= max(l_idx, p_idx, s_idx, e_idx): continue
            
            loc_val = str(row.iloc[l_idx]).strip()
            prod_val = str(row.iloc[p_idx]).strip()
            
            # 1. Update current location if col 0 has a value
            if pd.notna(row.iloc[l_idx]) and loc_val != 'nan' and loc_val != '':
                if loc_val.lower() == 'customer/location': continue
                
                # If there's a product in this row, it's a data row, update current_loc
                if not (loc_val.isdigit() and len(loc_val) <= 3):
                    is_subtotal = (prod_val == loc_val)
                    if not is_subtotal:
                        current_loc = loc_val
                    else: continue

            # 2. Skip if no product name
            if pd.isna(row.iloc[p_idx]) or prod_val == 'nan' or prod_val == '' or prod_val.lower() == 'product':
                continue
                
            # 3. Resolve Product Name using Master Mapping
            display_name = prod_val
            clean_prod = prod_val.strip().split('.')[0]
            
            if clean_prod.isdigit():
                # STRICT FILTER: Only accept numeric IDs if they exist in the master mapping
                if clean_prod in MASTER_MAPPING:
                    display_name = MASTER_MAPPING[clean_prod]
                else:
                    # If it's a number but not a known Product ID, it's noise (e.g. sales total like 1498)
                    continue
            
            # 4. Skip rows that are exactly equal to the location name
            if current_loc and display_name == current_loc:
                continue
                
            loc = current_loc
            if not loc or loc.lower() == 'nan' or loc.lower() == 'customer/location': continue
            if display_name in ['0', '0.0', 'nan', '']: continue

            try:
                start = float(row.iloc[s_idx]) if pd.notna(row.iloc[s_idx]) else 0
                end = float(row.iloc[e_idx]) if pd.notna(row.iloc[e_idx]) else 0
            except:
                start = 0
                end = 0
            
            # Update product counts
            if display_name not in extracted_prods:
                extracted_prods[display_name] = {'product_name': display_name, 'start_qty': 0, 'end_qty': 0}
            extracted_prods[display_name]['start_qty'] += start
            extracted_prods[display_name]['end_qty'] += end
            
            # Update location counts
            found_loc = next((x for x in extracted_locs if x['location'] == loc), None)
            if not found_loc:
                found_loc = {'location': loc, 'start_qty': 0, 'end_qty': 0}
                extracted_locs.append(found_loc)
            found_loc['start_qty'] += start
            found_loc['end_qty'] += end
            
        return {'locations': extracted_locs, 'products': list(extracted_prods.values())}
    except Exception as e:
        print(f"Error processing {path}: {e}")
        return None

def main():
    # Load current report
    with open('december_2025_verified_report.json', 'r', encoding='utf-8') as f:
        report = json.load(f)

    # 1. Phase 1: Dec 8-19
    print("Extracting Phase 1 (Dec 8-19)...")
    phase1 = extract_period_data('DEC 8-19/CSVStock Analysis Report.csv', 8, 0, 2, 4, 6)
    
    # 2. Phase 2: Dec 23-31
    print("Extracting Phase 2 (Dec 23-31)...")
    phase2 = extract_period_data('venv/DEC 23-31/new_dec_stock_analysis.csv', 8, 0, 4, 5, 6)

    # Update Section 5
    report['section_5_multi_period_inventory'] = {
        "phase_1_dec_8_to_19": {
            "label": "PHASE 1 (Dec 8-19, 2025)",
            "source": "DEC 8-19/CSVStock Analysis Report.csv",
            "locations": phase1['locations'] if phase1 else [],
            "products": phase1['products'] if phase1 else []
        },
        "phase_2_dec_23_to_31": {
            "label": "PHASE 2 (Dec 23-31, 2025)",
            "source": "venv/DEC 23-31/new_dec_stock_analysis.csv",
            "locations": phase2['locations'] if phase2 else [],
            "products": phase2['products'] if phase2 else []
        }
    }

    # Clean JSON IDs helper
    def clean_json_ids(obj):
        if isinstance(obj, dict):
            return {k: clean_json_ids(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_json_ids(x) for x in obj]
        elif isinstance(obj, str) and obj.endswith('.0'):
            return obj[:-2]
        return obj

    report = clean_json_ids(report)

    with open('december_2025_verified_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print("Report updated with comprehensive master product name resolution.")

if __name__ == "__main__":
    main()
