import json
import os
import pandas as pd
from datetime import datetime, timedelta

# Constants
JSON_FILE = 'n8n_consolidated_report_final.json'
INPUT_REPORT = 'n8n_consolidated_report_final.json'
OUTPUT_REPORT = 'n8n_consolidated_report_final.json'

# ROI Assumptions
TRANSFER_COST_PER_UNIT = 1.0  # Estimated cost to move one unit
MIN_ROI_TARGET = 2.0          # Target > 200% ROI
MIN_TRANSFER_QTY = 3          # Minimum units to make a transfer worth considering

def load_report(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_report(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def run_analysis():
    print("Loading data for ROI analysis...")
    
    # 1. Load Start Inventory (Dec 3) - Source of Truth for Product List
    print("Loading Start Inventory...")
    try:
        df_start = pd.read_csv('CSVStock Analysis Report.csv', skiprows=8, encoding='utf-8-sig', low_memory=False)
        df_start.columns = [c.strip() for c in df_start.columns]
        df_start = df_start.rename(columns={'Customer/Location': 'location', 'Product': 'product_name', 'Total Quantity': 'start_qty'})
        # Filter purely numeric start_qty
        df_start['start_qty'] = pd.to_numeric(df_start['start_qty'], errors='coerce').fillna(0)
    except Exception as e:
        print(f"Error loading start inventory: {e}")
        return

    # 2. Load Sales (Dec 3-31)
    print("Loading Sales Data...")
    sales_files = ['Transaction List Report 12.23.2025 11-28 AM.csv', 'Transaction List Report 12.23.2025 11-36 AM.csv']
    all_sales = []
    
    # Generate name mapping from sales files since they have codes
    product_map = {} 
    
    for f in sales_files:
        try:
            df = pd.read_csv(f, skiprows=9, encoding='utf-8-sig', low_memory=False)
            df.columns = [c.strip() for c in df.columns]
            df = df.rename(columns={'Micro Market': 'location', 'Product Desc': 'product_name', 'Quantity': 'sales_units', 'Sales': 'sales_value', 'Product Code': 'product_id'})
            
            # Update product map (Name -> ID)
            for _, row in df[['product_name', 'product_id']].dropna().drop_duplicates().iterrows():
                product_map[row['product_name']] = row['product_id']
                
            all_sales.append(df)
        except Exception as e:
            print(f"Error loading {f}: {e}")

    if not all_sales:
        print("No sales data loaded.")
        return

    df_sales = pd.concat(all_sales)
    df_sales['sales_units'] = pd.to_numeric(df_sales['sales_units'], errors='coerce').fillna(0)
    df_sales['sales_value'] = pd.to_numeric(df_sales['sales_value'], errors='coerce').fillna(0)
    
    # Aggregate sales by location+product
    sales_agg = df_sales.groupby(['location', 'product_name']).agg({
        'sales_units': 'sum', 
        'sales_value': 'sum'
    }).reset_index()
    
    sales_agg['unit_price'] = sales_agg['sales_value'] / sales_agg['sales_units'].replace(0, 1)

    # 3. Calculate Derived Inventory
    # Merge Start Inventory with Sales
    print("Calculating Derived Inventory...")
    inventory_status = pd.merge(df_start, sales_agg, on=['location', 'product_name'], how='left')
    inventory_status['sales_units'] = inventory_status['sales_units'].fillna(0)
    inventory_status['unit_price'] = inventory_status['unit_price'].fillna(0)
    
    # Calculated Current = Start - Sales
    inventory_status['current_qty'] = inventory_status['start_qty'] - inventory_status['sales_units']
    
    # Map IDs
    inventory_status['product_id'] = inventory_status['product_name'].map(product_map).fillna('UNKNOWN')

    # 4. Identify Opportunities
    sources = []
    destinations = []
    
    print("Identifying transfer opportunities...")
    
    for _, row in inventory_status.iterrows():
        loc = row['location']
        prod = row['product_name']
        qty = float(row['current_qty'])
        sales = float(row['sales_units'])
        price = float(row['unit_price'])
        # If price is 0 (no sales), try to infer? Or skip.
        if price == 0 and sales == 0:
            continue 

        p_id = row['product_id']
        
        # Source Criteria:
        # High Stock: > 10 units
        # Low Velocity: Stock > 3x Sales (sitting inventory) OR Sales < 2 (dead stock)
        # Ensure we have at least 10 units to give
        if qty > 10:
            if sales < 3 or qty > (sales * 3):
                excess = qty - max(5, sales * 1.5) # Leave buffer
                if excess >= MIN_TRANSFER_QTY:
                    sources.append({
                        'location': loc,
                        'product_name': prod,
                        'product_id': p_id,
                        'available_qty': int(excess),
                        'current_stock': int(qty),
                        'sales_velocity': sales
                    })
        
        # Destination Criteria:
        # Low Stock: < 5 units (Calculated)
        # High Velocity: Sales > 5 (proven demand)
        # Stockout Risk: Calculated <= 0 means likely stockout
        if qty < 5 and sales >= 5:
            needed = 15 - max(0, qty)
            if needed >= MIN_TRANSFER_QTY:
                destinations.append({
                    'location': loc,
                    'product_name': prod,
                    'product_id': p_id,
                    'needed_qty': int(needed),
                    'current_stock': int(qty),
                    'sales_velocity': sales,
                    'unit_price': price
                })

    print(f"Found {len(sources)} sources and {len(destinations)} destinations.")
    
    # 5. Matching logic
    sources_by_prod = {}
    for s in sources:
        sources_by_prod.setdefault(s['product_name'], []).append(s)

    transfer_recs = []
    
    for dest in destinations:
        p_name = dest['product_name']
        potential_srcs = sources_by_prod.get(p_name, [])
        potential_srcs.sort(key=lambda x: x['available_qty'], reverse=True)
        
        for src in potential_srcs:
            if src['location'] == dest['location']: continue
            
            xfer_qty = min(dest['needed_qty'], src['available_qty'])
            if xfer_qty < MIN_TRANSFER_QTY: continue
            
            revenue = xfer_qty * dest['unit_price']
            cost = xfer_qty * TRANSFER_COST_PER_UNIT
            
            if cost > 0:
                roi = ((revenue - cost) / cost) * 100
            else:
                roi = 0
                
            if roi >= 200:
                transfer_recs.append({
                    'product_name': p_name,
                    'product_id': dest['product_id'],
                    'source_site': src['location'],
                    'destination_site': dest['location'],
                    'transfer_qty': int(xfer_qty),
                    'revenue_potential': round(revenue, 2),
                    'transfer_cost': round(cost, 2),
                    'roi_percentage': round(roi, 1),
                    'priority': 'HIGH' if roi > 400 else 'MEDIUM',
                    'date_to_transfer': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'how_fast_to_transfer': 'Urgent (Within 24h)' if roi > 400 else 'Standard (Within 3 Days)',
                    'transfer_route': f"{src['location']} -> {dest['location']}"
                })
                
                src['available_qty'] -= xfer_qty
                if src['available_qty'] < MIN_TRANSFER_QTY:
                    potential_srcs.remove(src)
                break

    print(f"Generated {len(transfer_recs)} recommendations.")

    # 6. Update JSON
    report_data = load_report(INPUT_REPORT)
    report_data['engine_context'] += " Includes Inventory Transfer Optimization analysis (Calculated Inventory)."
    
    out_map = {}
    in_map = {}
    
    for t in transfer_recs:
        out = {
            'product_id': t['product_id'],
            'product_name': t['product_name'],
            'destination_site': t['destination_site'],
            'recommended_transfer_qty': t['transfer_qty'],
            'estimated_roi': t['roi_percentage'],
            'revenue_potential': t['revenue_potential'],
            'priority': t['priority'],
            'date_to_transfer': t['date_to_transfer'],
            'how_fast_to_transfer': t['how_fast_to_transfer'],
            'transfer_route': t['transfer_route']
        }
        out_map.setdefault(t['source_site'], []).append(out)
        
        inb = {
            'product_id': t['product_id'],
            'product_name': t['product_name'],
            'source_site': t['source_site'],
            'recommended_receive_qty': t['transfer_qty'],
            'estimated_revenue': t['revenue_potential'],
            'priority': t['priority'],
            'date_to_transfer': t['date_to_transfer'],
            'how_fast_to_transfer': t['how_fast_to_transfer'],
            'transfer_route': t['transfer_route']
        }
        in_map.setdefault(t['destination_site'], []).append(inb)

    for loc in report_data.get('location_ranking', []):
        lname = loc['location']
        if lname in out_map or lname in in_map:
            loc['transfer_opportunities'] = {}
            if lname in out_map:
                loc['transfer_opportunities']['outbound_suggestions'] = out_map[lname]
            if lname in in_map:
                loc['transfer_opportunities']['inbound_opportunities'] = in_map[lname]
                
    # Network Summary
    top_transfers = sorted(transfer_recs, key=lambda x: x['roi_percentage'], reverse=True)[:20]
    report_data['network_transfer_optimization'] = {
        'total_opportunities': len(transfer_recs),
        'total_revenue_potential': round(sum(t['revenue_potential'] for t in transfer_recs), 2),
        'top_recommendations': top_transfers
    }
    
    save_report(report_data, OUTPUT_REPORT)
    print("Report updated.")

if __name__ == "__main__":
    run_analysis()
