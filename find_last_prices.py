import pandas as pd
import glob
import os

def find_price(name):
    files = glob.glob('Sales By Products Report*.csv')
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if name.lower() in line.lower():
                        # Try to extract the price from the line
                        parts = line.split(',')
                        # Usually Unit Price is the 4th or 5th column
                        for part in parts:
                            try:
                                val = float(part.strip())
                                if 1.0 < val < 50.0: # Reasonable price range
                                    return val
                            except:
                                continue
        except:
            continue
    return None

prices = {}
prices["Penn Championship Tennis Balls"] = find_price("Tennis")
prices["Boom Chicka Popcorn Sea Salt 4.8oz"] = find_price("Boom Chicka")

print(prices)
