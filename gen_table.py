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

# Load Rancho Products
with open("c:\\Users\\IV-UDP-DT-0122\\Downloads\\shrinkage\\n8n_consolidated_report.json", "r", encoding='utf-8') as f:
    report = json.load(f)

rancho_products = []
for loc in report["location_ranking"]:
    if loc["location"] == "HIE - Rancho Cucamonga Market":
        rancho_products = loc["shrinkage_products"]
        break

# Generate Markdown Table
table = "| Product ID | Product Name | Qty | Unit Price | Total Value |\n"
table += "| :--- | :--- | :--- | :--- | :--- |\n"
total_val = 0
for prod in rancho_products:
    sku = prod["product_id"]
    name = prod["product_name"]
    qty = prod["shrinkage_qty"]
    price = prices.get(sku, 0)
    val = qty * price
    total_val += val
    if val > 0:
        table += f"| {sku} | {name} | {qty} | ${price:.2f} | ${val:.2f} |\n"

table += f"| **TOTAL** | | **716** | | **${total_val:.2f}** |\n"

with open("c:\\Users\\IV-UDP-DT-0122\\Downloads\\shrinkage\\rancho_product_table.md", "w", encoding='utf-8') as f:
    f.write(table)

print("Product table generated.")
