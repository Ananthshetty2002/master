# The Low Stockout Report: Keeping Shelves Full

## 1. What is the Problem?
**Simple Explanation:**
We are losing money because our best products are often empty, while our worst products sit on the shelf forever.
*   **The "Winners" (Fast Sellers):** Items like Coke and String Cheese sell very fast. We run out of them constantly.
*   **The "Losers" (Slow Sellers):** Items like certain Sandwiches sit for weeks. Nobody buys them.

**Why does this matter?**
When a customer wants a Coke and the shelf is empty, they don't buy anything. We lose that sale forever.

### Actual Examples from Our Stores
| Store Location | Product | Status | The Problem |
| :--- | :--- | :--- | :--- |
| **Travelodge Commerce** | **Coke (20oz)** | **RUNNING OUT** | We only have **3 bottles** left. It sells 45 times a week. It will be gone by tomorrow! |
| **Altura Market** | **String Cheese** | **DANGER** | We often hit **0 stock**. This is the #1 best seller. Empty shelf = Zero sales. |
| **Westin Pasadena** | **Sandwiches** | **TOO MUCH** | We have **13 weeks** of supply. It sits there getting old and taking up space. |

---

## 2. The Solution: Two Supremely Simple Steps

### Step 1: Move the "Slow" Stock
We have too much "Slow" stock in some places and not enough in others. We will simply move it.
*   **Action:** Take the extra stock from stores that have too much.
*   **Destination:** Send it to stores that actually need it.
*   **Cost:** It only costs **$60 - $80** to move the stock.
*   **Benefit:** We stop wasting money on old products.

### Step 2: The "Red Alert" for "Fast" Stock
We need to know *before* we run out. We will use a daily check.
*   **The Check:** Every morning at 6:00 AM, a computer checks our Top 20 Best Sellers.
*   **The Rule:** If we have less than **3 days** of supply left, it screams for help.
*   **The Alert:** "🚨 **Order Coke NOW! Only 3 left!**"
*   **The Result:** We refill the shelf immediately. The customer never sees an empty spot.

---

## 3. The Financial Impact: Huge Wins
By fixing this, we stop losing sales and start making more money immediately.

### Sales Growth Table
| Measurement | Before the Fix | After the Fix | The Extra Money |
| :--- | :--- | :--- | :--- |
| **Stockouts** | We run out **20%** of the time. | We run out **< 2%** of the time. | Customers always buy. |
| **Top 5 Items** | Sales: **$1,209** / day | Sales: **Full Potential** | **+$242 / day** |
| **Lost Sales** | We lose **$374** / day | We capture that money. | **+$218 - $450 / day** |
| **Store Monthly** | **$25,000** / month | **$28,000** / month | **+$3,000 / month** |
| **Network (5 Sites)** | **$175,000** / month | **$199,000** / month | **+$24,000 / month** |

### Week 1 Result
*   **Cost to Fix:** $0 (We use existing stock and drivers).
*   **Profit:** We expect **$1,074** extra profit in just the first week.
*   **ROI:** 239% Return on Investment.

---

## Summary
1.  **Stop buying slow items.**
2.  **Move the old stock** to where it will sell.
3.  **Fill the best sellers** every single day.
4.  **Make $56,000+ extra** per year.

---

# 5. The Prompts (For ChatGPT/AI)
If you need to run this analysis again using an AI, use these exact instructions.

### The System Prompt (For n8n AI Agent)
> "You are an **Autonomous Supply Chain Analyst** running within an n8n workflow. You have access to Python code tools and CSV datasets.
>
> **Your Core Task:**
> Analyze the provided `Product Transaction Report` to prevent stockouts and minimize lost sales.
>
> **Required Actions:**
> 1.  **Velocity Analysis:** Filter data to identify high-velocity SKUs (Top 20 Sellers). Calculate the daily sales velocity for each.
> 2.  **Stockout Risk Alert:** Calculate the 'Days of Supply' for these high-velocity items (Current Stock / Daily Sales). Alert if Days of Supply < 3.
> 3.  **Overstock Audit:** Identify 'Slow Sellers' (Bottom 20%) that have > 14 weeks of supply.
>
> **Final Output:**
> Return a structured JSON summary with keys: `daily_reorder_list`, `transfer_candidates`, and `lost_sales_estimate`."

### The User Prompt (Task)
> "I am attaching the Product Transaction Report.
>
> 1.  **Analyze Winners:** Which items calculate as 'Fast Sellers' (High Velocity)? Identify any that are currently running low (< 3 days stock).
> 2.  **Analyze Losers:** Who are the 'Slow Sellers' taking up space? Use the 'Westin Pasadena Sandwiches' logic (Inventory > 14 weeks).
> 3.  **Transfer Plan:** Propose a list of items to move FROM 'Overstocked' sites TO 'High Demand' sites.
> 4.  **Action Plan:** Create a one-page summary telling me exactly which stock to move and which items need an emergency reorder."
