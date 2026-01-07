import pandas as pd
import os
import glob
import sys
import json
from datetime import datetime

# ==========================================
# --- CONFIGURATION (Dec 3 to Dec 23) ---
# ==========================================
REPORT_START_DATE = '2025-12-03'
REPORT_END_DATE   = '2025-12-23'

# --- INPUT FILE PATHS ---
START_INVENTORY_FILE = 'CSVStock Analysis Report.csv'
END_INVENTORY_FILE   = 'Stock Analysis Report.csv'
ADJUSTMENTS_FILE     = 'pilot_shrink_log.csv'

# Glob patterns to find transaction logs
TRANSACTION_LOGS_PATTERNS = [
    'Transaction List Report*.csv',
    'transaction list week*.csv', 
    'transactionlist week*.csv',
    'transactionlistweek*.csv',
    'transaction week*.csv'
]

# --- OUTPUT FILE PATHS ---
DETAILED_REPORT_FILE = 'shrinkage_by_site_product_v2.csv'
SUMMARY_REPORT_FILE  = 'shrinkage_by_site_summary_v2.csv'
JSON_REPORT_FILE     = 'n8n_shrinkage_report_v2.json'
# ==========================================

def load_and_standardize(file_path, rename_map, required_cols=None):
    """Loads a CSV, standardizes columns, and verifies required columns exist."""
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        return pd.DataFrame()
    
    skip_rows = 0
    try:
        # Detect row with headers dynamically
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            found = False
            for i, line in enumerate(f):
                if i > 50: break # Scan up to 50 rows
                # Check how many of our target column names are in this line
                match_count = sum(1 for col_name in rename_map.keys() if col_name in line)
                if match_count >= 2: # Found the header row
                    skip_rows = i
                    print(f"  Detected header for {os.path.basename(file_path)} at row {i+1}")
                    found = True
                    break
            if not found:
                 print(f"  Warning: Could not find header keywords in {os.path.basename(file_path)}. Using row 0.")
        
        df = pd.read_csv(file_path, low_memory=False, skiprows=skip_rows)
    except Exception as e:
        print(f"Error: Failed to read {file_path}. Details: {e}")
        return pd.DataFrame()
    
    # Cleaning column names (strip spaces and handle potential leading commas)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Flexible mapping: only rename if column exists in the file
    actual_map = {k: v for k, v in rename_map.items() if k in df.columns}
    df = df.rename(columns=actual_map)
    
    # Critical filter: Remove footer/summary rows (where location is NaN or "Total")
    if 'location' in df.columns:
        df = df[df['location'].notna()]
        df = df[~df['location'].astype(str).str.contains('Total', case=False, na=False)]
    
    if 'product_id' in df.columns:
        df = df[df['product_id'].notna()]
        df = df[~df['product_id'].astype(str).str.contains('Total', case=False, na=False)]

    # Strip whitespace from key columns
    for col in ['location', 'product_id', 'product_name']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    return df

