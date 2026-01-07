# The Shrinkage Project: A Simple Guide

**Goal:** We built a "machine" to find where money is being lost (stolen items, wasted food) and how to save it.

---

## 1. How It Works
Think of this entire folder as a factory:
1.  **Input:** We feed it sales records and stock lists.
2.  **Process:** The computer ("The Robots") checks every line to find mistakes or weird patterns.
3.  **Output:** It prints a Report telling us exactly how to save **$500,000**.

---

## 3. The Files (Explained Simply)

### Group A: The Root Reports (The Inputs)
These are the original files we started with. Everything comes from here.

| File Name | Description | Key Fields Used |
| :--- | :--- | :--- |
| **`Overage Spoilage...`** | **The Waste Report.** Shows every item thrown away. | `Product`, `TotalCost`, `Qty`, `Site`, `Date` |

| **`transaction list...`** | **The 8-Week History.** Used to find "True Average" sales. | `Created On`, `Micro Market`, `Product Code`, `Product Desc`, `Quantity` |



---



### Group B: The Robots (The Python Scripts)
These are the small programs that do the hard work for us.

| File Name | What It Does (In English) |
| :--- | :--- |
| `analyze_waste.py` | **The Waste Finder.** Calculated clearly that we lose $605 every day on rotting food. |
| `shrinkage.py` | **The Theft Finder.** Looks for items that vanished without payment. |
| `risk_escalation.py` | **The Staff Watcher.** Tells us which employees (like Rony) are making the most mistakes. |
| `convert_to_pdf.py` | **The Publisher.** Takes your plain text and makes it a professional looking PDF. |
| `email_distribution.py`| **The Mailman.** Sends the reports to managers automatically so you don't have to. |

### Group C: The Facts (The Data Files)
The raw information we used to find the answers.

| File Name | What It Is |
| :--- | :--- |
| `transaction_site_sku_weekday_avg.csv` | **The "Holy Grail".** It knows exactly how much Milk sells on a Tuesday at Westin. We use this to know how much to order. |
| `risk_scores_day1.csv` | **The Scorecard.** A list of every employee and their "Risk Level". |
| `transfer_day1_all.csv` | **The Fix.** A list of exactly what food to move from one building to another to stop it from rotting. |

---

## 4. The Bottom Line
We used all these tools to prove three things:
1.  **Waste** is costing us huge money ($605/day).
2.  **Theft** is small per person, but dangerous if we ignore it ($450k risk).
3.  **The Fix** is easy: Move the stock, order less for quiet sites, and check on the high-risk staff.

---

## 5. The Prompts (For ChatGPT/AI)
If you need to run this analysis again using an AI, use these exact instructions.

### The System Prompt (For n8n AI Agent)
> "You are an **Autonomous Data Analyst** running within an n8n workflow. You have access to Python code tools and CSV datasets.
>
> **Your Core Task:**
> Analyze the provided `transaction_list` and `spoilage_log` to minimize financial loss.
>
> **Required Actions:**
> 1.  **Waste Analysis:** Filter data to identify SKUs where `Spoilage_Cost` > $0. Calculate the daily average waste (Target: ~$605/day).
> 2.  **Par Calculation:** Compute the `Mean(Daily_Sales)` over 8 weeks for high-waste items (Milk, Turkey, Ginger Ale). Suggest new lower stock levels.
> 3.  **Risk Audit:** Group shrinkage data by `User_Name`. Identify staff with > $1000 in missing stock.
>
> **Final Output:**
> Return a structured JSON summary with keys: `daily_waste_loss`, `recommended_pars`, and `high_risk_staff_list`."

### The User Prompt (Task)
> "I am attaching 8 weeks of Sales reports and the Spoilage/Shrinkage log.
>
> 1.  **Analyze Waste:** Identify why we are losing money on food waste (approx $600/day?). Which items are rotting?
> 2.  **Calculate Pars:** Look at the 'True Daily Average' sales for the top wasted items (Milk, Turkey, Ginger Ale) at Westin. Suggest a new 'Par Level' (e.g., Keep only 2 in the cooler) to stop the waste.
> 3.  **Staff Risk:** Look at the shrinkage log. Which staff members have the most missing items?
> 4.  **Action Plan:** Create a one-page summary telling me exactly which stock to move and which staff to audit."
