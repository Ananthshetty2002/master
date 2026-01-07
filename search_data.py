import json
import csv
import os

target_value = 3938
target_str = "Cucamonga"

def search_files(directory):
    for root, dirs, files in os.walk(directory):
        if "venv" in root: continue
        for file in files:
            if not (file.endswith(".json") or file.endswith(".csv")):
                continue
            
            path = os.path.join(root, file)
            print(f"Checking {path}...")
            
            try:
                if file.endswith(".json"):
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if target_str.lower() in content.lower():
                            print(f"FOUND string '{target_str}' in {path}")
                        if str(target_value) in content:
                            print(f"FOUND value '{target_value}' in {path}")
                
                elif file.endswith(".csv"):
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        for i, line in enumerate(f):
                            if target_str.lower() in line.lower():
                                print(f"FOUND string '{target_str}' in {path} at line {i+1}")
                            if str(target_value) in line:
                                print(f"FOUND value '{target_value}' in {path} at line {i+1}")
            except Exception as e:
                print(f"Error reading {path}: {e}")

if __name__ == "__main__":
    search_files(".")
