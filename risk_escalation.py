import pandas as pd
import os

base_dir = r"c:\Users\IV-UDP-DT-0122\Downloads\shrinkage"
risk_scores_path = os.path.join(base_dir, "risk_scores_day1.csv")

def analyze_escalation():
    try:
        df = pd.read_csv(risk_scores_path)
        
        # Segment data
        high_risk = df[df['Risk_band'] == 'HIGH']
        med_risk = df[df['Risk_band'] == 'MED']
        low_risk = df[df['Risk_band'] == 'LOW']
        
        # Calculate stats
        med_count = len(med_risk)
        med_value = med_risk['Total_shrink_value'].sum()
        med_avg = med_value / med_count if med_count else 0
        
        high_avg = high_risk['Total_shrink_value'].sum() / len(high_risk) if len(high_risk) else 0
        
        # Escalation Scenario: What if MED users behave like HIGH users?
        med_potential_loss = med_count * high_avg
        med_added_risk = med_potential_loss - med_value

        # Escalation Scenario: What if LOW users behave like HIGH users? (Worst case)
        low_count = len(low_risk)
        low_value = low_risk['Total_shrink_value'].sum()
        low_avg = low_value / low_count if low_count else 0
        
        low_potential_loss = low_count * high_avg
        low_added_risk = low_potential_loss - low_value
        
        total_added_risk = med_added_risk + low_added_risk

        with open(os.path.join(base_dir, "escalation_analysis.txt"), "w") as f:
            f.write("RISK ESCALATION ANALYSIS\n")
            f.write("========================\n\n")
            f.write(f"High Risk Avg Loss: ${high_avg:.2f}\n")
            f.write(f"Medium Risk Avg Loss: ${med_avg:.2f}\n")
            f.write(f"Low Risk Avg Loss: ${low_avg:.2f}\n\n")
            
            f.write(f"Medium Risk Users: {med_count} | Current Loss: ${med_value:.2f}\n")
            f.write(f" -> Potential Added Loss (Med->High): ${med_added_risk:.2f}\n\n")
            
            f.write(f"Low Risk Users: {low_count} | Current Loss: ${low_value:.2f}\n")
            f.write(f" -> Potential Added Loss (Low->High): ${low_added_risk:.2f}\n\n")
            
            f.write(f"TOTAL POTENTIAL ADDED LOSS (Med+Low -> High): ${total_added_risk:.2f}\n\n")
            
            f.write("Insight: Both Medium and Low risk users are 'High Risk in Training'.\n")
            f.write("The lack of monitoring converts them to High Risk over time.\n")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_escalation()
