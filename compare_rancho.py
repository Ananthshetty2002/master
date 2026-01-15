import pandas as pd
import json

def compare_sources():
    loc = 'HIE - Rancho Cucamonga Market'
    
    # Load JSON
    with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    json_prods = []
    for lp in data.get('location_ranking', []):
        if lp['location'] == loc:
            json_prods = lp['shrinkage_products']
            break
            
    # Load CSVs
    df1 = pd.read_csv('shrinkage_report.csv')
    df1.columns = [c.strip() for c in df1.columns]
    
    df2 = pd.read_csv('shrinkage_by_site_product_v2.csv')
    df2.columns = [c.strip() for c in df2.columns]
    
    r1 = df1[df1['Location'] == loc].copy()
    r2 = df2[df2['location'] == loc].copy()
    
    print("JSON Rancho Samples (first 5):")
    for p in json_prods[:5]:
        print(f"  PID: {p['product_id']}, Sales: {p.get('sales_units')}, Qty: {p.get('shrinkage_qty')}")
        
    print("\nCSV1 (shrinkage_report.csv) Rancho Samples (first 5):")
    # Mapping columns
    r1_cols = {'Product ID': 'pid', 'Sales_Quantity': 'sales', 'Shrinkage_Qty': 'qty'}
    sub1 = r1[list(r1_cols.keys())].head(5)
    print(sub1)
    
    print("\nCSV2 (shrinkage_by_site_product_v2.csv) Rancho Samples (first 5):")
    r2_cols = {'product_id': 'pid', 'sales_units': 'sales', 'shrinkage_qty': 'qty'}
    sub2 = r2[list(r2_cols.keys())].head(5)
    print(sub2)

if __name__ == "__main__":
    compare_sources()
