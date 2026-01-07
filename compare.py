import pandas as pd
from pathlib import Path

# change this filename each day
today = pd.read_csv("Overage Spoilage Shrinkage ReportUltraserv Automated Services 2025-12-04.csv")
today["Date"] = "2025-12-08"

today = today.rename(columns={"Micromarket": "Site", "Total Product cost": "TotalCost"})
pilot_sites = ["Bldg 80 Micro", "The Westin Long Beach", "Brandt Russell Guthrie"]
today = today[today["Site"].isin(pilot_sites)]

log_path = Path("pilot_shrink_log.csv")
if log_path.exists():
    log = pd.read_csv(log_path)
    log = pd.concat([log, today], ignore_index=True)
else:
    log = today

log.to_csv("pilot_shrink_log.csv", index=False)

# NEW: show a quick check
print("Rows added today:", len(today))
print("Total rows in log:", len(log))
print(log)
