import csv

target = "HIE - Rancho Cucamonga Market"
input_file = "c:\\Users\\IV-UDP-DT-0122\\Downloads\\shrinkage\\CSVStock Analysis Report.csv"

with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if target in row:
            print(f"L{i+1}: {row}")
