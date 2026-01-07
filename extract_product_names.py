import json

file_path = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage\n8n_consolidated_report_final.json"

try:
    with open(file_path, 'r') as f:
        data = json.load(f)

    unique_products = set()

    # extract from location_ranking -> shrinkage_products
    if "location_ranking" in data:
        for loc in data["location_ranking"]:
            if "shrinkage_products" in loc:
                for prod in loc["shrinkage_products"]:
                    if "product_name" in prod:
                        unique_products.add(prod["product_name"])
    
    # extract from network_transfer_optimization -> top_recommendations
    if "network_transfer_optimization" in data and "top_recommendations" in data["network_transfer_optimization"]:
        for prod in data["network_transfer_optimization"]["top_recommendations"]:
             if "product_name" in prod:
                unique_products.add(prod["product_name"])

    # extract from opportunities within location_ranking
    if "location_ranking" in data:
        for loc in data["location_ranking"]:
            if "transfer_opportunities" in loc:
                if "outbound_suggestions" in loc["transfer_opportunities"]:
                     for prod in loc["transfer_opportunities"]["outbound_suggestions"]:
                        if "product_name" in prod:
                            unique_products.add(prod["product_name"])
                if "inbound_opportunities" in loc["transfer_opportunities"]:
                     for prod in loc["transfer_opportunities"]["inbound_opportunities"]:
                        if "product_name" in prod:
                            unique_products.add(prod["product_name"])


    sorted_products = sorted(list(unique_products))
    
    output_file = "all_unique_products.txt"
    with open(output_file, "w") as f:
        f.write(f"Total Unique Products: {len(sorted_products)}\n\n")
        for p in sorted_products:
            f.write(f"{p}\n")
            
    print(f"Successfully extracted {len(sorted_products)} unique products to {output_file}")
    # Print first 20 for preview
    print("First 20 products:")
    for p in sorted_products[:20]:
        print(f"- {p}")

except Exception as e:
    print(f"Error: {e}")
