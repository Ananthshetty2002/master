import json
import os

def slim_master_report():
    input_path = 'full_network_master_report.json'
    output_path = 'network_agent_insights.json'
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r') as f:
        master_data = json.load(f)

    slim_micromarkets = []
    for item in master_data.get('all_micromarket_data', []):
        # Extract product names only for top_shrinkage_products
        top_products = [p['product_name'] for p in item.get('shrinkage_alerts', {}).get('top_products_at_risk', [])]
        
        slim_entry = {
            "name": item.get('micromarket'),
            "shrinkage_total_qty": item.get('shrinkage_alerts', {}).get('total_lost_qty'),
            "shrinkage_status": item.get('shrinkage_alerts', {}).get('status'),
            "top_shrinkage_products": top_products,
            "spoilage_items": item.get('spoilage_fefo_alerts', []),
            "site_action_summary": item.get('site_action_summary')
        }
        slim_micromarkets.append(slim_entry)

    final_slim_report = {
        "report_title": "Network Shrinkage & Spoilage Alerts - All Micromarkets",
        "report_date": master_data.get('report_metadata', {}).get('date'),
        "total_sites": master_data.get('report_metadata', {}).get('total_sites'),
        "micromarkets": slim_micromarkets
    }

    with open(output_path, 'w') as f:
        json.dump(final_slim_report, f, indent=2)
    
    print(f"Successfully generated slimmed report for {len(slim_micromarkets)} sites.")

if __name__ == "__main__":
    slim_master_report()
