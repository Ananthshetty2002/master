# Shrinkage Detection Strategy: network_agent_insights.json

## Phase 0: Data Sources 
- **Transaction Report (Sales Register)**: Records all sold units.
- **Inventory Snapshots Report (Stock Analysis)**: Compares opening and closing inventory.
- **Adjustment logs (pilot_shrink_log.csv)**: Records manual adjustments for spoilage, overage, and known shrinkage.
- **Scope**: 193 micromarkets analyzed → 150 identified with active shrinkage.

## Phase 1: Core Formulas 
- **Shrinkage Calculation**: `(Opening Inventory - Sales Units) - Closing Inventory`. 
  - *Constraint*: Negatives are clipped at 0 (only tracking loss).
- **Spoilage Exclusion**: Legitimate disposals/waste are subtracted from the result to isolate unexplained loss.
- **Financial Impact**: Calculated as `Units × Unit Price` (prices from Product Rank reports).

## Final Output: network_agent_insights.json
The final JSON provides high-level alerts and severity rankings for the n8n agent:
- **Rankings**: Sites categorized by severity (CRITICAL, HIGH, MONITOR).
- **Total Loss**: Financial impact per site (e.g., **HIE Rancho: $3,938.43**).
- **Top Theft Items**: Identified by high volume and "Ghost" (zero-sale) patterns (e.g., **Smart Water, Dasani**).

---
*Reference File: network_agent_insights.json*
*Generated: 2025-12-31*
