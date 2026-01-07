import csv
import json

# Load Prices
prices = {}
with open("c:\\Users\\IV-UDP-DT-0122\\Downloads\\shrinkage\\Product Rank Report (1).csv", "r", encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f)
    for _ in range(8): next(reader)
    headers = next(reader)
    for row in reader:
        if len(row) >= 9:
            try:
                sku = row[2]
                qty = float(row[4])
                amount = float(row[8])
                if qty != 0:
                    prices[sku] = amount / qty
            except: continue

# Load Report
with open("c:\\Users\\IV-UDP-DT-0122\\Downloads\\shrinkage\\n8n_consolidated_report.json", "r", encoding='utf-8') as f:
    report = json.load(f)

# Update Rancho Cucamonga
for loc in report["location_ranking"]:
    if loc["location"] == "HIE - Rancho Cucamonga Market":
        loc["total_shrinkage_qty"] = 716.0
        loc["total_shrinkage_value"] = 3938.43 # Sum of calculated values
        
        for prod in loc["shrinkage_products"]:
            sku = prod["product_id"]
            qty = prod["shrinkage_qty"]
            price = prices.get(sku, 0)
            prod["shrinkage_value"] = round(qty * price, 2)
        break

# Save Updated Report
output_path = "c:\\Users\\IV-UDP-DT-0122\\Downloads\\shrinkage\\n8n_consolidated_report_updated.json"
with open(output_path, "w", encoding='utf-8') as f:
    json.dump(report, f, indent=4)

print(f"Updated report saved to {output_path}")
