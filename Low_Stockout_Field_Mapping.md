# Low Stockout Analysis - Data Mapping

This document details the mapping between the `Product Transaction Report.csv` fields and the data points used to generate the `Low_Stockout_Analysis.pdf`.

## Field Mapping

### 1. Trans.# (Transaction Number)
*   **CSV Column:** `Trans.#`
*   **Report Data:** **Store Location** (e.g., "Travelodge Commerce")
*   **Usage:** Extracts the Store Location.
*   **Reason:** The CSV contains entries like `Travelodge Commerce Market/OUT...` within this column, which directly matches the locations cited in the report.

### 2. Product Description (or Product Code)
*   **CSV Column:** `Product Description`
*   **Report Data:** **Item Name** (e.g., "Coke (20oz)")
*   **Usage:** Identifies the specific product being analyzed.

### 3. Qty
*   **CSV Column:** `Qty`
*   **Report Data:** **Sales Velocity** and **Stock Level**
*   **Usage:**
    *   **Sales Velocity:** Calculated by summing the `Qty` of sales transactions over a specific period (e.g., "sells 45 times a week").
    *   **Stock Level:** Calculated by summing all historical In/Out `Qty` movements to determine the current balance (e.g., "3 bottles left").

### 4. Trans.Date
*   **CSV Column:** `Trans.Date`
*   **Report Data:** **Time Period**
*   **Usage:** Used to filter data for weekly sales rate calculations and to identify the recency of stock movements.

### 5. Transfer Type
*   **CSV Column:** `Transfer Type`
*   **Report Data:** **Transaction Category**
*   **Usage:** Distinguishes between Sales and Stock movements:
    *   **Sale:** Rows where Transfer Type is `"Transfer - Recept"` (often accompanied by "OUT" in the `Trans.#` or `Location`).
    *   **Inventory Changes:** Rows where Transfer Type is `"Quantity Adjustment"` or `"Purchase"`.
