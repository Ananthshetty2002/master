import pandas as pd
import glob

files = glob.glob('*.csv')
search_terms = ["Boom", "Penn", "Tennis", "Popcorn"]

for file in files:
    try:
        # Read a few rows to check if it's a valid CSV
        df_head = pd.read_csv(file, nrows=0)
        cols = df_head.columns.tolist()
        
        # Now search the file raw
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if any(term.lower() in line.lower() for term in search_terms):
                    if "Sea Salt" in line and "4.8oz" in line:
                        print(f"MATCH in {file} line {i}: {line.strip()}")
                    if "Tennis" in line:
                        print(f"MATCH in {file} line {i}: {line.strip()}")
    except:
        continue
