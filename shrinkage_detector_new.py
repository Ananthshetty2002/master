import pandas as pd
import os
import json

print("Starting December Shrinkage Analysis...")

# Load sales from transaction logs (header is at row 9)
sales_files = [
    'Transaction List Report 12.23.2025 11-28 AM.csv',
    'Transaction List Report 12.23.2025 11-36 AM.csv'
]

all_sales = []
for f in sales_files:
    df = pd.read_csv(f, skiprows=9, encoding='utf-8-sig', low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        'Created On': 'trans_date',
        'Micro Market': 'location',
        'Product Code': 'product_id',
        'Product Desc': 'product_name',
        'Quantity': 'sales_units',
        'Sales': 'sales_value'
    })
    all_sales.append(df)
    print(f"Loaded {len(df)} rows from {f}")

df_sales = pd.concat(all_sales).drop_duplicates()

# Filter to December
df_sales['trans_date'] = pd.to_datetime(df_sales['trans_date'], errors='coerce')
df_sales = df_sales[(df_sales['trans_date'] >= '2025-12-03') & (df_sales['trans_date'] <= '2025-12-31')]
df_sales['sales_units'] = pd.to_numeric(df_sales['sales_units'], errors='coerce').fillna(0)
df_sales['sales_value'] = pd.to_numeric(df_sales['sales_value'], errors='coerce').fillna(0)

# Create product name to ID mapping
name_to_id = df_sales.dropna(subset=['product_id', 'product_name']).groupby('product_name')['product_id'].first().to_dict()

sales_agg = df_sales.groupby(['location', 'product_id']).agg({
    'sales_units': 'sum',
    'sales_value': 'sum',
    'product_name': 'first'
}).reset_index()

print(f"Sales aggregated: {len(sales_agg)} unique location/product pairs")

# Load start inventory (has Product column)
df_start = pd.read_csv('CSVStock Analysis Report.csv', skiprows=8, encoding='utf-8-sig', low_memory=False)
df_start.columns = [c.strip() for c in df_start.columns]
df_start = df_start.rename(columns={'Customer/Location': 'location', 'Product': 'product_name', 'Total Quantity': 'qty'})
if 'product_name' in df_start.columns:
    df_start['product_id'] = df_start['product_name'].map(name_to_id).fillna(df_start['product_name'])
else:
    df_start['product_id'] = 'UNKNOWN'

# Load end inventory (different structure - no Product column, only Category)
# Since we can't match products, we'll aggregate by location only
df_end = pd.read_csv('new_dec_stock_analysis.csv', skiprows=8, encoding='utf-8-sig', low_memory=False)
df_end.columns = [c.strip() for c in df_end.columns]
df_end = df_end.rename(columns={'Customer/Location': 'location', 'Category': 'product_name', 'Total Quantity': 'qty'})
if 'product_name' in df_end.columns:
    df_end['product_id'] = df_end['product_name'].map(name_to_id).fillna(df_end['product_name'])
else:
    df_end['product_id'] = 'UNKNOWN'

# Merge all data
keys = pd.concat([sales_agg[['location', 'product_id']], df_start[['location', 'product_id']], df_end[['location', 'product_id']]]).drop_duplicates()

merged = keys.copy()
merged = pd.merge(merged, sales_agg, on=['location', 'product_id'], how='left')
merged = pd.merge(merged, df_start[['location', 'product_id', 'qty']], on=['location', 'product_id'], how='left').rename(columns={'qty': 'start_qty'})
merged = pd.merge(merged, df_end[['location', 'product_id', 'qty']], on=['location', 'product_id'], how='left').rename(columns={'qty': 'end_qty'})

for col in ['sales_units', 'sales_value', 'start_qty', 'end_qty']:
    merged[col] = pd.to_numeric(merged[col], errors='coerce').fillna(0)

# Calculate shrinkage
merged['unit_price'] = merged.apply(lambda x: x['sales_value'] / x['sales_units'] if x['sales_units'] > 0 else 0, axis=1)
merged['expected_qty'] = merged['start_qty'] - merged['sales_units']
merged['shrinkage_qty'] = (merged['expected_qty'] - merged['end_qty']).clip(lower=0)
merged['shrinkage_value'] = merged['shrinkage_qty'] * merged['unit_price']
merged['product_name'] = merged['product_name'].fillna(merged['product_id'])

# Build JSON report
site_summary = merged.groupby('location').agg({
    'shrinkage_qty': 'sum',
    'shrinkage_value': 'sum',
    'sales_units': 'sum',
    'start_qty': 'sum',
    'end_qty': 'sum'
}).reset_index().sort_values('shrinkage_value', ascending=False)

location_ranking = []
for _, row in site_summary.iterrows():
    loc = row['location']
    prods = merged[merged['location'] == loc].copy()
    prods = prods[(prods['shrinkage_qty'] > 0) | (prods['sales_units'] > 0)].sort_values('shrinkage_value', ascending=False)
    
    if prods.empty:
        continue
    
    products_json = []
    for _, p in prods.iterrows():
        products_json.append({
            "product_name": str(p['product_name']),
            "product_id": str(p['product_id']),
            "shrinkage_qty": float(p['shrinkage_qty']),
            "shrinkage_value": round(float(p['shrinkage_value']), 2),
            "sales_units": float(p['sales_units'])
        })
    
    location_ranking.append({
        "location": str(loc),
        "total_shrinkage_qty": float(row['shrinkage_qty']),
        "sales_units": float(row['sales_units']),
        "start_qty": float(row['start_qty']),
        "end_qty": float(row['end_qty']),
        "shrinkage_products": products_json,
        "total_shrinkage_value": round(float(row['shrinkage_value']), 2)
    })

final_report = {
    "report_period": {
        "start_date": "2025-12-03 00:00:01",
        "end_date": "2025-12-31 23:59:59"
    },
    "engine_context": "You are a Loss Prevention Analyst Agent.",
    "location_ranking": location_ranking
}

with open('n8n_consolidated_report1.json', 'w', encoding='utf-8') as f:
    json.dump(final_report, f, indent=4)

print(f"\nSUCCESS! Generated report with {len(location_ranking)} locations")
print(f"File size: {os.path.getsize('n8n_consolidated_report1.json')} bytes")
print(f"Report saved to: {os.path.abspath('n8n_consolidated_report1.json')}")
