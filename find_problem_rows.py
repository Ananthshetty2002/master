import csv
import os

target_file = 'venv/DEC 23-31/new_dec_stock_analysis.csv'
targets = ['930', '1498', '1318', '1685']

print(f"Searching for {targets} in {target_file}...")
if not os.path.exists(target_file):
    print("File not found.")
else:
    with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            # Check if any target is exactly in any cell
            if any(t in [cell.strip() for cell in row] for t in targets):
                print(f"Row {i}: {row}")
