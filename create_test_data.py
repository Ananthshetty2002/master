import pandas as pd

# 1. stock_analysis_yesterday.csv
yesterday = pd.DataFrame({
    'Location': ['Site_A', 'Site_A', 'Site_B', 'Site_C', 'Site_D'],
    'Product Code': ['SKU001', 'SKU002', 'SKU001', 'SKU999', 'SKU777'],
    'Product Description': ['Coke', 'Pepsi', 'Coke', 'Ghost Item', 'Overage Item'],
    'On Hand Qty': [100, 50, 80, 10, 5]
})
yesterday.to_csv('stock_analysis_yesterday.csv', index=False)

# 2. stock_analysis_today.csv
today = pd.DataFrame({
    'Location': ['Site_A', 'Site_A', 'Site_B', 'Site_C', 'Site_D'],
    'Product Code': ['SKU001', 'SKU002', 'SKU001', 'SKU888', 'SKU777'],
    'Product Description': ['Coke', 'Pepsi', 'Coke', 'New Item', 'Overage Item'],
    'On Hand Qty': [80, 45, 60, 5, 20] # SKU777: 5 - 0 - 20 = -15 (Overage)
})
today.to_csv('stock_analysis_today.csv', index=False)

# 3. transaction_list.csv
sales = pd.DataFrame({
    'Location': ['Site_A', 'Site_A', 'Site_B', 'Site_B', 'Site_A'],
    'Product Code': ['SKU001', 'SKU002', 'SKU001', 'SKU001', 'SKU001'],
    'Product Description': ['Coke', 'Pepsi', 'Coke', 'Coke', 'Coke'],
    'Quantity': [15, 2, 10, 5, 50], # 50 is out of range
    'Created On': ['2025-12-22', '2025-12-22', '2025-12-22', '2025-12-22', '2025-12-21']
})
sales.to_csv('transaction_list.csv', index=False)

# 4. product_prices.csv
prices = pd.DataFrame({
    'Product Code': ['SKU001', 'SKU002'],
    'Product Description': ['Coke', 'Pepsi'],
    'Unit Price': [2.50, 3.00]
})
prices.to_csv('product_prices.csv', index=False)

print("Test data files created successfully.")
