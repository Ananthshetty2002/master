import csv
import json

# Load Prices from both reports
prices = {}
def load_prices(path, skip=0):
    with open(path, "r", encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        for _ in range(skip): next(reader)
        try:
            headers = next(reader)
        except StopIteration:
            return
        for row in reader:
            if len(row) >= 9:
                try:
                    sku = row[2].strip()
                    qty = float(row[4])
                    amount = float(row[8])
                    if qty != 0:
                        prices[sku] = amount / qty
                except: continue

load_prices("c:\\Users\\IV-UDP-DT-0122\\Downloads\\shrinkage\\Product Rank Report (1).csv", 8)
load_prices("c:\\Users\\IV-UDP-DT-0122\\Downloads\\shrinkage\\ProductRankReportCSV.csv", 0)

# Load Rancho Products
with open("c:\\Users\\IV-UDP-DT-0122\\Downloads\\shrinkage\\n8n_consolidated_report.json", "r", encoding='utf-8') as f:
    report = json.load(f)

rancho_products = []
for loc in report["location_ranking"]:
    if loc["location"] == "HIE - Rancho Cucamonga Market":
        rancho_products = loc["shrinkage_products"]
        break

total_val = 0
total_qty = 0
print(f"{'SKU':<10} {'Qty':<10} {'Price':<10} {'Value':<10} {'Name'}")
for prod in rancho_products:
    sku = prod["product_id"].strip()
    qty = prod["shrinkage_qty"]
    name = prod["product_name"]
    price = prices.get(sku, 0)
    val = qty * price
    total_val += val
    total_qty += qty
    print(f"{sku:<10} {qty:<10.1f} {price:<10.2f} {val:<10.2f} {name}")

print("-" * 60)
print(f"Grand Total Qty: {total_qty}")
print(f"Grand Total Value: {total_val:.2f}")
