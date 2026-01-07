
import pandas as pd
import glob
import os
import sys

# Define file paths
PROD_TRANS_FILE = "c:/Users/IV-UDP-DT-0122/Downloads/shrinkage/Product Transaction Report (2).csv"
OVERAGE_FILE = "c:/Users/IV-UDP-DT-0122/Downloads/shrinkage/Overage Spoilage Shrinkage ReportUltraserv Automated Services 2025-12-04.csv"
SALES_FILES_PATTERN = "c:/Users/IV-UDP-DT-0122/Downloads/shrinkage/transaction*week*.csv"
OUTPUT_FILE = "c:/Users/IV-UDP-DT-0122/Downloads/shrinkage/shrinkage_analysis_output.csv"

def normalize_sales_columns(df, filename):
    # Standardize to: Location, Product Code, Quantity, Total Sales
    cols = df.columns
    
    # Location
    if 'Micro Market' in cols:
        df.rename(columns={'Micro Market': 'Location'}, inplace=True)
    elif 'Micromarket' in cols:
        df.rename(columns={'Micromarket': 'Location'}, inplace=True)
    elif 'Site' in cols:
        df.rename(columns={'Site': 'Location'}, inplace=True)
    elif 'Location' in cols:
        pass
    else:
        print(f"  Skipping {filename}: No Location column found in {list(cols)}")
        return None

    # Quantity
    if 'Quantity' in cols:
        pass
    elif 'Qty' in cols:
        df.rename(columns={'Qty': 'Quantity'}, inplace=True)
    elif 'Qty Sold' in cols:
        df.rename(columns={'Qty Sold': 'Quantity'}, inplace=True)
    else:
        print(f"  Skipping {filename}: No Quantity column found")
        return None

    # Total Sales (Value)
    if 'Total Sales' in cols:
        pass
    elif 'Sales' in cols:
        df.rename(columns={'Sales': 'Total Sales'}, inplace=True)
    elif 'Total Price' in cols:
        df.rename(columns={'Total Price': 'Total Sales'}, inplace=True)
    elif 'Price' in cols: # If only price, calculate total? No, assume Total exists
        # If no total sales column, maybe we can assume 0 or calc?
        # Let's verify 'transaction list week8.csv' had 'Total Sales'
        pass
    
    return df

def load_sales_data():
    print("Loading Sales Data...")
    all_files = glob.glob(SALES_FILES_PATTERN)
    df_list = []
    for filename in all_files:
        print(f"  Processing {os.path.basename(filename)}...")
        try:
            # Read header first
            header = pd.read_csv(filename, nrows=0).columns
            usecols = []
            
            # Identify columns to read
            for c in ['Micro Market', 'Micromarket', 'Site', 'Location', \
                      'Product Code', 'Product', 'Product_Code', \
                      'Quantity', 'Qty', 'Qty Sold', \
                      'Total Sales', 'Sales', 'Total Price']:
                if c in header:
                    usecols.append(c)
            
            df = pd.read_csv(filename, usecols=list(set(usecols)), low_memory=False)
            df = normalize_sales_columns(df, filename)
            
            if df is not None:
                # Ensure Product Code exists
                if 'Product Code' not in df.columns and 'Product' in df.columns:
                     df.rename(columns={'Product': 'Product Code'}, inplace=True)
                
                if 'Product Code' in df.columns:
                    df_list.append(df)
                else:
                    print(f"  Skipping {filename}: No Product Code column")

        except Exception as e:
            print(f"  Error reading {filename}: {e}")
            
    if not df_list:
        print("  No valid sales files loaded.")
        return pd.DataFrame()
        
    full_sales = pd.concat(df_list, ignore_index=True)
    
    # Check aggregation key existence
    if 'Location' not in full_sales.columns:
        print("  Critical: 'Location' column missing after sales load.")
        return pd.DataFrame()

    print("  Aggregating Sales...")
    sales_agg = full_sales.groupby(['Location', 'Product Code']).agg({
        'Quantity': 'sum',
        'Total Sales': 'sum'
    }).reset_index()
    sales_agg.rename(columns={'Quantity': 'Total_Sales_Qty', 'Total Sales': 'Total_Sales_Value'}, inplace=True)
    return sales_agg

