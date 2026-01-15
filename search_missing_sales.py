import pandas as pd
import glob
import os

files = glob.glob('Sales By Products Report*.csv')
search_names = ["Penn Championship Tennis Balls", "Boom Chicka Popcorn Sea Salt 4.8oz"]

results = []
for file in files:
    try:
        # Some sales reports have headers that need skipped
        # Let's try to detect the header row or just search raw lines
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            for name in search_names:
                if name in line:
                    # Find price in this line
                    # Usually prices are 5.25, 6.95, etc.
                    # Let's try to parse the row with pandas from this line
                    # Or just print the line
                    print(f"File: {file}, Line: {i}")
                    print(line.strip())
                    
    except Exception as e:
        print(f"Error reading {file}: {e}")

