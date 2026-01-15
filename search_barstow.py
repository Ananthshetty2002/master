
import json

def search_minified():
    try:
        with open('n8n_shrinkage_report_minified.json', 'r') as f:
            data = json.load(f)
            products = data.get("data", [])
            
            count = 0
            for p in products:
                if "Barstow" in p.get("location", ""):
                    print(f"Product: {p.get('product_name')}, Shrink: {p.get('shrinkage_qty')}, Loc: {p.get('location')}")
                    count += 1
                    if count > 5: break
            print(f"Found {count} sample products.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_minified()
