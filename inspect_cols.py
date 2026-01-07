
import pandas as pd

def print_cols(name, path):
    try:
        cols = pd.read_csv(path, nrows=0).columns.tolist()
        print(f"--- {name} ---")
        for c in cols:
            print(c)
    except Exception as e:
        print(f"Error reading {name}: {e}")

print_cols("PROD_TRANS", "c:/Users/IV-UDP-DT-0122/Downloads/shrinkage/Product Transaction Report (2).csv")
print_cols("SALES", "c:/Users/IV-UDP-DT-0122/Downloads/shrinkage/transaction week1.csv")
print_cols("OVERAGE", "c:/Users/IV-UDP-DT-0122/Downloads/shrinkage/Overage Spoilage Shrinkage ReportUltraserv Automated Services 2025-12-04.csv")
