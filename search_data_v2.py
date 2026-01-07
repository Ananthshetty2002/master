import os

target_value = "3938"
target_str = "Cucamonga"

def search_files(directory):
    for root, dirs, files in os.walk(directory):
        if "venv" in root: continue
        for file in files:
            if not (file.endswith(".json") or file.endswith(".csv") or file.endswith(".md") or file.endswith(".txt")):
                continue
            
            path = os.path.join(root, file)
            
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f):
                        found_str = target_str.lower() in line.lower()
                        found_val = target_value in line
                        
                        if found_str or found_val:
                            msg = f"MATCH in {path} L{i+1}: "
                            if found_str: msg += f"[STR: {target_str}] "
                            if found_val: msg += f"[VAL: {target_value}] "
                            print(msg + line.strip()[:100])
            except Exception as e:
                pass

if __name__ == "__main__":
    search_files(".")
