import json
import random
from datetime import datetime, timedelta

# --- 1. MOCK DATA GENERATOR (Simulating "Input" Node) ---

def generate_mock_data():
    """
    Generates mock Sales and Inventory data for:
    - Scenario A: Winter Seasonality (Low sales in Nov-Feb)
    - Scenario B: Incorrect Par Levels (Low traffic, High par)
    """
    
    locations = ["Location_Alpha", "Location_Beta", "Location_Gamma"]
    products = ["Iced_Coffee", "Hot_Soup", "Salad_Bowl"]
    
    # Date range: Last 6 months including winter
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    sales_data = []
    inventory_data = []
    
    # Inventory Par Levels (Static for simulation)
    # Scenario B: Location_Beta has INCORRECT Par Levels (High Par for Low Traffic items)
    par_levels = {
        "Location_Alpha": {"Iced_Coffee": 50, "Hot_Soup": 30, "Salad_Bowl": 40},
        "Location_Beta":  {"Iced_Coffee": 80, "Hot_Soup": 20, "Salad_Bowl": 20}, # High Par for Iced Coffee
        "Location_Gamma": {"Iced_Coffee": 40, "Hot_Soup": 40, "Salad_Bowl": 40},
    }

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        month = current_date.month
        is_winter = month in [11, 12, 1, 2]
        
        for loc in locations:
            for prod in products:
                par = par_levels[loc][prod]
                
                # Base Sales Logic
                sales_qty = random.randint(int(par * 0.6), int(par * 0.9)) # Normal healthy sales
                
                # --- APPLY SCENARIO LOGIC ---
                
                # Scenario A: Winter Seasonality
                # "Iced_Coffee" drops significantly in Winter
                if is_winter and prod == "Iced_Coffee":
                    sales_qty = random.randint(int(par * 0.1), int(par * 0.3))
                
                # Scenario B: Incorrect Par Levels (Location_Beta)
                # Location_Beta has naturally low traffic for Iced_Coffee distinct from seasonality,
                # but let's say it's just consistently low vs the High Par set above.
                if loc == "Location_Beta" and prod == "Iced_Coffee":
                     # Even in summer, they don't sell 80.
                     # Max demand might be 30.
                     sales_qty = min(sales_qty, random.randint(10, 25))

                sales_data.append({
                    "date": date_str,
                    "location": loc,
                    "product": prod,
                    "quantity_sold": sales_qty
                })
                
                # Snapshot of inventory (assuming end-of-day level = Par - Sales for simplicity of waste calc context,
                # or just logging the Par to compare against).
                # The requirement asks to use Par Utilization, so we need Par.
                if current_date == end_date: # Just take latest snapshot for "Current" data
                    inventory_data.append({
                        "location": loc,
                        "product": prod,
                        "par_level": par,
                        "current_stock": par - sales_qty # Remainder
                    })
        
        current_date += timedelta(days=1)

    return sales_data, inventory_data

# --- 2. LOGIC NODES (The "Agent" Logic) ---

def node_combine_datasets(sales, inventory):
    """Combines sales history with current inventory/par info."""
    # Organize sales by loc/product to make math easier
    sales_map = {}
    for record in sales:
        key = (record['location'], record['product'])
        if key not in sales_map:
            sales_map[key] = []
        sales_map[key].append(record['quantity_sold'])
        
    combined = []
    for item in inventory:
        key = (item['location'], item['product'])
        combined.append({
            **item,
            "sales_history": sales_map.get(key, [])
        })
    return combined

def node_calculate_daily_avg_sales(data):
    """Calculates Daily Avg Sales from history."""
    for item in data:
        history = item.get("sales_history", [])
        if history:
            avg_sales = sum(history) / len(history)
            item["daily_avg_sales"] = round(avg_sales, 2)
        else:
            item["daily_avg_sales"] = 0
    return data

def node_calculate_par_utilization(data):
    """Calculates Current Par Utilization (Avg Sales / Par)."""
    for item in data:
        par = item['par_level']
        avg_sales = item['daily_avg_sales']
        
        if par > 0:
            utilization = (avg_sales / par) * 100
            item["par_utilization_pct"] = round(utilization, 2)
        else:
            item["par_utilization_pct"] = 0.0
    return data

def node_flag_high_waste(data):
    """
    Flag high waste locations (> 30% Waste).
    Waste implies Utilization < 70% (Since 100% - 70% Sold = 30% Unsold/Waste risk).
    """
    analyzed_output = []
    
    for item in data:
        utilization = item["par_utilization_pct"]
        # If Utilization is Say 60%, then 40% is potentially wasted/overstocked.
        # Threshold: High Waste > 30%  => Utilization < 70%
        
        waste_risk_pct = 100 - utilization
        is_high_waste = waste_risk_pct > 30
        
        analyzed_output.append({
            "location": item["location"],
            "product": item["product"],
            "par_level": item["par_level"],
            "daily_avg_sales": item["daily_avg_sales"],
            "par_utilization_pct": f"{utilization}%",
            "waste_risk_pct": f"{round(waste_risk_pct, 2)}%",
            "alert": "HIGH_WASTE" if is_high_waste else "OK"
        })
    return analyzed_output

# --- 3. WORKFLOW RUNNER ---

def run_agent():
    # Step 1: Input
    print("--- [Node: Input Data] Generating Mock Data ---")
    sales_data, inventory_data = generate_mock_data()
    print(f"Generated {len(sales_data)} sales records and {len(inventory_data)} inventory records.\n")
    
    # Step 2: Combine
    print("--- [Node: Combine Datasets] ---")
    combined_data = node_combine_datasets(sales_data, inventory_data)
    
    # Step 3: Calc Avg Sales
    print("--- [Node: Calc Daily Avg Sales] ---")
    data_with_avgs = node_calculate_daily_avg_sales(combined_data)
    
    # Step 4: Calc Par Utilization
    print("--- [Node: Calc Par Utilization] ---")
    data_with_util = node_calculate_par_utilization(data_with_avgs)
    
    # Step 5: Flag Logic
    print("--- [Node: Flag High Waste] ---")
    final_output = node_flag_high_waste(data_with_util)
    
    # Step 6: JSON Output
    print("--- [Node: JSON Output] ---")
    json_output = json.dumps(final_output, indent=2)
    print(json_output)
    
    with open('analyzed_metrics.json', 'w') as f:
        f.write(json_output)
    print("\n[System] Output saved to analyzed_metrics.json")

if __name__ == "__main__":
    run_agent()
