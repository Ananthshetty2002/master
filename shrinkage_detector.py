import pandas as pd

class ShrinkageDetector:
    def __init__(self, start_df, end_df, sales_df, adjustments_df=None):
        """
        Initialize the ShrinkageDetector with inventory snapshots, sales data, and adjustments.
        
        Args:
            start_df (pd.DataFrame): Inventory at T1. Cols: Location, Product ID, Quantity.
            end_df (pd.DataFrame): Inventory at T2. Cols: Location, Product ID, Quantity.
            sales_df (pd.DataFrame): Sales between T1 and T2. Cols: Location, Product ID, Quantity, Value.
            adjustments_df (pd.DataFrame, optional): Known adjustments (waste, spoilage). Cols: Location, Product ID, Quantity.
        """
        self.start_df = start_df
        self.end_df = end_df
        self.sales_df = sales_df
        self.adjustments_df = adjustments_df
        self.report_df = None

    def detect(self):
        """
        Performs the shrinkage calculation:
        Shrinkage = (Inventory_Start - Inventory_End) - Sales - Known_Adjustments
        """
        # Rename columns standardly to ensure merge works if inputs vary, but assuming 
        # based on spec they are aligned or we just merged on common cols.
        # We'll assume standard naming for now: 'Location', 'Product ID'
        
        # 1. Merge Start and End to calculate Total Depletion
        inventory_merge = pd.merge(
            self.start_df, 
            self.end_df, 
            on=['Location', 'Product ID'], 
            how='outer', 
            suffixes=('_Start', '_End')
        )
        
        # Fill NaNs with 0 for calculation (e.g. item new in End or missing in Start)
        inventory_merge['Quantity_Start'] = inventory_merge['Quantity_Start'].fillna(0)
        inventory_merge['Quantity_End'] = inventory_merge['Quantity_End'].fillna(0)
        
        # Total Depletion = Start - End
        # If result is positive, we lost stock. If negative, we gained stock (restock/error).
        inventory_merge['Total_Depletion'] = inventory_merge['Quantity_Start'] - inventory_merge['Quantity_End']
        
        # 2. Merge with Sales
        # Aggregate sales just in case there are multiple rows per loc/product
        sales_agg = self.sales_df.groupby(['Location', 'Product ID']).agg({
            'Quantity': 'sum',
            'Value': 'sum' # Summing value to keep track of sales value
        }).reset_index().rename(columns={'Quantity': 'Sales_Quantity', 'Value': 'Sales_Value'})
        
        full_data = pd.merge(
            inventory_merge,
            sales_agg,
            on=['Location', 'Product ID'],
            how='outer'
        )
        
        full_data['Sales_Quantity'] = full_data['Sales_Quantity'].fillna(0)
        full_data['Sales_Value'] = full_data['Sales_Value'].fillna(0)

        # 3. Merge with Adjustments (if provided)
        if self.adjustments_df is not None and not self.adjustments_df.empty:
            adj_agg = self.adjustments_df.groupby(['Location', 'Product ID']).agg({
                'Quantity': 'sum'
            }).reset_index().rename(columns={'Quantity': 'Known_Adjustments_Qty'})
            
            full_data = pd.merge(
                full_data,
                adj_agg,
                on=['Location', 'Product ID'],
                how='outer'
            )
            full_data['Known_Adjustments_Qty'] = full_data['Known_Adjustments_Qty'].fillna(0)
        else:
            full_data['Known_Adjustments_Qty'] = 0
        
        # 4. Calculate Shrinkage
        # Shrinkage = Total Depletion - Sales - Known Adjustments
        # Positive Shrinkage means we lost more than we sold + wasted (Theft/Unaccounted)
        full_data['Shrinkage_Qty'] = full_data['Total_Depletion'] - full_data['Sales_Quantity'] - full_data['Known_Adjustments_Qty']
        
        # Estimate Shrinkage Value. Since we might not have cost, we can use Sales Value / Sales Qty * Shrink Qty
        # Or if Sales_Value is provided per unit... let's try to infer unit price from sales.
        # If Sales Qty > 0, Unit Price = Sales Value / Sales Qty.
        # Else we might not know value if not sold. 
        # For this MVP, let's use the average implied price from sales data if available.
        # Safety check for zero division.
        
        full_data['Implied_Unit_Price'] = full_data.apply(
            lambda row: row['Sales_Value'] / row['Sales_Quantity'] if row['Sales_Quantity'] > 0 else 0, axis=1
        )
        
        # If implied price is 0, we can't calculate shrinkage value easily without a cost map.
        # We will leave it as 0 for now or if user provides a price map later.
        full_data['Shrinkage_Value'] = full_data['Shrinkage_Qty'] * full_data['Implied_Unit_Price']
        
        self.report_df = full_data
        return self.report_df

    def rank_by_severity(self):
        """
        Sorts by Shrinkage Quantity and Value descending.
        """
        if self.report_df is None:
            self.detect()
            
        # We care mostly about positive shrinkage (loss).
        # We will sort descending so big losses are at top.
        self.report_df = self.report_df.sort_values(by=['Shrinkage_Qty', 'Shrinkage_Value'], ascending=False)
        return self.report_df

    def get_report(self):
        return self.report_df
