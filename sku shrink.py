import pandas as pd

# 1. Load combined Sep+Oct+Nov overage/shrink file
df = pd.read_csv("Overage Spoilage Shrinkage ReportUltraserv Automated Services 2025-12-04.csv")

# Rename to simpler names
df = df.rename(columns={
    "Micromarket": "Site",
    "User Name": "Operator",
    "Change Type": "ChangeType",
    "Quantity": "Qty",
    "Total Product cost": "TotalCost"
})

pilot_sites = ["Bldg 80 Micro", "The Westin Long Beach", "Brandt Russell Guthrie"]

# 2. Split into EXCESS (overage) and NEED (shrink/stockout proxy)
excess = df[(df["Site"].isin(pilot_sites)) &
            (df["ChangeType"].str.contains("Overage", case=False, na=False))]

need = df[(df["Site"].isin(pilot_sites)) &
          (df["ChangeType"].str.contains("Shrink", case=False, na=False))]

# Aggregate by Site + Product
excess_agg = (excess.groupby(["Site", "Product Code", "Product"])["Qty"]
                     .sum().reset_index().rename(columns={"Qty": "Excess_Qty"}))

need_agg = (need.groupby(["Site", "Product Code", "Product"])["Qty"]
                   .sum().reset_index().rename(columns={"Qty": "Need_Qty"}))

# 3. Simple matching: from excess sites to need sites per product
transfers = []

for _, ex in excess_agg.iterrows():
    prod = ex["Product Code"]
    # All sites that need this product
    needs_prod = need_agg[need_agg["Product Code"] == prod]
    if needs_prod.empty:
        continue

    available = ex["Excess_Qty"]
    for _, nd in needs_prod.iterrows():
        if available <= 0:
            break
        qty_move = min(available, nd["Need_Qty"])
        transfers.append({
            "SKU": prod,
            "Product": ex["Product"],
            "From": ex["Site"],
            "To": nd["Site"],
            "Qty": qty_move
        })
        available -= qty_move

transfer_df = pd.DataFrame(transfers)
print(transfer_df)
transfer_df.to_csv("transfer_day1_all.csv", index=False)
import pandas as pd
transfers = pd.read_csv("transfer_day1_all.csv")
print("TODAY'S MILK-RUN ROUTE (Top 10):")
print(transfers.head(10)[["From", "To", "SKU", "Product", "Qty"]])

