import json
import pandas as pd

def audit_everything():
    json_path = 'n8n_consolidated_report_final_fixed.json'
    csv_path = 'shrinkage_report.csv'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    
    # Correct columns
    qty_col = 'Shrinkage Qty'
    sales_col = 'Quantity Sales'
    start_col = 'Quantity Start'
    end_col = 'Quantity End'
    
    results = []
    for loc_entry in data.get('location_ranking', []):
        loc_name = loc_entry.get('location')
        json_top_sales = loc_entry.get('sales_units')
        json_top_shrink = loc_entry.get('total_shrinkage_qty')
        
        # Get matching rows from CSV for this location
        csv_loc = df[df['Location'] == loc_name]
        csv_sum_sales = csv_loc[sales_col].sum()
        csv_sum_shrink = csv_loc[qty_col].sum()
        
        mismatch_sales = abs(json_top_sales - csv_sum_sales) > 0.1
        mismatch_shrink = abs(json_top_shrink - csv_sum_shrink) > 0.1
        
        if mismatch_sales or mismatch_shrink:
            results.append({
                'location': loc_name,
                'json_sales': json_top_sales,
                'csv_sales': csv_sum_sales,
                'json_shrink': json_top_shrink,
                'csv_shrink': csv_sum_shrink
            })
            
    print(f"Total locations with top-level mismatches: {len(results)}")
    if results:
        print("\nSample top-level mismatches:")
        for r in results[:10]:
            print(r)

if __name__ == "__main__":
    audit_everything()
