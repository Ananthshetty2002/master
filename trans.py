import glob
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

# ========== 1. LOAD & CLEAN ALL 8 TRANSACTION FILES ==========

files = glob.glob("transaction*week*.csv")   # your 8 weekly files
print("Files found:", files)

dfs = []
for f in files:
    df = pd.read_csv(f)
    print(f"\nProcessing: {f}")
    print("Columns:", list(df.columns))

    # rename to standard internal names
    df = df.rename(columns={
        'Created On': 'Date',
        'Micro Market': 'Site',
        'Product Code': 'Product_Code',
        'Product Desc': 'Product_Desc',
        'Quantity': 'Qty_Sold'
    })

    if 'Date' not in df.columns or 'Qty_Sold' not in df.columns:
        print("  -> Skipping, missing Date or Qty_Sold")
        continue

    # drop totals / blanks then convert Date
    df = df[df['Date'].notna()]
    df = df[~df['Date'].astype(str).str.contains('Total', case=False, na=False)]
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    # quantity numeric
    df['Qty_Sold'] = pd.to_numeric(df['Qty_Sold'], errors='coerce').fillna(0)

    dfs.append(df[['Date', 'Site', 'Product_Code', 'Product_Desc', 'Qty_Sold']])

trans = pd.concat(dfs, ignore_index=True)
print("\nTotal rows after clean:", len(trans))
print(trans.head())

# ========== 2. DAILY SALES PER SITE + SKU ==========

daily = (trans
         .groupby(['Site', 'Product_Code', 'Product_Desc', 'Date'])['Qty_Sold']
         .sum()
         .reset_index())

print("\nSample of daily:")
print(daily.head())

# ========== 3. WEEKDAY AVERAGE PATTERN (SITE-SPECIFIC TUNING) ==========

daily['Weekday'] = daily['Date'].dt.weekday  # 0=Mon
avg_pattern = (daily
               .groupby(['Site', 'Product_Code', 'Product_Desc', 'Weekday'])['Qty_Sold']
               .mean()
               .round()
               .reset_index())

avg_pattern.to_csv("transaction_site_sku_weekday_avg.csv", index=False)
print("\nSaved: transaction_site_sku_weekday_avg.csv")
avg = pd.read_csv("transaction_site_sku_weekday_avg.csv")
westin_avg = avg[avg['Site'] == 'The Westin Long Beach']

targets = westin_avg[westin_avg['Product_Desc'].str.contains(
    'milk|yogurt|turkey|ginger|dew', case=False, na=False)]
print(targets[['Product_Code','Product_Desc']].drop_duplicates())

# ========== 4. ARIMA HELPER FUNCTION ==========

def arima_forecast(ts, steps=7):
    """
    ts: pandas Series indexed by Date (daily).
    returns: average forecast for next 7 days.
    """
    ts = ts.asfreq('D').fillna(0)
    if len(ts) < 14:          # if less than 14 days of data, use mean
        return ts.mean()
    model = ARIMA(ts, order=(1, 1, 1))
    res = model.fit()
    return res.forecast(steps=steps).mean()

# ========== 5. DEFINE PILOT SITES & SKUs ==========

# Use exact Site text from trans['Site'].unique()
pilot_sites = [
    'The Westin Long Beach',
    'Bldg 80 Micro',
    'Brandt Russell Guthrie'
]

# Start with two key SKUs; replace with true milk / yogurt / ginger codes you identify
key_skus = [
    'PC10997',          # Regular milk – Milk Shamrock Lowfat 7oz
    'AVR18526',         # Fairlife Chocolate Milk 14oz
    'AVR27451',         # Muscle Milk Chocolate 14oz
    'AVR27452',         # Muscle Milk Vanilla 14oz
    'AVR26220',         # FR SLB Multigrain Turkey & Bacon Club
    'AVR26225',         # FR SLB Sub Turkey & Cheese
    'AVR26226',         # FR SLB Triangle Turkey Wheat
    'PC10762',          # Lunchables Turkey & Cheddar
    'AVR00149',         # Schweppe\'s Ginger Ale 20oz
    'AVR09658'          # Mountain Diet Dew 20oz
]


   # update after checking value_counts

# ========== 6. BUILD ARIMA-BASED ORDERS ==========

rows = []
for s in pilot_sites:
    for sku in key_skus:
        sub = daily[(daily['Site'] == s) & (daily['Product_Code'] == sku)]
        if sub.empty:
            continue
        ts = sub.set_index('Date')['Qty_Sold'].sort_index()

        # simple average daily demand (since we already know they sell)
        f = ts.mean()          # average units per day

        rows.append({
            'Site': s,
            'Product_Code': sku,
            'Forecast_avg_next_7d': round(f, 1),
            'Weekday_order': int(f * 1.2),   # +20% buffer
            'Weekend_order': int(f * 0.8)    # -20% weekend
        })

orders = pd.DataFrame(rows)
orders.to_csv("transaction_arima_orders.csv", index=False)
print("\nOrders (mean-based):")
print(orders)

westin = trans[trans['Site'] == 'The Westin Long Beach']
print(westin['Product_Code'].value_counts().head(40))
codes = ['PC19076','PC14015','PC14016','PC16271','PC00889',
         'AVR14918','AVR00144','AVR00145','AVR00147','AVR00148','AVR00156']

print(westin[westin['Product_Code'].isin(codes)]
      [['Product_Code','Product_Desc']].drop_duplicates())
for sku in [
    'PC10997','AVR26220','AVR26225','AVR26226','PC10762',
    'AVR09658','AVR18526','AVR27451','AVR27452'
]:
    sub = trans[(trans['Site'] == 'The Westin Long Beach') &
                (trans['Product_Code'] == sku)]
    print(sku, "rows:", len(sub))
# Top 15 SKUs at Westin by average DAILY sales
westin_daily = daily[daily['Site'] == 'The Westin Long Beach']

top_westin = (westin_daily
              .groupby(['Product_Code','Product_Desc'])['Qty_Sold']
              .mean()
              .sort_values(ascending=False)
              .head(15))

print("Top Westin SKUs by avg units/day:")
print(top_westin)
focus_codes = [
    'PC10997',          # plain milk
    'AVR18526','AVR27451','AVR27452',  # flavored/protein milk
    'AVR26220','AVR26225','AVR26226','PC10762',  # turkey
    'AVR00149',         # Ginger Ale
    'AVR09658'          # Diet Dew
]

focus = (westin_daily[westin_daily['Product_Code'].isin(focus_codes)]
         .groupby(['Product_Code','Product_Desc'])['Qty_Sold']
         .mean()
         .sort_values(ascending=False))

print("\nFocus SKUs avg units/day at Westin:")
print(focus)
focus_codes = ['PC10997','AVR18526','AVR27451','AVR27452',
               'AVR26220','AVR26225','AVR26226','PC10762',
               'AVR00149','AVR09658']

for site in ['Bldg 80 Micro', 'Brandt Russell Guthrie']:
    sd = daily[daily['Site'] == site]
    focus = (sd[sd['Product_Code'].isin(focus_codes)]
             .groupby(['Product_Code','Product_Desc'])['Qty_Sold']
             .mean().round(2))
    print("\n", site, "avg units/day:")
    print(focus)