def load_inventory_in_data():
    print("Loading Inventory In (Product Transaction Report)...")
    try:
        df = pd.read_csv(PROD_TRANS_FILE, low_memory=False)
        
        # Verify columns
        if 'Location' not in df.columns:
             print("  Error: 'Location' column missing in Product Transaction Report")
             return pd.DataFrame()
             
        df['Transfer Type'] = df['Transfer Type'].astype(str).str.strip()
        df = df[df['Location'].notna()]
        
        in_types = ['Bill', 'Transfer - Receipt', 'Direct Invoice', 'Purchase', 'Restock']
        df_in = df[df['Transfer Type'].isin(in_types)]
        
        inv_agg = df_in.groupby(['Location', 'Product Code']).agg({
             'Qty': 'sum',
             'Amount': 'sum'
        }).reset_index()
        inv_agg.rename(columns={'Qty': 'Total_In_Qty', 'Amount': 'Total_In_Cost'}, inplace=True)
        return inv_agg
        
    except Exception as e:
        print(f"  Error reading Inventory file: {e}")
        return pd.DataFrame()

def load_adjustment_data():
    print("Loading Recorded Shrinkage (Overage Report)...")
    try:
        df = pd.read_csv(OVERAGE_FILE, low_memory=False)
        
        if 'Micromarket' in df.columns:
            df.rename(columns={'Micromarket': 'Location'}, inplace=True)
        
        if 'Location' not in df.columns:
             print("  Error: 'Location/Micromarket' column missing in Overage Report")
             return pd.DataFrame()
             
        # Filter for legitimate Known Adjustments
        if 'Change Type' in df.columns:
            valid_types = ['Spoilage', 'Shrinkage', 'Quantity Adjustment']
            df = df[df['Change Type'].isin(valid_types)]
        else:
            print("  Warning: 'Change Type' column missing in Overage Report. Using all data as adjustments.")

        adj_agg = df.groupby(['Location', 'Product Code']).agg({
            'Quantity': 'sum',
            'Total Product cost': 'sum'
        }).reset_index()
        adj_agg.rename(columns={'Quantity': 'Known_Adjustments_Qty', 'Total Product cost': 'Known_Adjustments_Cost'}, inplace=True)
        return adj_agg
    except Exception as e:
        print(f"  Error reading Overage file: {e}")
        return pd.DataFrame()

def main():
    sales = load_sales_data()
    inv_in = load_inventory_in_data()
    shrink = load_adjustment_data()
    
    if sales.empty and inv_in.empty:
        print("No Sales or Inventory data loaded. Exiting.")
        return

    print("Merging Data...")
    merged = pd.merge(sales, inv_in, on=['Location', 'Product Code'], how='outer')
    merged = pd.merge(merged, shrink, on=['Location', 'Product Code'], how='outer')
    
    for col in ['Total_Sales_Qty', 'Total_Sales_Value', 'Total_In_Qty', 'Total_In_Cost', 'Known_Adjustments_Qty', 'Known_Adjustments_Cost']:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0)
        else:
            merged[col] = 0
            
    # Calculations
    merged['Implied_Stock_Delta'] = merged['Total_In_Qty'] - merged['Total_Sales_Qty']
    # Shrink_Qty_Approx = Total_In – Total_Sales – Known_Adjustments
    merged['Shrink_Qty_Approx'] = merged['Total_In_Qty'] - merged['Total_Sales_Qty'] - merged['Known_Adjustments_Qty']
    
    print(f"Saving analysis to {OUTPUT_FILE}...")
    merged.to_csv(OUTPUT_FILE, index=False)
    print("Analysis saved.")

if __name__ == "__main__":
    main()
