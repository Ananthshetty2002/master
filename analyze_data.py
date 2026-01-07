import pandas as pd
import os

# Define file paths
base_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
shrink_log_path = os.path.join(base_dir, "pilot_shrink_log_clean.csv")
risk_scores_path = os.path.join(base_dir, "risk_scores_day1.csv")
transfer_path = os.path.join(base_dir, "transfer_day1_all.csv")
output_file = os.path.join(base_dir, "data_analysis_summary.txt")

def analyze_data():
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("SHRINKAGE AND RISK DATA ANALYSIS\n")
        f.write("================================\n\n")

        # 1. Analyze Risk Scores
        if os.path.exists(risk_scores_path):
            f.write("1. RISK SCORES ANALYSIS (from risk_scores_day1.csv)\n")
            f.write("--------------------------------------------------\n")
            try:
                df_risk = pd.read_csv(risk_scores_path)
                f.write(f"Total entries: {len(df_risk)}\n")
                
                # High Risk Users
                high_risk = df_risk[df_risk['Risk_band'] == 'HIGH']
                f.write(f"Number of HIGH risk users: {len(high_risk)}\n\n")
                f.write("Top 5 Highest Shrink Value Users:\n")
                top_users = df_risk.sort_values(by='Total_shrink_value', ascending=False).head(5)
                for _, row in top_users.iterrows():
                    f.write(f" - {row['User Name']} @ {row['Site']}: ${row['Total_shrink_value']:.2f} ({row['Risk_band']})\n")
                f.write("\n")
            except Exception as e:
                f.write(f"Error reading risk scores: {e}\n\n")

        # 2. Analyze Shrink Log
        if os.path.exists(shrink_log_path):
            f.write("2. SHRINKAGE LOG ANALYSIS (from pilot_shrink_log_clean.csv)\n")
            f.write("----------------------------------------------------------\n")
            try:
                df_shrink = pd.read_csv(shrink_log_path)
                f.write(f"Total shrinkage events: {len(df_shrink)}\n")
                
                # Total Shrinkage Value
                total_value = df_shrink['TotalCost'].sum()
                f.write(f"Total Shrinkage Cost: ${total_value:.2f}\n")
                
                # Top Products by Shrink Cost
                f.write("\nTop 5 Products by Total Shrink Cost:\n")
                top_products = df_shrink.groupby('Product')['TotalCost'].sum().sort_values(ascending=False).head(5)
                for product, cost in top_products.items():
                    f.write(f" - {product}: ${cost:.2f}\n")
                
                # Top Sites by Shrink Cost
                f.write("\nTop 5 Sites by Total Shrink Cost:\n")
                top_sites = df_shrink.groupby('Site')['TotalCost'].sum().sort_values(ascending=False).head(5)
                for site, cost in top_sites.items():
                    f.write(f" - {site}: ${cost:.2f}\n")
                f.write("\n")
            except Exception as e:
                f.write(f"Error reading shrink log: {e}\n\n")

        # 3. Analyze Transfers
        if os.path.exists(transfer_path):
            f.write("3. TRANSFER ANALYSIS (from transfer_day1_all.csv)\n")
            f.write("------------------------------------------------\n")
            try:
                df_transfer = pd.read_csv(transfer_path)
                f.write(f"Total transfers recorded: {len(df_transfer)}\n")
                
                # Product counts
                f.write("\nTop 5 Transferred Products (by frequency):\n")
                top_transfers = df_transfer['Product'].value_counts().head(5)
                for product, count in top_transfers.items():
                    f.write(f" - {product}: {count} transfers\n")
            except Exception as e:
                f.write(f"Error reading transfers: {e}\n\n")

if __name__ == "__main__":
    analyze_data()
    print(f"Analysis complete. Results saved to {output_file}")
