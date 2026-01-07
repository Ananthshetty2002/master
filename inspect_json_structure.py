import json
import os

def inspect_json(filepath):
    print(f"--- Inspecting {os.path.basename(filepath)} ---")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if isinstance(data, dict):
            print("Top level keys:", list(data.keys()))
            for key in data.keys():
                if isinstance(data[key], list):
                    print(f"Key '{key}' is a list with {len(data[key])} items.")
                elif isinstance(data[key], dict):
                    print(f"Key '{key}' is a dict with keys: {list(data[key].keys())}")
                else:
                    print(f"Key '{key}' is of type {type(data[key])}")
            
            # Recursive search for 'transfer' in keys
            print("\nSearching for 'transfer' in keys recursively...")
            found_transfer = []
            def search_keys(d, path=""):
                if isinstance(d, dict):
                    for k, v in d.items():
                        current_path = f"{path}.{k}" if path else k
                        if 'transfer' in k.lower():
                            found_transfer.append(current_path)
                        if isinstance(v, (dict, list)):
                            search_keys(v, current_path)
                elif isinstance(d, list):
                     if len(d) > 0:
                        search_keys(d[0], f"{path}[0]")

            search_keys(data)
            if found_transfer:
                print("Found 'transfer' related keys:")
                for p in found_transfer:
                    print(p)
            else:
                print("No keys containing 'transfer' found.")

        else:
            print("Top level is not a dict.")

    except Exception as e:
        print(f"Error reading {filepath}: {e}")

file1 = "n8n_consolidated_report.json"
file2 = "n8n_consolidated_report1.json"

inspect_json(file1)
print("\n" + "="*30 + "\n")
inspect_json(file2)
