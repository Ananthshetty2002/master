import pandas as pd

# 1) Load Sep+Oct+Nov combined report
base = pd.read_csv("Overage Spoilage Shrinkage ReportUltraserv Automated Services 2025-12-04.csv")  # use your real file name

# 2) Standardize column names
base = base.rename(columns={
    "Micromarket": "Site",
    "Total Product cost": "TotalCost"
})

# 3) Keep only pilot sites
pilot_sites = ["Bldg 80 Micro", "The Westin Long Beach", "Brandt Russell Guthrie"]
base = base[base["Site"].isin(pilot_sites)]

# 4) Baseline shrink $ per site
baseline_site = (
    base.groupby("Site")["TotalCost"]
    .sum()
    .reset_index()
    .rename(columns={"TotalCost": "Baseline_Shrink_Value"})
)

print(baseline_site)
baseline_site.to_csv("baseline_shrink_sites.csv", index=False)
