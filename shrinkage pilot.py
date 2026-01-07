import pandas as pd

df = pd.read_csv("Overage Spoilage Shrinkage ReportUltraserv Automated Services 2025-12-04.csv")

# Standardize columns
df = df.rename(columns={
    "Micromarket": "Site",
    "Total Product cost": "TotalCost"
})

# Keep only true shrink/spoilage
df = df[df["Change Type"].str.contains("Shrink|Spoilage", case=False, na=False)]

# Build operator risk across ALL sites
risk = (
    df.groupby(["Site", "User Name"], as_index=False)
      .agg(
          Total_shrink_units=("Quantity", "sum"),
          Total_shrink_value=("TotalCost", "sum"),
      )
)

# Add simple risk bands
risk["Risk_band"] = pd.qcut(
    risk["Total_shrink_value"],
    q=[0, 0.6, 0.85, 1.0],  # LOW 60%, MED next 25%, HIGH top 15%
    labels=["LOW", "MED", "HIGH"]
)

risk.to_csv("risk_scores_day1.csv", index=False)
print("Saved risk_scores_day1.csv with", len(risk), "operators")
import pandas as pd

risk = pd.read_csv("risk_scores_day1.csv")

pilot_sites = ["The Westin Long Beach", "Bldg 80 Micro", "Brandt Russell Guthrie"]

risk_pilot = (
    risk[risk["Site"].isin(pilot_sites)]
    .sort_values("Total_shrink_value", ascending=False)
)

# Save one manager sheet
risk_pilot.to_csv("audit_sheet_pilot_sites.csv", index=False)

# Optional: separate files
high = risk_pilot[risk_pilot["Risk_band"] == "HIGH"]
med  = risk_pilot[risk_pilot["Risk_band"] == "MED"]
low  = risk_pilot[risk_pilot["Risk_band"] == "LOW"]

high.to_csv("audit_high_today.csv", index=False)
med.to_csv("audit_med_today.csv", index=False)
low.to_csv("audit_low_today.csv", index=False)
