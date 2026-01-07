import pandas as pd

def inspect_csv(file_path):
    output = []
    output.append(f"--- Inspecting {file_path} ---")
    try:
        df = pd.read_csv(file_path, low_memory=False)
        output.append(f"Headers: {df.columns.tolist()}")
        output.append("\nFirst 5 rows:")
        output.append(df.head().to_string())
        if 'Micro Market' in df.columns:
            output.append(f"\nUnique Micro Markets: {df['Micro Market'].unique().tolist()}")
        elif 'Location' in df.columns:
            output.append(f"\nUnique Locations: {df['Location'].unique().tolist()}")
    except Exception as e:
        output.append(f"Error reading {file_path}: {e}")
    return "\n".join(output)

results = []
results.append(inspect_csv('transactionlistweek2.csv'))
results.append(inspect_csv('end.csv'))

with open('inspection_results.txt', 'w') as f:
    f.write("\n\n".join(results))
