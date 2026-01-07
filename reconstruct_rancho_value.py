import csv
import json

# 1. Load Prices from Product Rank Report
prices = {}
with open("c:\\Users\\IV-UDP-DT-0122\\Downloads\\shrinkage\\Product Rank Report (1).csv", "r", encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f)
    # Skip preamble lines
    for _ in range(8):
        next(reader)
    headers = next(reader)
    # Rank,Item Description,Item #,Category,Quantity,Quantity(Previous period),Difference,Status,Amount
    for row in reader:
        if len(row) >= 9:
            try:
                sku = row[2]
                qty = float(row[4])
                amount = float(row[8])
                if qty != 0:
                    prices[sku] = amount / qty
            except:
                continue

# 2. Load Rancho Cucamonga Products from n8n_consolidated_report.json
with open("c:\\Users\\IV-UDP-DT-0122\\Downloads\\shrinkage\\n8n_consolidated_report.json", "r", encoding='utf-8') as f:
    report = json.load(f)

rancho_products = []
for loc in report["location_ranking"]:
    if loc["location"] == "HIE - Rancho Cucamonga Market":
        rancho_products = loc["shrinkage_products"]
        break

# 3. Calculate Total Value
total_calculated_value = 0
total_qty = 0
print(f"{'Product ID':<10} {'Qty':<5} {'Price':<10} {'Value':<10} {'Name'}")
for prod in rancho_products:
    sku = prod["product_id"]
    qty = prod["shrinkage_qty"]
    name = prod["product_name"]
    price = prices.get(sku, 0)
    val = qty * price
    total_calculated_value += val
    total_qty += qty
    if val > 0:
        print(f"{sku:<10} {qty:<5} {price:<10.2f} {val:<10.2f} {name}")

print("-" * 50)
print(f"Total Qty: {total_qty}")
print(f"Total Calculated Value: {total_calculated_value:.2f}")
