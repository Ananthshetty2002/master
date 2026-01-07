import csv

path = r"C:\Users\IV-UDP-DT-0122\Downloads\shrinkage\transaction list week8.csv"

try:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < 15: continue # Skip likely headers and garbage
            if i > 15: break # Just look at one data row
            
            print(f"--- Row {i} ---")
            for idx, val in enumerate(row):
                print(f"{idx}: {val}")
except Exception as e:
    print(e)
