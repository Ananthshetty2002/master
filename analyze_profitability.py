import csv
from datetime import datetime
from collections import defaultdict

def parse_date(date_str):
    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.split('.')[0], fmt).date()
        except ValueError:
            pass
    return None

def analyze_profitability():
    trans_path = r"C:\Users\IV-UDP-DT-0122\Downloads\shrinkage\transaction list week8.csv"
    waste_path = r"C:\Users\IV-UDP-DT-0122\Downloads\shrinkage\pilot_shrink_log.csv"
    
    # Target Period: Widen to catch available data
    start_date = datetime(2025, 11, 30).date()
    end_date = datetime(2025, 12, 12).date()
    
    print(f"Analyzing Profitability for period: {start_date} to {end_date}")
    
    # 1. Load Sales Data
    sales_stats = defaultdict(lambda: {'revenue': 0.0, 'units': 0.0})
    dates_found = set()
    
    try:
        with open(trans_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 13: continue
                date_val = parse_date(row[0])
                if date_val:
                    dates_found.add(date_val)
                    if start_date <= date_val <= end_date:
                        try:
                            prod_name = row[6].strip()
                            # Clean product name logic?
                            rev = float(row[12]) if row[12] else 0.0
                            units = float(row[11]) if row[11] else 0.0
                            
                            sales_stats[prod_name]['revenue'] += rev
                            sales_stats[prod_name]['units'] += units
                        except ValueError:
                            continue
    except Exception as e:
        print(f"Error reading transactions: {e}")

    if dates_found:
        print(f"Transaction Dates Found: {sorted(list(dates_found))[0]} to {sorted(list(dates_found))[-1]}")
    else:
        print("No transaction dates found.")

    # 2. Load Waste Data & Costs
    waste_stats = defaultdict(lambda: {'cost': 0.0, 'qty': 0.0})
    unit_costs = {}
    
    try:
        with open(waste_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 10: continue
                date_val = parse_date(row[2])
                if date_val and start_date <= date_val <= end_date:
                    try:
                        prod_name = row[4].strip()
                        cost = float(row[9])
                        qty = float(row[8])
                        unit_c = float(row[7])
                        
                        waste_stats[prod_name]['cost'] += cost
                        waste_stats[prod_name]['qty'] += qty
                        if unit_c > 0:
                            unit_costs[prod_name] = unit_c
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Error reading waste: {e}")

    # 3. Calculate Profitability
    results = []
    
    for prod, data in sales_stats.items():
        revenue = data['revenue']
        units = data['units']
        
        if revenue <= 0: continue
        
        # Get Cost
        unit_cost = unit_costs.get(prod)
        w_cost = waste_stats.get(prod, {}).get('cost', 0.0)
        
        cogs = 0.0
        if unit_cost:
            cogs = units * unit_cost
        
        gross_profit = revenue - cogs
        net_profit = gross_profit - w_cost
        
        margin_pct = 0.0
        if revenue > 0:
            margin_pct = (net_profit / revenue) * 100
            
        rating = '?'
        if unit_cost:
            if margin_pct > 25: rating = 'A'
            elif margin_pct >= 15: rating = 'B'
            elif margin_pct >= 5: rating = 'C'
            else: rating = 'D'
        elif w_cost > 0:
             # Logic for waste but no cost? Use full revenue as margin base but subtract waste? 
             # Just mark as ?
             pass
            
        results.append({
            'product': prod,
            'revenue': revenue,
            'waste': w_cost,
            'margin': margin_pct,
            'rating': rating,
            'has_cost': unit_cost is not None
        })
        
    # Sort by Margin (ascending) for D-grade
    results.sort(key=lambda x: x['margin'])
    
    print(f"\nPotential D-Grade Products (Low/Negative Margin) - Top 20")
    print("-" * 120)
    print(f"{'Product':<40} | {'Rev ($)':<10} | {'Waste ($)':<10} | {'Margin %':<10} | {'Rating'}")
    print("-" * 120)
    
    for r in results[:20]:
        if r['has_cost']:
            print(f"{r['product'][:40]:<40} | {r['revenue']:<10.2f} | {r['waste']:<10.2f} | {r['margin']:<10.1f} | {r['rating']}")

    print("\n--- Haagen Dazs / Ice Cream Check ---")
    for r in results:
        if "Haag" in r['product'] or "Ice Cream" in r['product']:
             print(f"{r['product'][:40]:<40} | {r['revenue']:<10.2f} | {r['waste']:<10.2f} | {r['margin']:<10.1f} | {r['rating']}")

if __name__ == "__main__":
    analyze_profitability()
