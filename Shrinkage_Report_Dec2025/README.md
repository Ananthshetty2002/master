# Shrinkage Analysis & Network Report - December 2025

## 📊 Project Overview
This repository contains the data and final analysis for the December 2025 Shrinkage Detection project. The goal of this analysis was to identify discrepancies between inventory levels and sales/adjustments across 193 micro-market locations, highlighting critical areas of loss ("shrinkage").

**Report Generated:** January 15, 2026
**Analysis Period:** December 3, 2025 – December 31, 2025

## 📂 Data Structure
The source data used to generate the final verified report (`final.json`) is organized as follows:

```
/data
├── inventory/           # Stock snapshots (Start vs. End)
│   ├── start_inventory.csv     # Open stock (Dec 3)
│   ├── end_inventory.csv       # Closing stock (Dec 19/20)
│   └── late_dec_inventory.csv  # Late Dec stock checks
├── sales/               # Transaction logs (Sales History)
│   ├── sales_log_1.csv         # Batch 1 (Dec 23)
│   └── sales_log_2.csv         # Batch 2 (Dec 23)
├── adjustments/         # Corrections
│   └── adjustments_log.csv     # Manual pilot adjustments (spoilage/waste)
└── products/            # Reference Data
    ├── rank_report.csv         # Product ranking
    └── product_trans_*.csv     # Product ID-to-Name mapping sources
```

## 🔍 Methodology
The analysis follows a standard shrinkage detection formula:

1.  **Expected Inventory** = `Start Inventory` - `Sales` - `Recorded Spoilage/Adjustments`
2.  **Shrinkage** = `Expected Inventory` - `Actual End Inventory`
3.  **Filtration**:
    *   Negative shrinkage (gain) is clipped to 0.
    *   "Ghost" items (no sales, no stock) are removed.

## 📈 Key Findings
*(Summary based on final.json)*
*   **Total Sites Analyzed**: 193
*   **Identified Critical Sites**: 0 (in this batch context)
*   **Total Financial Impact**: ~$41,677
*   **Top Contributing Factors**:
    *   Unrecorded consumption.
    *   Potential mis-scans or theft of high-value items (e.g., Electronics, Premium Beverages).

## 🚀 How to Use
1.  **Reproduce Analysis**: detailed scripts (e.g., `shrinkage_detector_v2.py`) use the files in `/data` as input.
2.  **Verify Results**: Compare `end_inventory.csv` against the calculated expected values derived from `start_inventory.csv` and `sales_log_*.csv`.

---
*Confidential Data - Internal Use Only*
