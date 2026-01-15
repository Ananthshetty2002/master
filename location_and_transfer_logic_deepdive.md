# Deep Dive: Location, Shrinkage & Transfer Logic

This document explains the **Criteria**, **Reasoning**, and **Insights** for every field used in the consolidated report, specifically focusing on Location performance and Transfer optimization.

---

## 1. Location & Shrinkage Performance
These fields measure the physical and financial "health" of a specific market.

| Field | Criteria (How it's calculated) | Reasoning (Why it matters) | Insight Provided |
| :--- | :--- | :--- | :--- |
| **`location`** | The designated "Reporting Hub" or Management Office. | Ensures a clear line of accountability for regional managers. | Identifies who is responsible for fixing high-loss areas. |
| **`total_shrinkage_qty`** | `(Opening + Restock) - (Sales + Adjustments + Closing)`. | Measures the physical volume of missing products. | Reveals the scale of the theft or scanning problem. |
| **`shrinkage_percentage`** | `(Total Shrinkage Qty / Total Start Qty) * 100`. | **Derived Metric:** Normalizes data so large and small sites can be compared fairly. | A 100% loss at a site like Rancho Cucamonga indicates a "Total Wipeout" of inventory. |
| **`total_shrinkage_value`** | `Sum(Units Lost × Unit Price)`. | Converts physical loss into a financial "bottom line" impact. | Justifies the cost of adding security or performing an audit. |
| **`dates` (Report Period)** | Dec 17 - Dec 31, 2025. | Defines the specific "window" of time being analyzed. | Narrowing dates helps pinpoint when specific theft patterns started. |

---

## 1.5. Actual Data Examples (Top Locations)
Based on the `n8n_consolidated_report_final_fixed.json`, here are the calculated percentages for the top identified sites:

| Location | Shrinkage Qty | Start Qty | **Shrinkage % (Loss Rate)** |
| :--- | :--- | :--- | :--- |
| **HIE - Rancho Cucamonga** | 716.0 | 716.0 | **100.0%** (Total Inventory Loss) |
| **Thousand Oaks Inn** | 423.0 | 1166.0 | **36.27%** |
| **Holiday Inn Express Barstow** | 177.0 | (Market Hub) | High impact by value ($378k) |
| **Motel 6 Westminster North** | 74.0 | (Market Hub) | High value $378k |

---

## 2. Product-Level Percentage Logic
When looking at individual products within a location, there are two ways to view the "percentage":

### **A. Contribution Percentage (Share of Total Loss)**
*   **Formula:** `(Product Shrinkage Qty / Location Total Shrinkage Qty) * 100`
*   **Reasoning:** Tells you which specific items are driving the most loss at that site.
*   **Example (Rancho Cucamonga - Total Loss: 716 units):**
    *   **Smart Water 20oz:** 77 units lost → **10.75%** of the total site loss.
    *   **Dasani 20oz:** 47 units lost → **6.56%** of the total site loss.
    *   **Smart Water 1L:** 40 units lost → **5.58%** of the total site loss.

### **B. Product Loss Rate (Inventory Vanish Rate)**
*   **Formula:** `(Product Shrinkage Qty / Product Start Qty) * 100`
*   **Reasoning:** Tells you what percentage of that item's specific inventory disappeared.
*   **Insight:** In "Ghost" locations like Rancho Cucamonga (where start qty = total shrinkage), this rate is **100% for every product**, meaning every single unit of that item was lost.

---

## 3. Waste & Spoilage Analysis
Analyzes items that were intentionally discarded (Expired/Damaged) rather than stolen.

| Field | Criteria (How it's calculated) | Reasoning (Why it matters) | Insight Provided |
| :--- | :--- | :--- | :--- |
| **`total_waste_cost`** | Sum of items marked as "Waste" in the `pilot_shrink_log.csv`. | Separates **preventable waste** from **unexplained theft**. | Tells you if you are ordering too much fresh food (Salads/Sandwiches). |
| **Spoilage Criteria** | Items with a fixed shelf life that reached their expiration date. | Prevents food safety issues and tracks "authorized" loss. | High spoilage often leads to a recommendation to reduce "Par" levels. |

---

## 3. Network Transfer Optimization
This is the most complex logic, used to recover value from stagnant stock.

### **A. Logic of the "Why"**
*   **Nearness / Cost Effectivity:** The system calculates the `transfer_cost` (the estimated expense of moving the item). If the cost is higher than the potential profit, the transfer is **rejected**.
*   **Revenue Potential:** This is calculated as `transfer_qty × Unit_Price`. It represents the "saved" sales that would have been lost if the item stayed at a site where it wasn't selling.

### **B. Field-by-Field Breakdown**

| Field | Criteria / Reasoning |
| :--- | :--- |
| **`source_site`** | The "Home" site where the item is currently idle and **Zero Sales** are occurring. |
| **`destination_site`** | The "Fast-Selling" site where inventory is low but **High Demand** is predicted. |
| **`estimated_roi`** | `((Revenue Potential - Transfer Cost) / Transfer Cost) * 100`. Only transfers with a high ROI (usually >200%) are recommended. |
| **`priority`** | **HIGH** priorities are assigned to items with high ROI ($$$) OR high spoilage risk (items that will expire soon). |
| **`date_to_transfer`** | The "Target Window." Moving the item by this date ensures it arrives before the destination site runs out of stock. |
| **`how_fast_to_transfer`** | **Urgent (24h)** vs **Standard (3 Days)**. This is determined by the "Sell-By" date of the product. |
| **`transfer_route`** | The physical path from Source to Destination. The logic prioritizes the **shortest path** to minimize travel time and labor costs. |

---

## 4. Key Takeaways
1.  **High Theft Reasoning:** An item is flagged as "High Theft" if its shrinkage quantity is disproportionately high compared to its sales. (e.g., 50 units missing but 0 units sold).
2.  **Date Reasoning:** Dates are used to verify if "Shrinkage" is a one-time event (like a specific theft incident) or a daily ongoing habit.
3.  **Transfer Reasoning:** We move items to **Destination sites** because it is better to sell an item for $5 (even with a $1 move cost) than to let it expire and lose $4.
