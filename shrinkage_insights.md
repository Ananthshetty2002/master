# Shrinkage Insights & n8n Questions

Based on the analysis of `shrinkage_report.csv`, here are the key insights and the recommended questions to implement in your n8n engine.

## 1. "Ghost" Disappearances (High Shrinkage, Zero Sales)
**Insight**: A significant number of products are disappearing entirely without *any* recorded sales. This strongly suggests theft or complete spoilage that wasn't logged.
- **Data Point**: We found frequent cases where `Shrinkage > 10` but `Sales Quantity == 0`.
- **Example**: `PC16463` lost 910 units with 0 sales.

### n8n Questions (Natural Language)
1.  "Identify products that have high inventory loss but zero sales recorded."
2.  "Which items are disappearing from stock without generating any revenue?"
3.  "List top 10 'Ghost' items by quantity lost."

## 2. High Loss Rate (>50% of Stock)
**Insight**: Some products are losing more than half of their starting inventory to shrinkage. These are high-risk items that need immediate physical security or removal.
- **Data Point**: `Shrinkage / Start_Quantity > 0.5`.
- **Example**: `PC10849` lost 100% (263/263) of its stock.

### n8n Questions (Natural Language)
1.  "Which products have varying loss rates greater than 50%?"
2.  "Show me items where we lost more than half of the starting inventory."
3.  "Rank locations by the percentage of inventory lost."

## 3. Top Absolute Losers
**Insight**: Regardless of rate, some items represent the biggest bulk losses.
- **Data Point**: Top ranked items by `Shrinkage_Qty`.

### n8n Questions (Natural Language)
1.  "What are the top 5 products by quantity lost across all locations?"
2.  "Which location has the highest total shrinkage quantity?"

## 4. Unexpected "Gains" (Negative Shrinkage)
**Insight**: We detected items where the Ending Inventory > (Start - Sales). This implies `Shrinkage < 0`. This usually means:
- Missed Restock event in the logs.
- Miscount at Start (underestimated).
- Swapping (Product A counted as Product B).

### n8n Questions (Natural Language)
1.  "Are there any products showing inventory gains (negative shrinkage)?"
2.  "List items that might have been restocked without a transaction record."

## Implementation in n8n
When building your n8n workflow:
- **Input**: `shrinkage_report.csv`
- **Agent Prompt**: "You are a Loss Prevention Analyst. Use the attached report to answer the user's questions about theft and inventory gaps."
- **Context**: Provide the definitions above (e.g. "Ghost Disappearance means Sales=0 and Shrink>0").
