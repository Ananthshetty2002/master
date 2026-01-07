import csv

path = r"C:\Users\IV-UDP-DT-0122\Downloads\shrinkage\transaction list week8.csv"
try:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        header = next(reader)
        print("Headers:", header)
        print("Row 1:", next(reader))
except Exception as e:
    print(e)
