import pandas as pd

# ----- BASELINE: Sep–Nov for Westin -----
base = pd.read_csv("Overage Spoilage Shrinkage ReportUltraserv Automated Services 2025-12-04.csv")
base = base.rename(columns={"Micromarket": "Site", "Total Product cost": "TotalCost"})
base = base[base["Site"] == "The Westin Long Beach"]

days_base = base["Date"].nunique()
baseline_per_day = base["TotalCost"].sum() / days_base

# ----- PILOT: logged days for Westin -----
# Baseline/day (already works)
# ...

# Pilot/day AFTER 5+ dates
import pandas as pd
from pathlib import Path

log = pd.read_csv("pilot_shrink_log.csv")

log = log.rename(columns={"Micromarket": "Site", "Total Product cost": "TotalCost"})
log = log.loc[:, ~log.columns.duplicated()]

# keep ONLY rows where Change Type mentions Shrink or Spoilage
log = log[log["Change Type"].str.contains("Shrink|Spoilage", case=False, na=False)]

log.to_csv("pilot_shrink_log_clean.csv", index=False)
print("Clean rows:", len(log))
print(log[["Date", "Site", "Change Type", "TotalCost"]].head())

# baseline_per_day already computed earlier

clean = pd.read_csv("pilot_shrink_log_clean.csv")
clean = clean[clean["Site"] == "The Westin Long Beach"]

days_pilot = clean["Date"].nunique()
pilot_per_day = clean["TotalCost"].sum() / days_pilot

print("Baseline/day (true shrink):", baseline_per_day)
print("Pilot/day (true shrink):", pilot_per_day)
