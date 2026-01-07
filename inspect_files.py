
import pandas as pd
import glob

files = {
    "Overage": "c:/Users/IV-UDP-DT-0122/Downloads/shrinkage/Overage Spoilage Shrinkage ReportUltraserv Automated Services 2025-12-04.csv",
    "ProdTrans": "c:/Users/IV-UDP-DT-0122/Downloads/shrinkage/Product Transaction Report (2).csv",
    "TransListWeek8": "c:/Users/IV-UDP-DT-0122/Downloads/shrinkage/transaction list week8.csv"
}

for name, path in files.items():
    print(f"\n--- {name} ---")
    try:
        df = pd.read_csv(path, nrows=10000) # Read first 10k rows
        print("Columns:", list(df.columns))
        
        if "Change Type" in df.columns:
            print("Change Types:", df["Change Type"].unique())
            
        if "Transfer Type" in df.columns:
            print("Transfer Types:", df["Transfer Type"].unique())
            
        if "Location" in df.columns:
            print(f"Location populated: {df['Location'].notna().sum()}/{len(df)}")
            if df['Location'].notna().any():
                print("Location sample:", df['Location'].dropna().unique()[:5])
                
        if "Micro Market" in df.columns:
             print("Micro Market sample:", df['Micro Market'].dropna().unique()[:5])

    except Exception as e:
        print(f"Error reading {name}: {e}")

# Check for other sales files
print("\n--- Other Transaction Files ---")
sales_files = glob.glob("c:/Users/IV-UDP-DT-0122/Downloads/shrinkage/*transaction*.csv")
for f in sales_files:
    print(f)
