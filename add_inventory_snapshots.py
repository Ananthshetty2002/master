import pandas as pd
import json
from datetime import datetime

def add_inventory_snapshots():
    """Add Start Qty, End Qty, Present Stock to alerts by date period"""
    
    # Load current alerts
    with open('business_alerts.json', 'r', encoding='utf-8') as f:
        alerts = json.load(f)
    
    # Load main report for DEC 3-31 inventory data
    with open('n8n_consolidated_report_FINAL_VERIFIED.json', 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    print("Adding inventory snapshots...")
    
    # 1. DEC 3-31 Period - Add location and product inventory
    dec_main = alerts["data_periods"]["december_3_to_31_2025"]
    dec_main["inventory_snapshots"] = {
        "by_location": [],
        "by_product": []
    }
    
    # Extract location inventory
    for site in report.get('sites_full', []):
        location_inv = {
            "location": site.get('site'),
            "period": "DEC 3-31, 2025",
            "inventory": {
                "start_qty": None,  # Not in current report structure
                "end_qty": None,    # Not in current report structure
                "present_stock": None,  # Would be end_qty
                "total_shrinkage_qty": sum(p.get('shrinkage_qty', 0) for p in site.get('products', [])),
                "total_sales_units": sum(p.get('sales_units', 0) for p in site.get('products', []))
            }
        }
        dec_main["inventory_snapshots"]["by_location"].append(location_inv)
    
    # Extract product inventory (aggregate across all locations)
    product_inv = {}
    for site in report.get('sites_full', []):
        for product in site.get('products', []):
            pid = product.get('product_id')
            if pid not in product_inv:
                product_inv[pid] = {
                    "product_id": pid,
                    "product_name": product.get('product_name'),
                    "period": "DEC 3-31, 2025",
                    "inventory": {
                        "total_shrinkage_qty": 0,
                        "total_sales_units": 0,
                        "locations_count": 0
                    }
                }
            product_inv[pid]["inventory"]["total_shrinkage_qty"] += product.get('shrinkage_qty', 0)
            product_inv[pid]["inventory"]["total_sales_units"] += product.get('sales_units', 0)
            product_inv[pid]["inventory"]["locations_count"] += 1
    
    dec_main["inventory_snapshots"]["by_product"] = list(product_inv.values())
    
    # 2. Try to load DEC 8-19 Stock Analysis for that period
    try:
        df_8_19 = pd.read_csv(r'DEC 8-19/CSVStock Analysis Report.csv', skiprows=8)
        df_8_19.columns = [c.strip() for c in df_8_19.columns]
        
        dec_8_19 = alerts["data_periods"]["december_8_to_19_2025"]
        dec_8_19["inventory_snapshots"] = {
            "by_location": [],
            "by_product": [],
            "note": "Extracted from Stock Analysis Report"
        }
        
        # Group by location if possible
        if 'Micromarket' in df_8_19.columns or 'Location' in df_8_19.columns:
            loc_col = 'Micromarket' if 'Micromarket' in df_8_19.columns else 'Location'
            
            for location in df_8_19[loc_col].unique():
                if pd.notna(location):
                    loc_data = df_8_19[df_8_19[loc_col] == location]
                    
                    # Try to find quantity columns
                    qty_cols = [c for c in df_8_19.columns if 'qty' in c.lower() or 'quantity' in c.lower()]
                    
                    location_inv = {
                        "location": str(location),
                        "period": "DEC 8-19, 2025",
                        "inventory": {
                            "product_count": len(loc_data),
                            "data_available": qty_cols
                        }
                    }
                    dec_8_19["inventory_snapshots"]["by_location"].append(location_inv)
        
        print(f"  Added DEC 8-19 inventory snapshots")
    except Exception as e:
        print(f"  Could not load DEC 8-19 inventory: {e}")
    
    # 3. Try to load DEC 23-31 data
    try:
        # Check for new_dec_stock_analysis.csv
        df_23_31 = pd.read_csv(r'venv/DEC 23-31/new_dec_stock_analysis.csv')
        df_23_31.columns = [c.strip() for c in df_23_31.columns]
        
        dec_23_31 = alerts["data_periods"]["december_23_to_31_2025"]
        dec_23_31["inventory_snapshots"] = {
            "by_location": [],
            "by_product": [],
            "note": "End-of-month inventory snapshot"
        }
        
        # This would be the "Present Stock" as of Dec 31
        if 'Location' in df_23_31.columns:
            for location in df_23_31['Location'].unique():
                if pd.notna(location):
                    loc_data = df_23_31[df_23_31['Location'] == location]
                    
                    location_inv = {
                        "location": str(location),
                        "period": "DEC 23-31, 2025 (End of Month)",
                        "inventory": {
                            "present_stock_products": len(loc_data),
                            "note": "This represents inventory as of Dec 31"
                        }
                    }
                    dec_23_31["inventory_snapshots"]["by_location"].append(location_inv)
        
        print(f"  Added DEC 23-31 inventory snapshots")
    except Exception as e:
        print(f"  Could not load DEC 23-31 inventory: {e}")
    
    # 4. Load refined CSV for actual Start/End quantities
    try:
        df_refined = pd.read_csv('shrinkage_report_refined.csv')
        df_refined.columns = [c.strip() for c in df_refined.columns]
        
        # Add to DEC 3-31 period with actual start/end
        for location in df_refined['Location'].unique():
            if pd.notna(location):
                loc_data = df_refined[df_refined['Location'] == location]
                
                # Find the location in our snapshots and update
                for loc_inv in dec_main["inventory_snapshots"]["by_location"]:
                    if loc_inv["location"] == str(location):
                        loc_inv["inventory"]["start_qty"] = float(loc_data['Quantity_Start'].sum())
                        loc_inv["inventory"]["end_qty"] = float(loc_data['Quantity_End'].sum())
                        loc_inv["inventory"]["present_stock"] = float(loc_data['Quantity_End'].sum())
                        break
        
        print(f"  Updated DEC 3-31 with Start/End quantities from refined CSV")
    except Exception as e:
        print(f"  Could not load refined CSV: {e}")
    
    # Save updated alerts
    with open('business_alerts.json', 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2)
    
    print(f"\n✅ Inventory snapshots added!")
    print(f"  DEC 3-31: {len(dec_main['inventory_snapshots']['by_location'])} locations")
    print(f"  DEC 3-31: {len(dec_main['inventory_snapshots']['by_product'])} products")

if __name__ == "__main__":
    add_inventory_snapshots()
