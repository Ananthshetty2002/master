import pandas as pd

def refine_report():
    print("Refining Shrinkage Report...")
    try:
        # Load the raw report
        report_df = pd.read_csv('shrinkage_report.csv')
        
        # Load the transaction data for price estimation
        trans_df = pd.read_csv('transactionlistweek2.csv', low_memory=False)
        
        # Calculate global unit prices per product
        # Unit Price = Total Sales / Quantity
        global_prices = trans_df.groupby('Product Code').agg({
            'Quantity': 'sum',
            'Sales': 'sum'
        }).reset_index()
        
        global_prices['Global_Unit_Price'] = global_prices.apply(
            lambda x: x['Sales'] / x['Quantity'] if x['Quantity'] > 0 else 0, axis=1
        )
        global_prices = global_prices[['Product Code', 'Global_Unit_Price']].rename(columns={'Product Code': 'Product ID'})
        
        # Merge global prices into the report
        report_df = pd.merge(report_df, global_prices, on='Product ID', how='left')
        report_df['Global_Unit_Price'] = report_df['Global_Unit_Price'].fillna(0)
        
        # Refine Implied_Unit_Price: Use Sales_Value/Sales_Quantity if available, else Global_Unit_Price
        def get_best_price(row):
            if row['Sales_Quantity'] > 0:
                return row['Sales_Value'] / row['Sales_Quantity']
            return row['Global_Unit_Price']
            
        report_df['Implied_Unit_Price'] = report_df.apply(get_best_price, axis=1)
        
        # Recalculate Shrinkage_Value
        report_df['Shrinkage_Value'] = report_df['Shrinkage_Qty'] * report_df['Implied_Unit_Price']
        
        # Drop the helper column and save
        report_df = report_df.drop(columns=['Global_Unit_Price'])
        report_df.to_csv('shrinkage_report_refined.csv', index=False)
        
        print("Refined report saved to 'shrinkage_report_refined.csv'")
        
        # Show top 5 "Ghost" items with refined values
        ghosts = report_df[(report_df['Sales_Quantity'] == 0) & (report_df['Shrinkage_Qty'] > 10)]
        print("\nTop 5 Refined Ghost Items:")
        print(ghosts[['Product ID', 'Shrinkage_Qty', 'Implied_Unit_Price', 'Shrinkage_Value']].head(5))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    refine_report()