def run_shrinkage_detection():
    print(f"--- Starting December Shrinkage Detection (Period: {REPORT_START_DATE} to {REPORT_END_DATE}) ---")
    
    # 1. Load Sales Data
    rename_map_sales = {
        'Micro Market': 'location',
        'Micromarket': 'location',
        'Product Code': 'product_id',
        'Product Desc': 'product_name',
        'Quantity': 'sales_units',
        'Created On': 'trans_date',
        'Sales': 'total_sales_value',
        'Trans.#': 'trans_id'
    }

    print("Searching for transaction logs...")
    transaction_files = []
    for pattern in TRANSACTION_LOGS_PATTERNS:
        transaction_files.extend(glob.glob(pattern))
    
    all_sales_dfs = []
    processed_files = set()
    for f in sorted(list(set(transaction_files))): # deduplicate file paths
        f_abs = os.path.abspath(f)
        if f_abs in processed_files: continue
        processed_files.add(f_abs)
        
        print(f"  Reading {f}...")
        df = load_and_standardize(f, rename_map_sales)
        if not df.empty and 'location' in df.columns and 'product_id' in df.columns:
            all_sales_dfs.append(df)
            
    if not all_sales_dfs:
        print("Warning: No valid transaction logs found.")
        df_sales_all = pd.DataFrame(columns=['location', 'product_id', 'sales_units', 'trans_date', 'trans_id', 'product_name'])
    else:
        df_sales_all = pd.concat(all_sales_dfs, ignore_index=True)
        # Deduplicate based on Transaction ID if available
        if 'trans_id' in df_sales_all.columns:
             initial_len = len(df_sales_all)
             df_sales_all = df_sales_all.drop_duplicates(subset=['location', 'product_id', 'trans_id'])
             print(f"  Deduplicated sales: {len(df_sales_all)} rows remaining (from {initial_len})")

    df_sales_all['trans_date'] = pd.to_datetime(df_sales_all['trans_date'], errors='coerce')
    df_sales_all = df_sales_all.dropna(subset=['trans_date'])
    
    start_dt = pd.to_datetime(REPORT_START_DATE)
    end_dt = pd.to_datetime(REPORT_END_DATE)
    mask = (df_sales_all['trans_date'] >= start_dt) & (df_sales_all['trans_date'] <= end_dt)
    df_sales_filtered = df_sales_all.loc[mask].copy()

    # Build Name-to-ID mapping from sales data
    name_to_id = {}
    if not df_sales_all.empty:
        mapping_df = df_sales_all.dropna(subset=['product_id', 'product_name'])
        for name, group in mapping_df.groupby('product_name'):
            name_to_id[name] = group['product_id'].mode()[0]

    sales_agg = df_sales_filtered.groupby(['location', 'product_id']).agg({
        'sales_units': 'sum',
        'product_name': 'first'
    }).reset_index()

    # 2. Load Adjustments (Pilot Shrink Log)
    print(f"Loading recorded adjustments ({ADJUSTMENTS_FILE})...")
    rename_map_adj = {
        'Micromarket': 'location',
        'Product Code': 'product_id',
        'Quantity': 'adj_qty',
        'Change Type': 't_type'
    }
    df_adj_raw = load_and_standardize(ADJUSTMENTS_FILE, rename_map_adj)
    if not df_adj_raw.empty:
        valid_types = ['Spoilage', 'Shrinkage', 'Quantity Adjustment', 'Overage']
        df_adj = df_adj_raw[df_adj_raw['t_type'].isin(valid_types)].copy()
        df_adj['adj_qty'] = pd.to_numeric(df_adj['adj_qty'], errors='coerce').fillna(0)
        df_adj['adj_val'] = df_adj.apply(lambda x: -x['adj_qty'] if x['t_type'] == 'Overage' else x['adj_qty'], axis=1)
        adj_agg = df_adj.groupby(['location', 'product_id']).agg({'adj_val': 'sum'}).reset_index().rename(columns={'adj_val': 'adj_qty'})
    else:
        adj_agg = pd.DataFrame(columns=['location', 'product_id', 'adj_qty'])

    # 3. Load Snapshots (Start/End Inventory)
    print("Loading inventory snapshots...")
    rename_map_stock = {
        'Micromarket': 'location', 
        'Product': 'product_name', 
        'Total Quantity': 'on_hand_qty'
    }
    df_start_raw = load_and_standardize(START_INVENTORY_FILE, rename_map_stock)
    df_end_raw = load_and_standardize(END_INVENTORY_FILE, rename_map_stock)

    def resolve_snapshot_ids(df):
        if df.empty: return df
        if 'product_id' not in df.columns:
            df['product_id'] = df['product_name'].map(name_to_id).fillna(df['product_name'])
        return df[['location', 'product_id', 'product_name', 'on_hand_qty']]

    df_start = resolve_snapshot_ids(df_start_raw)
    df_end = resolve_snapshot_ids(df_end_raw)

    # 4. Core Calculation Logic
    print("Consolidating data per site/product...")
    all_keys = pd.concat([
        sales_agg[['location', 'product_id']],
        adj_agg[['location', 'product_id']],
        df_start[['location', 'product_id']],
        df_end[['location', 'product_id']]
    ]).dropna(subset=['location', 'product_id']).drop_duplicates()

    merged = pd.merge(all_keys, sales_agg, on=['location', 'product_id'], how='left')
    merged = pd.merge(merged, adj_agg, on=['location', 'product_id'], how='left')
    merged = pd.merge(merged, df_start.drop(columns=['product_name']), on=['location', 'product_id'], how='left').rename(columns={'on_hand_qty': 'start_qty'})
    merged = pd.merge(merged, df_end.drop(columns=['product_name']), on=['location', 'product_id'], how='left').rename(columns={'on_hand_qty': 'end_qty'})

    for col in ['sales_units', 'adj_qty', 'start_qty', 'end_qty']:
        merged[col] = pd.to_numeric(merged[col], errors='coerce').fillna(0)

    merged['expected_qty'] = (merged['start_qty']) - merged['sales_units'] - merged['adj_qty']
    merged['shrinkage_qty'] = (merged['expected_qty'] - merged['end_qty']).clip(lower=0)

    # 5. Final Polish
    if 'product_name' in merged.columns:
        id_to_name = {v: k for k, v in name_to_id.items()}
        merged['product_name'] = merged['product_name'].fillna(merged['product_id'].map(id_to_name)).fillna(merged['product_id'])

    detailed_report = merged[merged['shrinkage_qty'] > 0].copy()
    detailed_report = detailed_report.sort_values(by='shrinkage_qty', ascending=False)

    summary_report = merged.groupby('location').agg({
        'shrinkage_qty': 'sum',
        'sales_units': 'sum',
        'start_qty': 'sum',
        'end_qty': 'sum'
    }).reset_index().rename(columns={'shrinkage_qty': 'total_shrinkage_qty'}).sort_values(by='total_shrinkage_qty', ascending=False)

    # 6. Write Outputs
    detailed_report.to_csv(DETAILED_REPORT_FILE, index=False)
    summary_report.to_csv(SUMMARY_REPORT_FILE, index=False)

    report_json = {
        "report_period": f"{REPORT_START_DATE} to {REPORT_END_DATE}",
        "analysis_notes": "Note: Incoming inventory data for December was unavailable. Shrinkage reflects the difference between snapshots and recorded sales/waste.",
        "location_ranking": summary_report.to_dict(orient='records'),
        "data": detailed_report.to_dict(orient='records')
    }
    with open(JSON_REPORT_FILE, 'w') as f:
        json.dump(report_json, f, indent=2)

    print(f"\n--- SUCCESS ---")
    print(f"Unique Sites Processed: {len(summary_report)}")
    print(f"Total Shrinkage Units Identified: {detailed_report['shrinkage_qty'].sum():,.0f}")
    if not summary_report.empty:
        top_site = summary_report.iloc[0]
        print(f"Top Risk Site: {top_site['location']} ({top_site['total_shrinkage_qty']:.0f} units)")

if __name__ == "__main__":
    run_shrinkage_detection()
