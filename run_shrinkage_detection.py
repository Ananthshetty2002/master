import pandas as pd
import argparse
import sys
import os
from shrinkage_detector import ShrinkageDetector

def generate_mock_data():
    """
    Generates dummy data for testing the logic:
    Start(100) - End(90) - Sales(8) = Shrinkage(2).
    """
    # Inventory Start (T1)
    inv_start = pd.DataFrame({
        'Location': ['LocA', 'LocB', 'LocC'],
        'Product ID': ['Prod1', 'Prod1', 'Prod2'],
        'Quantity': [100, 50, 10]
    })
    
    # Inventory End (T2)
    inv_end = pd.DataFrame({
        'Location': ['LocA', 'LocB', 'LocC'],
        'Product ID': ['Prod1', 'Prod1', 'Prod2'],
        'Quantity': [90, 40, 5]
    })
    
    # Sales Data (Aggregated T1-T2)
    sales = pd.DataFrame({
        'Location': ['LocA', 'LocB', 'LocC'],
        'Product ID': ['Prod1', 'Prod1', 'Prod2'],
        'Quantity': [8, 10, 0],
        'Value': [16.0, 20.0, 0.0] # Implied price $2
    })
    
    print("--- Mock Data Generated ---")
    return inv_start, inv_end, sales

def load_data_from_csvs(start_path, end_path, sales_path, adjustments_path=None):
    print(f"Loading data from CSVs:\n  Start: {start_path}\n  End:   {end_path}\n  Sales: {sales_path}")
    if adjustments_path:
        print(f"  Adjustments: {adjustments_path}")
    
    try:
        start_df = pd.read_csv(start_path)
        end_df = pd.read_csv(end_path)
        sales_df = pd.read_csv(sales_path)
        
        adjustments_df = None
        if adjustments_path:
             adjustments_df = pd.read_csv(adjustments_path)
             # Normalize columns to match Detector expectation (Location, Product ID)
             # Mappings based on Overage Report inspection
             rename_map = {
                 'Micromarket': 'Location',
                 'Site': 'Location', 
                 'Product Code': 'Product ID',
                 'Product_Code': 'Product ID'
             }
             adjustments_df.rename(columns=rename_map, inplace=True)
             
             # Filter for valid change types if column exists (optional but good practice based on other scripts)
             if 'Change Type' in adjustments_df.columns:
                 valid_types = ['Spoilage', 'Shrinkage', 'Quantity Adjustment']
                 adjustments_df = adjustments_df[adjustments_df['Change Type'].isin(valid_types)]
             
             print(f"  Adjustments loaded: {len(adjustments_df)} rows")
        
        # Basic normalization (User should ensure these exist or we add mapping logic here)
        # For now, we assume standard headers or fail gracefully
        required_cols = ['Location', 'Product ID', 'Quantity']
        
        for df, name in [(start_df, 'Start'), (end_df, 'End')]:
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                print(f"Error: {name} CSV missing columns: {missing}")
                sys.exit(1)
                
        sales_req = ['Location', 'Product ID', 'Quantity', 'Value']
        missing_sales = [c for c in sales_req if c not in sales_df.columns]
        if missing_sales:
             print(f"Error: Sales CSV missing columns: {missing_sales}")
             sys.exit(1)
             
        return start_df, end_df, sales_df, adjustments_df
    except Exception as e:
        print(f"Failed to load CSVs: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Shrinkage Detector Wrapper")
    parser.add_argument('--start', help="Path to Inventory Start CSV")
    parser.add_argument('--end', help="Path to Inventory End CSV")
    parser.add_argument('--sales', help="Path to Sales CSV")
    parser.add_argument('--adjustments', help="Path to Known Adjustments (Overage) CSV")
    args = parser.parse_args()
    
    adjustments_df = None
    
    if args.start and args.end and args.sales:
        print("Initializing Shrinkage Detector with Real Data...")
        start_df, end_df, sales_df, adjustments_df = load_data_from_csvs(args.start, args.end, args.sales, args.adjustments)
    else:
        print("No CSV inputs provided. Using Mock Data Mode.")
        start_df, end_df, sales_df = generate_mock_data()
    
    # 2. Instantiate Agent
    detector = ShrinkageDetector(start_df, end_df, sales_df, adjustments_df)
    
    # 3. Running Detection
    print("\n--- Running Detection ---")
    detector.detect()
    
    # 4. Ranking
    ranked_report = detector.rank_by_severity()
    
    print("\n--- Shrinkage Report (Ranked) ---")
    cols_to_show = ['Location', 'Product ID', 'Quantity_Start', 'Quantity_End', 
                    'Total_Depletion', 'Sales_Quantity', 'Shrinkage_Qty', 'Shrinkage_Value']
    
    # Only show columns if they exist (safe check)
    actual_cols = [c for c in cols_to_show if c in ranked_report.columns]
    print(ranked_report[actual_cols].to_string(index=False))
    
    # 5. Validation Check (Only run on Mock Data for now)
    if not args.start:
        row_a = ranked_report[(ranked_report['Location'] == 'LocA') & (ranked_report['Product ID'] == 'Prod1')]
        if not row_a.empty:
            shrink_a = row_a.iloc[0]['Shrinkage_Qty']
            print(f"\nVerification LocA: Expected 2, Got {shrink_a}")
            if shrink_a == 2:
                print("✅ SUCCESS: LocA calculation correct.")
            else:
                print("❌ FAILURE: LocA calculation incorrect.")
        
    # Save to CSV
    output_path = 'shrinkage_report.csv'
    ranked_report.to_csv(output_path, index=False)
    print(f"\nFull report saved to {output_path}")

if __name__ == "__main__":
    main()
