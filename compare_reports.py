import pandas as pd

# Load new report
new_report = pd.read_csv('shrinkage_by_site_product.csv')
print("--- New Report Top 5 ---")
print(new_report[['product_id', 'product_name', 'shrinkage_qty']].head(5))

# Load old report (if it exists and has expected columns)
old_report_path = 'shrinkage_analysis_output.csv'
try:
    old_report = pd.read_csv(old_report_path)
    # Aggregate old report by product to compare with 'Stock' (which is aggregated)
    old_agg = old_report.groupby('Product Code').agg({
        'Shrink_Qty_Approx': 'sum'
    }).reset_index().sort_values(by='Shrink_Qty_Approx', ascending=False)
    
    print("\n--- Previous Report (Aggregated) Top 5 ---")
    print(old_agg.head(5))
except Exception as e:
    print(f"\nCould not analyze {old_report_path}: {e}")
