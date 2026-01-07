
import pandas as pd
import glob
import os
from datetime import datetime

patterns = [
    'transaction*.csv',
    'transactionlist*.csv',
    'Transaction List Report*.csv',
    'Product Transaction Report*.csv',
    'Sales By Products Report*.csv',
    'Overage Spoilage*.csv'
]

results = []

for pattern in patterns:
    for f in glob.glob(pattern):
        try:
            # Guessing headers/skips based on known patterns
            skip = 0
            if 'Transaction List Report' in f: skip = 9
            elif 'Sales By Products Report' in f: skip = 8
            elif 'Product Transaction Report' in f: skip = 1
            elif 'transaction' in f.lower(): skip = 0 # week files usually don't have headers
            
            df = pd.read_csv(f, skiprows=skip, nrows=5000, low_memory=False)
            
            date_cols = [c for c in df.columns if 'Date' in c or 'Created' in c or 'Time' in c]
            loc_cols = [c for c in df.columns if 'Market' in c or 'Location' in c or 'Site' in c]
            
            res = f"{f}: {len(df)} rows (sample)"
            if loc_cols: res += f", SiteCol: {loc_cols[0]}"
            
            if date_cols:
                df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors='coerce')
                min_d = df[date_cols[0]].min()
                max_d = df[date_cols[0]].max()
                if pd.notnull(min_d):
                    res += f", Dates: {min_d.date()} to {max_d.date()}"
            results.append(res)
        except Exception as e:
            results.append(f"{f}: Error {e}")

with open('comprehensive_inspection.txt', 'w') as out:
    for r in sorted(results):
        out.write(r + "\n")
