import pandas as pd
import sys

def explore():
    with open('data_exploration.txt', 'w') as f:
        # Product Transaction Report
        try:
            f.write("--- Product Transaction Report (2).csv ---\n")
            df = pd.read_csv('Product Transaction Report (2).csv', low_memory=False, nrows=10000)
            f.write(f"Columns: {list(df.columns)}\n")
            if 'Transfer Type' in df.columns:
                f.write(f"Unique Transfer Types: {df['Transfer Type'].unique().tolist()}\n")
            else:
                f.write("Transfer Type column not found.\n")
        except Exception as e:
            f.write(f"Error reading Product Transaction Report: {e}\n")

        f.write("\n")

        # Overage Report
        try:
            f.write("--- Overage Spoilage Shrinkage Report... ---\n")
            df2 = pd.read_csv('Overage Spoilage Shrinkage ReportUltraserv Automated Services 2025-12-04.csv', low_memory=False, nrows=1000)
            f.write(f"Columns: {list(df2.columns)}\n")
        except Exception as e:
            f.write(f"Error reading Overage Report: {e}\n")

if __name__ == "__main__":
    explore()
