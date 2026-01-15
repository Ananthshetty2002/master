import glob
import os
import csv

ids_to_find = {'930', '1318', '1498', '1685', '230'}
found_map = {}

ignore_dirs = {'venv', '.git', '__pycache__', '.gemini'}

print("Searching for IDs:", ids_to_find)

csv_files = []
for root, dirs, files in os.walk('.'):
    # Modify dirs in-place to skip ignored directories
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    for file in files:
        if file.endswith('.csv'):
            csv_files.append(os.path.join(root, file))

for f_path in csv_files:
    try:
        with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader):
                # Convert row to string to check for ID presence first (optimization)
                row_str = ','.join(row)
                
                # Check each ID
                for target_id in ids_to_find:
                    # Look for exact match in columns
                    # We assume the name might be in an adjacent column
                    if target_id in row:
                        print(f"\n[MATCH] {target_id} in {f_path} row {row_idx}")
                        print(f"Row: {row}")
                        
                        # Try to guess the name (longest non-numeric string?)
                        potential_names = [c for c in row if len(c) > 3 and not c.replace('.', '').isdigit()]
                        if potential_names:
                             print(f"Potential Name: {potential_names}")

    except Exception as e:
        pass
