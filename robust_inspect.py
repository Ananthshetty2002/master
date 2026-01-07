import pandas as pd
import os

def find_header_and_dates(path):
    print(f"\nAnalyzing: {path}")
    df_raw = pd.read_csv(path, header=None, low_memory=False)
    header_row = -1
    for i, row in df_raw.iterrows():
        row_str = ' '.join(str(x) for x in row.values)
        if 'Micromarket' in row_str or 'Micro Market' in row_str or 'MicroMarket' in row_str:
            header_row = i
            break
    
    if header_row == -1:
        print("Could not find Micromarket header.")
        return
    
    print(f"Header found at row {header_row}")
    df = pd.read_csv(path, skiprows=header_row)
    print("Columns:", df.columns.tolist())
    
    date_col = None
    for col in df.columns:
        if 'Created On' in str(col) or 'Date' in str(col):
            date_col = col
            break
    
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        valid_dates = df[date_col].dropna()
        if not valid_dates.empty:
            print(f"Date Range: {valid_dates.min()} to {valid_dates.max()}")
        else:
            print("No valid dates found in date column.")
    else:
        print("No date column found.")

find_header_and_dates('new_dec_stock_analysis.csv')
find_header_and_dates('new_dec_transaction_list.csv')
find_header_and_dates('new_shrinkage_dec.csv')
find_header_and_dates('Stock Analysis Report.csv')
