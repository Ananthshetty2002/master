import os

target_value = "716.0"
target_str = "716"

def search_files(directory):
    for root, dirs, files in os.walk(directory):
        if "venv" in root: continue
        for file in files:
            if not (file.endswith(".json") or file.endswith(".csv")):
                continue
            
            path = os.path.join(root, file)
            
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if target_str in content:
                        print(f"FOUND {target_str} in {path}")
            except Exception as e:
                pass

if __name__ == "__main__":
    search_files(".")
