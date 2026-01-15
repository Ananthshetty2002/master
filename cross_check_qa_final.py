import json

def cross_check_qa():
    # 1. Load the Ground Truth (The Re-Fixed Report)
    with open('n8n_consolidated_report_RE-FIXED.json', 'r', encoding='utf-8') as f:
        truth_data = json.load(f)
    
    # Create a lookup for products and locations from Truth
    all_locations = {l['location']: l for l in truth_data['location_ranking']}
    all_products_by_id = {} # (loc, pid) -> product
    for loc, entry in all_locations.items():
        for p in entry['shrinkage_products']:
            all_products_by_id[(loc, p['product_id'])] = p

    # 2. Load the QA Answers
    with open('analyzed_metrics.json', 'r', encoding='utf-8') as f:
        qa_answers = json.load(f)

    print("--- QA CROSS-CHECK REPORT ---")
    
    for insight in qa_answers:
        title = insight.get('location')
        print(f"\nChecking Segment: {title}")
        
        items = insight.get('data', [])
        if not isinstance(items, list):
            # Might be summary info
            # print(f"  Info: {insight}")
            continue
            
        if "Ghost Disappearances" in title:
            # Check if all ghosts in QA have 0 sales in Truth
            mismatch_count = 0
            for item in items[:10]:
                pid = item.get('product_id')
                loc = item.get('location') # Note: this depends on how it's keyed
                # Extract loc from the item if present
                if pid and loc:
                    p_truth = all_products_by_id.get((loc, pid))
                    if p_truth:
                        if p_truth.get('sales_units', 0) > 0:
                            print(f"  [X] FALSE GHOST: {pid} in {loc} has sales={p_truth['sales_units']} in Truth.")
                            mismatch_count += 1
            if mismatch_count == 0:
                print("  [OK] All checked Ghosts have 0 sales in Truth.")

        elif "Top 10 High Shrinkage Items" in title or "Financial Impact" in title:
             # Verify ranking consistency (at least check the top one)
             pass

        # We can add more specific logic for each of the 9 segments here.
        
    print("\nSummary Validation:")
    # Check top-level sums
    json_sum_qty = truth_data['summary_metrics']['total_shrinkage_qty']
    json_sum_val = truth_data['summary_metrics']['total_shrinkage_value']
    print(f"  Truth Overall Qty: {json_sum_qty}")
    print(f"  Truth Overall Value: {json_sum_val}")

if __name__ == "__main__":
    cross_check_qa()
