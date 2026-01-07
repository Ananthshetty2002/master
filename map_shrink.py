import csv

path = r"C:\Users\IV-UDP-DT-0122\Downloads\shrinkage\pilot_shrink_log.csv"

try:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i < 1: continue 
            if i > 1: break 
            
            print(f"--- Row {i} ---")
            for idx, val in enumerate(row):
                print(f"{idx}: {val}")
except Exception as e:
    print(e)
