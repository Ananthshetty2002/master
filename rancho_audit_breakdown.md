# Audit Breakdown: HIE – Rancho Cucamonga Market

This document provides a trace of how the "Critical" alert was generated for the Rancho Cucamonga site, mapping the JSON output to the raw source data.

## 1. Overall Shrinkage: 716 Units (CRITICAL)
- **Status**: CRITICAL
- **Source File**: `CSVStock Analysis Report.csv`
- **Data Point**: Line 11019, Column: `Total Quantity`
- **Calculation Logic**: 
  - `Opening Stock (716)` - `Sales Units (0)` - `Adjustments (0)` = **716 Expected**.
  - `Actual End Inventory` = **0**.
  - **Verdict**: Since 100% of the opening stock is unaccounted for, the site is flagged as Critical.

## 2. Top Theft Products
These items are ranked by **Shrinkage Quantity** (the volume of missing units).

| Product Name | Rank | Source Logic |
| :--- | :--- | :--- |
| **Smart Water 20oz** | #1 | Highest individual volume loss (77 units). Zero sales recorded. |
| **Dasani 20oz** | #2 | High volume loss (47 units). Missing from snapshot comparison. |
| **Smart Water 1L** | #3 | High value/volume combination (40 units). |
| **Coke 20oz** | #4 | Core beverage category loss. |
| **Snickers Ice Cream Bar**| #5 | High-velocity item with zero recorded movement. |

## 3. Spoilage Alert: Milk
- **Metric**: 13 Units at Risk
- **Logic**: 
  - **Source**: Inventory database compared against `Today's Date` (Dec 27).
  - **Calculation**: `Expiry (Dec 28)` - `Today (Dec 27)` = **1 day remaining**.
  - **Action**: Automated recommendation to **"Bundle/Discount"** to recover value within the next 24 hours.

## 4. Site Action Summary
> "Audit required for 716.0 missing units. Check expiry for Milk."

- **Derived From**: This is a concatenated string built by the script's decision engine. It triggers the "Audit" message if shrinkage exceeds 100 units and the "Expiry" message if any items appear in the `spoilage_items` array.

---
*Reference Report: network_agent_insights.json*
*Generated: 2025-12-31*
