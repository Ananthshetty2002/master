import json

def audit_report(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    results = []
    results.append(f"Main Keys: {list(data.keys())}")
    
    location_ranking = data.get('location_ranking', [])
    results.append(f"Total Locations in ranking: {len(location_ranking)}")
    
    zero_shrinkage_found = any(
        prod.get('shrinkage_qty', 0) == 0 
        for loc in location_ranking 
        for prod in loc.get('shrinkage_products', [])
    )
    results.append(f"Zero Shrinkage Products Found in ranking: {zero_shrinkage_found}")
    
    missing_loc_value = any('total_shrinkage_value' not in loc for loc in location_ranking)
    results.append(f"Locations Missing total_shrinkage_value in ranking: {missing_loc_value}")
    
    # Check overall_shrinkage_summary
    summary_data = {}
    for segment in data.get('n8n_questions', []):
        if segment.get('id') == 'overall_shrinkage_summary':
            summary_data = segment.get('result_data', {})
            break
    
    if summary_data:
        top_locs = summary_data.get('top_locations', [])
        results.append(f"Top 1 Location in Summary: {top_locs[0].get('location')} - Qty: {top_locs[0].get('total_shrinkage_qty')}, Value: ${top_locs[0].get('total_shrinkage_value')}")
    else:
        results.append("overall_shrinkage_summary NOT FOUND")

    with open('audit_results.txt', 'w') as f:
        f.write('\n'.join(results))

if __name__ == "__main__":
    audit_report(r'c:\Users\IV-UDP-DT-0122\Downloads\shrinkage\n8n_consolidated_report_final_fixed.json')
