import json
import os

def optimize_for_gist(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    print(f"Original size: {os.path.getsize(file_path) / 1024:.2f} KB")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    def round_floats(obj):
        if isinstance(obj, float):
            return round(obj, 2)
        if isinstance(obj, dict):
            return {k: round_floats(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [round_floats(i) for i in obj]
        return obj

    # 1. Round all decimals to 2 places
    print("Rounding decimals...")
    optimized_data = round_floats(data)

    # 2. Minify (remove all whitespace)
    print("Minifying JSON...")
    minified_content = json.dumps(optimized_data, separators=(',', ':'))

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(minified_content)

    new_size = os.path.getsize(file_path)
    print(f"Final size: {new_size / 1024:.2f} KB")
    print(f"Total reduction: {((1 - new_size/os.path.getsize(file_path+'_backup' if os.path.exists(file_path+'_backup') else file_path)) * 100):.2f}%") # Rough calc

if __name__ == "__main__":
    optimize_for_gist('n8n_consolidated_report_final_fixed.json')
