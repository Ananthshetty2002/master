
import json

def search_minified():
    try:
        with open('n8n_shrinkage_report_minified.json', 'r') as f:
            data = json.load(f)
            products = data.get("data", [])
            
            for p in products:
                if p.get("product_id") == "PC10726" and "Altura" in p.get("location", ""):
                    print(f"Found Altura Match: Loc={p.get('location')}, Shrink={p.get('shrinkage_qty')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_minified()
