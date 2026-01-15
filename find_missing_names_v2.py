import glob
import os
import csv
import json

ids_to_find = {'930', '1318', '1498', '1685', '230'}
found_matches = []

ignore_dirs = {'venv', '.git', '__pycache__', '.gemini'}

csv_files = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    for file in files:
        if file.endswith('.csv'):
            csv_files.append(os.path.join(root, file))

for f_path in csv_files:
    try:
        with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader):
                for target_id in ids_to_find:
                    if target_id in row:
                        # Heuristic: Find longest string that isn't the ID itself
                        potential_names = [c for c in row if len(str(c)) > 3 and not str(c).replace('.', '').isdigit()]
                        
                        found_matches.append({
                            'file': f_path,
                            'id': target_id,
                            'row': row,
                            'potential_names': potential_names
                        })
    except: pass

with open('missing_names_found.json', 'w') as f:
    json.dump(found_matches, f, indent=2)

print(f"Found {len(found_matches)} matches. Saved to missing_names_found.json")
