import csv

target = "Holiday Inn Ontario Airport Market"
input_file = "c:\\Users\\IV-UDP-DT-0122\\Downloads\\shrinkage\\Overage Spoilage Shrinkage ReportUltraserv Automated Services 2025-12-04.csv"

total_value = 0
total_qty = 0

with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f)
    headers = next(reader)
    print(f"Headers: {headers}")
    
    # Let's find columns for Type, Qty, and Value
    # Based on earlier view, it seems like:
    # Market, User, Date, Category, Product, Type, Qty, Price, Total
    
    for row in reader:
        if target in row:
            try:
                # Based on observation, Total is around 9th column (index 8)
                # Let's print some rows to be sure
                if total_qty < 5:
                    print(row)
                
                # We need to find which column is Total Value
                # Typically it's Qty * Price
                # Let's assume the last few columns
                val = float(row[-2]) # Trying second to last
                qty = float(row[-4]) # Trying 4th to last
                
                total_value += val
                total_qty += qty
            except:
                pass

print(f"Total Qty: {total_qty}, Total Value: {total_value}")
