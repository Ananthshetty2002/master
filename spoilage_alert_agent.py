import pandas as pd
import json
from datetime import datetime, timedelta
import os

class SpoilageAlertAgent:
    def __init__(self, inventory_csv, sales_csv=None, current_date=None):
        self.inventory_df = pd.read_csv(inventory_csv)
        self.current_date = pd.to_datetime(current_date) if current_date else pd.to_datetime(datetime.now().date())
        
        # Load or mock sales velocity (7-day average)
        if sales_csv and os.path.exists(sales_csv):
            # In a real scenario, we'd aggregate 7-day sales from the transaction logs
            # Here, we'll assume a simplified format or use a fallback
            try:
                self.sales_df = pd.read_csv(sales_csv)
            except:
                self.sales_df = self._generate_mock_velocity()
        else:
            self.sales_df = self._generate_mock_velocity()

    def _generate_mock_velocity(self):
        """Generates mock 7-day sales velocity data."""
        data = [
            {'location': 'LOC001', 'product_id': 'PC10726', 'daily_velocity': 2.5}, # Sells 2.5/day
            {'location': 'LOC001', 'product_id': 'PC10243', 'daily_velocity': 0.5}, # Sells 0.5/day (Slow)
            {'location': 'LOC001', 'product_id': 'PC10555', 'daily_velocity': 0.2}, # Sells 0.2/day (Very Slow)
            {'location': 'LOC002', 'product_id': 'PC10726', 'daily_velocity': 5.0}, # Sells 5/day (Fast)
            {'location': 'LOC003', 'product_id': 'PC10555', 'daily_velocity': 1.0}, # Sells 1/day (Fast)
            {'location': 'LOC005', 'product_id': 'PC10726', 'daily_velocity': 0.1}, # Sells 0.1/day (Very Slow)
            {'location': 'LOC005', 'product_id': 'PC10243', 'daily_velocity': 8.0}, # Sells 8/day (Very Fast)
        ]
        return pd.DataFrame(data)

    def analyze(self):
        # 1. Prepare Data
        self.inventory_df['expiry_date'] = pd.to_datetime(self.inventory_df['expiry_date'])
        self.inventory_df['days_to_expiry'] = (self.inventory_df['expiry_date'] - self.current_date).dt.days
        
        # Merge with velocity
        merged = pd.merge(self.inventory_df, self.sales_df, on=['location', 'product_id'], how='left')
        merged['daily_velocity'] = merged['daily_velocity'].fillna(0)
        
        # 2. Identify Risks
        # Risk: Stock Qty > (Daily Velocity * Days to Expiry)
        # Essentially: We have more than we can sell before it dies.
        merged['expected_sales_before_expiry'] = merged['daily_velocity'] * merged['days_to_expiry']
        merged['potential_spoilage_qty'] = (merged['stock_qty'] - merged['expected_sales_before_expiry']).clip(lower=0)
        
        # Filter for items with actual risk (expiring soon or high potential spoilage)
        risky_items = merged[((merged['days_to_expiry'] <= 7) & (merged['stock_qty'] > 0)) | (merged['potential_spoilage_qty'] > 0)].copy()
        
        # 3. Suggest Transfers
        transfer_suggestions = []
        for idx, row in risky_items[risky_items['potential_spoilage_qty'] > 0].iterrows():
            # Find locations that need this product (high velocity, low stock)
            potential_targets = merged[
                (merged['product_id'] == row['product_id']) & 
                (merged['location'] != row['location']) &
                (merged['daily_velocity'] > row['daily_velocity'])
            ].sort_values(by='daily_velocity', ascending=False)
            
            if not potential_targets.empty:
                target = potential_targets.iloc[0]
                transfer_suggestions.append({
                    'product_name': row['product_name'],
                    'qty': int(row['potential_spoilage_qty']),
                    'expiry': row['expiry_date'].strftime('%m/%d'),
                    'source': row['location'],
                    'target': target['location'],
                    'reason': f"Slow mover at {row['location']} ({row['daily_velocity']}/day) vs Fast at {target['location']} ({target['daily_velocity']}/day)"
                })

        # 4. Suggest Bundling (for OpenAI)
        # Convert Timestamps to strings for JSON serialization
        risky_items_json = risky_items.copy()
        date_cols = risky_items_json.select_dtypes(include=['datetime64']).columns
        for col in date_cols:
            risky_items_json[col] = risky_items_json[col].dt.strftime('%Y-%m-%d')
            
        bundling_candidates = risky_items_json[risky_items_json['potential_spoilage_qty'] > 0].to_dict(orient='records')

        return {
            'current_date': self.current_date.strftime('%Y-%m-%d'),
            'risky_items': risky_items_json.sort_values(by='days_to_expiry').to_dict(orient='records'),
            'transfers': transfer_suggestions,
            'bundling_prompt_data': bundling_candidates
        }

if __name__ == "__main__":
    # Simulate current date as Dec 27, 2025
    agent = SpoilageAlertAgent(
        inventory_csv='mock_inventory_expiry.csv', 
        current_date='2025-12-27'
    )
    report = agent.analyze()
    
    with open('spoilage_report.json', 'w') as f:
        json.dump(report, f, indent=2)
        
    print("\n--- Spoilage Alert Analysis ---")
    for t in report['transfers']:
        print(f"Transfer {t['qty']} {t['product_name']} (exp {t['expiry']}) from {t['source']} -> {t['target']}")
    
    if not report['transfers']:
        print("No high-value transfers found.")
