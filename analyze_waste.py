import csv
from datetime import datetime
from collections import defaultdict

def analyze_waste():
    log_path = r"C:\Users\IV-UDP-DT-0122\Downloads\shrinkage\pilot_shrink_log.csv"
    
    target_start_date = datetime(2025, 12, 4)
    target_end_date = datetime(2025, 12, 11)
    
    relevant_data = []
    product_names = set()
    
    print(f"Analyzing data from {log_path} for period {target_start_date.date()} to {target_end_date.date()}...")
    
    try:
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            header = next(reader, None) # Skip header if exists, but check if it's actually a header
            
            # Simple heuristic to find column indices if header exists
            # Based on previous output: Site, User Name, Date, SKU Code, Product Name, Category, Type, Cost, Qty, Total Cost...
            # Let's try to map by index based on observation
            # 0: Site
            # 2: Date
            # 4: Product Name (Estimated)
            # 6: Type (Overage/Spoilage)
            # 9: Total Cost (Estimated - need to verify)
            
            for row in reader:
                if not row or len(row) < 10: continue
                
                try:
                    date_str = row[2]
                    try:
                        dt = datetime.strptime(date_str, '%Y-%m-%d')
                    except ValueError:
                        continue # Skip invalid dates
                        
                    if target_start_date <= dt <= target_end_date:
                        product_name = row[4]
                        shrink_type = row[6] # Overage, Spoilage, etc.
                        
                        # Check for target products
                        if "Life Water" in product_name or "Smart Water" in product_name or \
                           "Glaceau Smartwater" in product_name or "Lifewater" in product_name:
                           
                            try:
                                total_cost = float(row[9])
                                qty = float(row[8])
                            except ValueError:
                                total_cost = 0.0
                                qty = 0.0
                                
                            relevant_data.append({
                                'date': dt.date(),
                                'product': product_name,
                                'type': shrink_type,
                                'cost': total_cost,
                                'qty': qty
                            })
                            product_names.add(product_name)
                            
                except IndexError:
                    continue
                    
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print(f"Found products: {product_names}")
    print(f"Total relevant records: {len(relevant_data)}")
    
    # Aggregation
    daily_stats = defaultdict(lambda: {'cost': 0.0, 'qty': 0.0})
    all_dates_seen = set()
    
    # Check date range of entire file just in case
    try:
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) > 2:
                    try:
                        all_dates_seen.add(row[2])
                    except: pass
    except: pass
    
    if all_dates_seen:
        dates = [d for d in all_dates_seen if d.startswith('2025')]
        dates.sort()
        if dates:
            print(f"File contains dates from {dates[0]} to {dates[-1]}")

    for item in relevant_data:
        day = item['date']
        daily_stats[day]['cost'] += item['cost']
        daily_stats[day]['qty'] += item['qty']
        
    sorted_days = sorted(daily_stats.keys())
    
    print("\nDaily Waste Trend (Life Water & Smart Water):")
    print(f"{'Date':<12} | {'Qty':<10} | {'Cost ($)':<10}")
    print("-" * 40)
    
    for day in sorted_days:
        stats = daily_stats[day]
        print(f"{day}   | {stats['qty']:<10.1f} | ${stats['cost']:<10.2f}")

if __name__ == "__main__":
    analyze_waste()
