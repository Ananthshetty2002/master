# Logic & Reasoning: Consolidated Shrinkage Report Insights

This document outlines the specific criteria and business reasoning used to generate the insights in the `n8n_consolidated_report_final_fixed.json` report.

---

## 1. Core Shrinkage Engine
*   **Metric:** Shrinkage Quantity
*   **Formula:** `(Quantity_Start - Sales_Units) - Quantity_End`
*   **Logic:** This is the standard retail formula. If the ending count is lower than it "ought" to be (Start minus Sales), the difference is **Shrinkage** (unexplained loss).
*   **Reasoning:** To identify exactly how many physical units have disappeared without being paid for.

---

## 2. Unexpected Gains (Negative Shrink)
*   **Severity:** Low
*   **Criteria:** `Quantity_End > (Quantity_Start - Sales_Units)` (Result is a negative number).
*   **Reasoning:** It is physically impossible to have more items than you started with unless more were added. 
    *   **Meaning:** This identifies **Administrative Errors**: unrecorded deliveries, incorrect previous audits, or staff "finding" items they missed last time.

---

## 3. Waste Analysis (Spoilage)
*   **Severity:** Medium
*   **Criteria:** Data pulled from `pilot_shrink_log.csv` (Adjustment Logs).
*   **Reasoning:** This separates "Authorized Loss" (e.g., throwing away an expired sandwich) from "Unexplained Loss" (Theft). 
    *   **Insight:** Highlights fresh food categories (Wraps, Salads) where ordering too much leads to high expiration costs.

---

## 4. Staff Risk & Escalation
*   **Severity:** High
*   **Criteria:** Aggregates `total_shrinkage_value` from the locations assigned to specific staff names.
*   **Reasoning:** This is **not an accusation of theft**, but an indicator of **oversight risk**. 
    *   **Insight:** If a specific manager or auditor's sites consistently show the highest losses in the network, it suggests a need for better monitoring procedures or training at those specific sites.

---

## 5. Overall Shrinkage Summary
*   **Severity:** Critical
*   **Criteria:** Top 10 ranking by `total_shrinkage_value` across all locations and products.
*   **Reasoning:** To prevent "data overload" for senior leadership.
    *   **Insight:** Ensures that the top 5% of sites causing 80% of the financial loss receive immediate attention and audit priority.

---

## 6. Par Level Recommendations
*   **Severity:** Medium
*   **Criteria:** `Current_Par` vs. `Avg_Weekly_Sales`. Triggered when `Par` is significantly higher (e.g., 5-10x) than actual sales.
*   **Reasoning:** Keeping 100 sodas on a shelf when only 2 sell per week increases the "Surface Area" for theft.
    *   **Insight:** Recommends "lean" inventory levels. Reducing the amount of stock on the shelf directly reduces the maximum amount that can be stolen at one time.

---

## 7. Network Transfer Optimization
*   **Severity:** Actionable
*   **Criteria:** High Sales/Low Stock at Destination + Zero Sales/High Stock at Source + High Gross Margin.
*   **Reasoning:** This is a **Recovery Insight**. 
    *   **ROI Calculation:** `(Potential Revenue - Logistic Cost) / Logistic Cost`. 
    *   **Goal:** Instead of declaring "dead stock" a loss, move it to a site where people actually want to buy it, effectively turning potential waste into cash.
