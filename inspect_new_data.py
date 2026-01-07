import pandas as pd
import os

def inspect(name, path):
    print(f"--- {name} ---")
    if not os.path.exists(path):
        print(f"File {path} not found.")
        return
    df = pd.read_csv(path, low_memory=False)
    header_found = False
    for i in range(min(100, len(df))):
        row_values = [str(x) for x in df.iloc[i].values]
        row_str = ' '.join(row_values)
        if any(kw in row_str for kw in ['Micromarket', 'Micro Market', 'MicroMarket']):
            print(f"Header found at row {i}")
            print('Columns at this row:', row_values)
            # Try to determine date range if it looks like a transaction list
            if any('Created On' in val or 'trans_date' in val for val in row_values):
                # We need to reload the DF with this row as header to get dates easily
                df_temp = pd.read_csv(path, skiprows=i+1, low_memory=False)
                # Some files have 'Created On'
                date_cols = [c for c in df_temp.columns if 'Created On' in str(c) or 'Date' in str(c)]
                if date_cols:
                    col = date_cols[0]
                    df_temp[col] = pd.to_datetime(df_temp[col], errors='coerce')
                    print(f"Date range: {df_temp[col].min()} to {df_temp[col].max()}")
            header_found = True
            break
    if not header_found:
        print("Header not found in first 100 rows.")
        print("Columns of raw file:", df.columns.tolist())
        # Check dates anyway if 'Created On' is in columns
        date_cols = [c for c in df.columns if 'Created On' in str(c) or 'Date' in str(c)]
        if date_cols:
            col = date_cols[0]
            df[col] = pd.to_datetime(df[col], errors='coerce')
            print(f"Date range: {df[col].min()} to {df[col].max()}")

inspect('stock analysis', 'new_dec_stock_analysis.csv')
inspect('transaction list', 'new_dec_transaction_list.csv')
inspect('shrinkage dec', 'new_shrinkage_dec.csv')
