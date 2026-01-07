import pandas as pd
import os
import glob

def inspect_csvs():
    csv_files = glob.glob("*.csv")
    for f in csv_files:
        try:
            # Try to find header row (some files have metadata at top)
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                header = ""
                for i in range(20):
                    line = file.readline()
                    if not line: break
                    if "Micromarket" in line or "Site" in line or "Product" in line:
                        header = line
                        break
                
                if "exp" in header.lower() or "date" in header.lower():
                    print(f"\n--- {f} ---")
                    print(f"Potential Header: {header.strip()}")
                    # Load a few rows
                    try:
                        df = pd.read_csv(f, nrows=5, skiprows=i if header else 0, on_bad_lines='skip')
                        print("Sample data:")
                        print(df.head())
                    except:
                        print("Could not load sample data.")
        except Exception as e:
            print(f"Error reading {f}: {e}")

if __name__ == "__main__":
    inspect_csvs()
