import glob
import os

def find_sales_file(target_loc):
    files = glob.glob('Sales By Products Report*.csv')
    print(f"Scanning {len(files)} files for '{target_loc}'...")
    
    found = False
    for fname in files:
        try:
            with open(fname, 'r') as f:
                # Read first 5 lines
                lines = [f.readline() for _ in range(5)]
                # Check line 3 (index 2) or any line for target_loc
                content = "".join(lines)
                if target_loc.lower() in content.lower():
                    print(f"FOUND: {fname}")
                    print(f"Header Context: {lines[2].strip() if len(lines)>2 else ''}")
                    found = True
                    break
        except Exception as e:
            pass
            
    if not found:
        print("Not found.")

if __name__ == "__main__":
    find_sales_file("Altura HOC 2nd Floor Market")
