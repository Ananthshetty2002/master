import pandas as pd

REPORT_FILE = "shrinkage_report.csv"

def analyze():
    print("Loading Report...")
    try:
        df = pd.read_csv(REPORT_FILE)
        
        # 1. Total Shrinkage
        total_qty_lost = df['Shrinkage_Qty'].sum()
        total_val_lost = df['Shrinkage_Value'].sum()
        
        print(f"\n--- General Overview ---")
        print(f"Total Quantity Gap: {total_qty_lost}")
        
        # 2. Zero Sales High Shrinkage (Theft without purchase?)
        # Filter: Shrinkage > 10 AND Sales_Quantity == 0
        zero_sales_shrink = df[(df['Shrinkage_Qty'] > 10) & (df['Sales_Quantity'] == 0)]
        print(f"\n--- Insight: 'Ghost' Disappearances (Shrink > 10 but 0 Sales) ---")
        print(f"Count of products: {len(zero_sales_shrink)}")
        if not zero_sales_shrink.empty:
            print("Top 5 examples:")
            print(zero_sales_shrink[['Product ID', 'Shrinkage_Qty']].head(5).to_string(index=False))
            
        # 3. Negative Shrinkage (Inventory Gain / Unknown Restock)
        # Filter: Shrinkage_Qty < -5
        gains = df[df['Shrinkage_Qty'] < -5].sort_values('Shrinkage_Qty')
        print(f"\n--- Insight: Unexpected Gains (Negative Shrinkage < -5) ---")
        print(f"Count of products: {len(gains)}")
        if not gains.empty:
            print("Top 5 gains (Possible miscounts/restock errors):")
            print(gains[['Product ID', 'Shrinkage_Qty']].head(5).to_string(index=False))
            
        # 4. High Velocity Loss (Shrinkage % relative to Start inventory)
        # Filter: Quantity_Start > 10
        df_sig = df[df['Quantity_Start'] > 10].copy()
        df_sig['Loss_Rate'] = df_sig['Shrinkage_Qty'] / df_sig['Quantity_Start']
        high_rate = df_sig[df_sig['Loss_Rate'] > 0.5].sort_values('Loss_Rate', ascending=False)
        
        print(f"\n--- Insight: High Loss Rate (>50% of stock lost) ---")
        print(f"Count of products: {len(high_rate)}")
        if not high_rate.empty:
            print("Top 5 Depleted items:")
            print(high_rate[['Product ID', 'Quantity_Start', 'Shrinkage_Qty', 'Loss_Rate']].head(5).to_string(index=False))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze()
