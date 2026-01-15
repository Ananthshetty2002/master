
import json

def locate():
    with open('n8n_consolidated_report_final_fixed.json', 'r') as f:
        data = json.load(f)
    
    found = []
    def walk(obj, path):
        if isinstance(obj, dict):
            vals = obj.values()
            # Searching for 1329 and 907
            if 1329 in vals and 907 in vals:
                print(f"Found candidate at {path}")
                found.append(obj)
            
            for k, v in obj.items():
                walk(v, path + f".{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(item, path + f"[{i}]")

    walk(data, "root")
    
    if found:
        with open('found_entry.json', 'w') as f:
            json.dump(found, f, indent=2)
        print(f"Saved {len(found)} entries to found_entry.json")

if __name__ == "__main__":
    locate()
