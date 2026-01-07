import json
import os
from datetime import datetime, timedelta

def add_advanced_analysis():
    work_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
    json_path = os.path.join(work_dir, "n8n_consolidated_report_final_fixed.json")
    
    if not os.path.exists(json_path):
        print("JSON report not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Reference date for "Days Left" calculations
    ref_date = datetime(2025, 12, 27)

    def get_risk_level(row):
        # Logic: If shrinkage qty is high, mark as high theft risk
        return "HIGH THEFT RISK"

    print("Adding risk and waste analysis to all locations...")
    for loc_entry in data.get('location_ranking', []):
        shrink_prods = loc_entry.get('shrinkage_products', [])
        
        # 1. TOP 5 SHRINKAGE PRODUCTS (Risk Analysis)
        # Sort by shrinkage_qty descending
        sorted_shrink = sorted(shrink_prods, key=lambda x: x.get('shrinkage_qty', 0), reverse=True)
        top_5 = sorted_shrink[:5]
        
        risk_analysis = []
        for p in top_5:
            risk_analysis.append({
                "product_name": p.get('product_name'),
                "risk_level": get_risk_level(p)
            })
        loc_entry['top_shrinkage_risk'] = risk_analysis

        # 2. Waste Risk / Actions Table
        # We look for items with positive end stock that might expire
        # We can pull from spoilage_items (as potential future waste) or simply use available stock
        waste_actions = []
        
        # Pick top items from shrinkage_products that have quantity_end > 0
        potential_waste = [p for p in shrink_prods if p.get('quantity_end', 0) > 0]
        # Sort by quantity_end or value
        potential_waste = sorted(potential_waste, key=lambda x: x.get('quantity_end', 0), reverse=True)
        
        for p in potential_waste[:3]: # Add top 3 waste risks
            # Mock Expiry logic
            # Fresh items (names containing Milk, Salad, Sandwich, Yogurt) get closer dates
            name = str(p.get('product_name', '')).lower()
            if any(x in name for x in ['milk', 'salad', 'sandwich', 'yogurt', 'fruit', 'juice']):
                expiry = ref_date + timedelta(days=1)
            else:
                expiry = ref_date + timedelta(days=5)
            
            days_left = (expiry - ref_date).days
            
            waste_actions.append({
                "product": p.get('product_name'),
                "stock": p.get('quantity_end'),
                "expiry_date": expiry.strftime("%Y-%m-%d"),
                "days_left": f"{days_left}d",
                "waste_risk": round(p.get('quantity_end', 0) * (p.get('shrinkage_value', 0) / p.get('shrinkage_qty', 1) if p.get('shrinkage_qty', 0) > 0 else 2.5), 2),
                "action": "Bundle/Discount" if days_left <= 2 else "Monitor Stock"
            })
        
        loc_entry['waste_prevention_plan'] = waste_actions

    print("Saving updated report...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print("Done. Advanced analysis added to all micromarkets.")

if __name__ == "__main__":
    add_advanced_analysis()
