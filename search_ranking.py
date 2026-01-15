
import json
import os

def check_ranking():
    file_path = 'n8n_shrinkage_report_v2.json'
    if not os.path.exists(file_path):
        file_path = 'n8n_shrinkage_report.json'
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        ranking = data.get("location_ranking", [])
        
        print(f"Found {len(ranking)} locations.")
        found = False
        for loc in ranking:
            name = loc.get("location")
            if "Altura" in name:
                print(f"Found Location in Ranking: {name}")
                found = True
        
        if not found:
            print("Altura not found in ranking.")

if __name__ == "__main__":
    check_ranking()
