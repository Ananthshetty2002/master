import pandas as pd
import glob
import os

targets = ['930', '1318', '1498', '1685']
all_csvs = glob.glob('**/*.csv', recursive=True)

print(f"Searching for {targets} in {len(all_csvs)} CSV files...")

for f in all_csvs:
    try:
        # Load small chunks to check
        df = pd.read_csv(f, low_memory=False, nrows=10000)
        # Check every column
        for col in df.columns:
            # Check if any target is in this column
            matches = df[df[col].astype(str).str.contains('|'.join(targets), na=False)]
            if not matches.empty:
                print(f"\n[MATCH FOUND] in {f}, Column: {col}")
                # Print the whole row for context
                print(matches.head(10).to_string())
    except Exception as e:
        # Some files might be messy, skip them
        pass
