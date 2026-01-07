# shrink_pilot_day1_from_overage_report_v2.py

import pandas as pd

# 1. LOAD ALL MONTHS APPENDED (SEP+OCT+NOV)
df = pd.read_csv("Overage Spoilage Shrinkage ReportUltraserv Automated Services 2025-12-04.csv")

# ---- ADAPT TO YOUR COLUMN NAMES ----
# Rename for convenience
df = df.rename(columns={
    "Micromarket": "Site",
    "User Name": "Operator",
    "Change Type": "ChangeType",
    "Quantity": "Qty",
    "Total Product cost": "TotalCost"
})

# 2. KEEP ONLY PILOT SITES
pilot_sites = ["Bldg 80 Micro", "The Westin Long Beach", "Brandt Russell Guthrie"]
df = df[df["Site"].isin(pilot_sites)]

# 3. FLAG SHRINK / SPOILAGE ROWS
# (Adjust text if your system uses slightly different words)
shrink_mask = df["ChangeType"].str.contains("Shrink", case=False, na=False)
spoil_mask  = df["ChangeType"].str.contains("Spoilage", case=False, na=False)

df["shrink_units"]  = df["Qty"].where(shrink_mask, 0)
df["spoil_units"]   = df["Qty"].where(spoil_mask, 0)
df["shrink_value"]  = df["TotalCost"].where(shrink_mask, 0)
df["spoil_value"]   = df["TotalCost"].where(spoil_mask, 0)

df["total_shrink_units"] = df["shrink_units"] + df["spoil_units"]
df["total_shrink_value"] = df["shrink_value"] + df["spoil_value"]

# 4. GROUP BY SITE + OPERATOR (30‑DAY / 3‑MONTH BASELINE)
baseline = (
    df.groupby(["Site", "Operator"])[["total_shrink_units", "total_shrink_value"]]
    .sum()
    .reset_index()
)

print("BASELINE SHRINK BY SITE & OPERATOR")
print(baseline)

baseline.to_csv("operator_risk_day1.csv", index=False)
