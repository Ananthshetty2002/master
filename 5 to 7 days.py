import pandas as pd

baseline_site = pd.read_csv("baseline_shrink_sites.csv")
log = pd.read_csv("pilot_shrink_log.csv")

# Standardize columns
log = log.rename(columns={"Micromarket": "Site", "Total Product cost": "TotalCost"})

# If both 'Site' columns exist, keep only one
log = log.loc[:, ~log.columns.duplicated()]   # remove duplicate-named columns

pilot_sites = ["Bldg 80 Micro", "The Westin Long Beach", "Brandt Russell Guthrie"]
log = log[log["Site"].isin(pilot_sites)]

week1_site = (
    log.groupby("Site")["TotalCost"]
    .sum()
    .reset_index()
    .rename(columns={"TotalCost": "Week1_Shrink_Value"})
)

summary = baseline_site.merge(week1_site, on="Site", how="left")
summary["Change_%"] = (1 - summary["Week1_Shrink_Value"] / summary["Baseline_Shrink_Value"]) * 100

print(summary)
summary.to_csv("week1_shrink_summary.csv", index=False)
