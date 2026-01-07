import json
import os

def consolidate_n8n_data():
    print("Consolidating n8n definitions and insight results...")
    try:
        # Load the definitions
        with open('n8n_questions.json', 'r', encoding='utf-8') as f:
            definitions = json.load(f)
            
        # Load the results
        with open('shrinkage_insights.json', 'r', encoding='utf-8') as f:
            results = json.load(f)
            
        # Load the detailed report for location ranking
        site_report = {}
        if os.path.exists('n8n_shrinkage_report_v2.json'):
            with open('n8n_shrinkage_report_v2.json', 'r', encoding='utf-8') as f:
                site_report = json.load(f)
        elif os.path.exists('n8n_shrinkage_report.json'):
            with open('n8n_shrinkage_report.json', 'r', encoding='utf-8') as f:
                site_report = json.load(f)

        # Load product details from minified report
        product_data = []
        if os.path.exists('n8n_shrinkage_report_minified.json'):
            with open('n8n_shrinkage_report_minified.json', 'r', encoding='utf-8') as f:
                minified = json.load(f)
                product_data = minified.get("data", [])
        
        # Group products by location
        location_products = {}
        for row in product_data:
            loc = row.get("location")
            if loc not in location_products:
                location_products[loc] = []
            
            # Keep only essential fields to manage file size
            location_products[loc].append({
                "product_name": row.get("product_name"),
                "product_id": row.get("product_id"),
                "shrinkage_qty": row.get("shrinkage_qty"),
                "shrinkage_value": row.get("shrinkage_value"),
                "sales_units": row.get("sales_units")
            })

        # Get location ranking
        location_ranking = site_report.get("location_ranking", [])
        
        # Add product details to each location in ranking
        for loc_item in location_ranking:
            loc_name = loc_item.get("location")
            products = location_products.get(loc_name, [])
            # Sort products by shrinkage_qty descending (severity)
            products.sort(key=lambda x: x.get("shrinkage_qty", 0), reverse=True)
            loc_item["shrinkage_products"] = products

        # Create consolidated structure
        consolidated = {
            "report_period": results.get("report_period", {}),
            "engine_context": definitions.get("engine_context", ""),
            "location_ranking": location_ranking,
            "insights": [],
            "summary_metrics": results.get("summary_metrics", {})
        }
        
        # Merge each insight definition with its corresponding data
        for insight_def in definitions.get("insights", []):
            insight_id = insight_def['id']
            data = results.get(insight_id, [])
            
            merged_insight = {**insight_def, "result_data": data}
            consolidated["insights"].append(merged_insight)
            
        # Optimize floats to save space
        def round_floats(obj):
            if isinstance(obj, float):
                return round(obj, 2)
            elif isinstance(obj, dict):
                return {k: round_floats(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [round_floats(x) for x in obj]
            return obj
            
        consolidated = round_floats(consolidated)
            
        # Save the master file
        output_file = 'n8n_consolidated_report.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated, f, indent=2)
            
        print(f"Consolidated file saved to {output_file}")
        
    except Exception as e:
        import traceback
        print(f"Error during consolidation: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    consolidate_n8n_data()
