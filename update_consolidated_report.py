import json
import pandas as pd
import os

REPORT_FILE = "shrinkage_report_refined.csv"
JSON_FILE = "n8n_consolidated_report.json"
DEFAULT_LOCATION = "FFI - Moorpark" # As identified in previous context

def update_report():
    print(f"Loading {REPORT_FILE}...")
    if not os.path.exists(REPORT_FILE):
        print(f"Error: {REPORT_FILE} not found.")
        return
    
    df = pd.read_csv(REPORT_FILE)
    df['Product ID'] = df['Product ID'].astype(str)
    
    print(f"Loading {JSON_FILE}...")
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found.")
        return
        
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    def process_item(item):
        if not isinstance(item, dict):
            return item
            
        # Always fix "Stock" if it exists as a Location
        if item.get("Location") == "Stock":
            item["Location"] = DEFAULT_LOCATION
            
        prod_id = str(item.get("Product ID", ""))
        if not prod_id:
            return item
            
        matches = df[df['Product ID'] == prod_id]
        if matches.empty:
            return item
            
        best_match = None
        target_qty = item.get("Shrinkage_Qty")
        if target_qty is not None:
            qty_matches = matches[matches['Shrinkage_Qty'] == float(target_qty)]
            if not qty_matches.empty:
                best_match = qty_matches.iloc[0]
        
        if best_match is None:
            target_val = item.get("Shrinkage_Value")
            if target_val is not None:
                val_matches = matches[matches['Shrinkage_Value'] == float(target_val)]
                if not val_matches.empty:
                    best_match = val_matches.iloc[0]
        
        if best_match is None:
            best_match = matches.iloc[0]
            
        loc = best_match["Location"]
        if loc == "Stock":
            loc = DEFAULT_LOCATION
            
        item["Location"] = loc
        item["Product ID"] = best_match["Product ID"]
        item["Shrinkage_Qty"] = float(best_match["Shrinkage_Qty"])
        item["Shrinkage_Value"] = float(best_match["Shrinkage_Value"])
        
        if "Implied_Unit_Price" in best_match:
            item["Implied_Unit_Price"] = float(best_match["Implied_Unit_Price"])
        if "Quantity_Start" in best_match:
            item["Quantity_Start"] = float(best_match["Quantity_Start"])
        if "Quantity_End" in best_match:
            item["Quantity_End"] = float(best_match["Quantity_End"])
        if "Sales_Quantity" in best_match:
            item["Sales_Units"] = float(best_match["Sales_Quantity"])
        if "Loss_Rate" in best_match:
            item["Loss_Rate"] = float(best_match["Loss_Rate"])
        
        return item

    print("Updating insights...")
    for insight in master_data.get("insights", []):
        result_data = insight.get("result_data")
        
        if isinstance(result_data, list):
            insight["result_data"] = [process_item(it) for it in result_data]
        elif isinstance(result_data, dict):
            for key, items in result_data.items():
                if isinstance(items, list):
                    result_data[key] = [process_item(it) for it in items]
    
    print(f"Saving updated {JSON_FILE}...")
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, indent=4)
        
    print("Done!")

if __name__ == "__main__":
    update_report()
