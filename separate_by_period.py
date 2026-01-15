import pandas as pd
import json
from datetime import datetime

def separate_alerts_by_period():
    """Rebuild alerts with proper date period separation"""
    
    # Load existing alerts
    with open('business_alerts.json', 'r', encoding='utf-8') as f:
        old_alerts = json.load(f)
    
    # Create new structure with date periods
    alerts = {
        "generated_at": datetime.now().isoformat(),
        "data_periods": {
            "december_3_to_31_2025": {
                "period_label": "DEC 3-31, 2025",
                "data_source": "shrinkage_report_refined.csv + n8n_consolidated_report",
                "alert_count": 0,
                "alerts": {
                    "theft_detection": [],
                    "spoilage_prevention": [],
                    "inventory_accuracy": [],
                    "transfer_optimization": [],
                    "pos_health": [],
                    "high_loss_products": [],
                    "location_risk_scores": []
                }
            },
            "november_2025": {
                "period_label": "NOV 2025 (Baseline)",
                "data_source": "Overage Spoilage Shrinkage Report 2025-12-04.csv",
                "alert_count": 0,
                "note": "This data is from November, not December - use for baseline comparison only",
                "alerts": {
                    "spoilage_events": []
                }
            },
            "december_8_to_19_2025": {
                "period_label": "DEC 8-19, 2025",
                "data_source": "DEC 8-19 folder (Sales Reports, Transaction Lists)",
                "alert_count": 0,
                "alerts": {
                    "transaction_analysis": [],
                    "sales_verification": []
                }
            },
            "december_23_to_31_2025": {
                "period_label": "DEC 23-31, 2025",
                "data_source": "DEC 23-31 folder (Product Rank, Transaction Reports)",
                "alert_count": 0,
                "alerts": {
                    "product_rankings": [],
                    "end_of_month_analysis": []
                }
            }
        },
        "summary": {
            "total_alerts": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "data_quality_warnings": [
                "191 out of 193 sites missing Sales By Product reports for December",
                "Spoilage data is from November 2025, not December 2025",
                "Main analysis period (DEC 3-31) has incomplete sales data"
            ]
        }
    }
    
    # Categorize existing alerts by period
    # Most alerts are from the main December 3-31 period
    dec_main = alerts["data_periods"]["december_3_to_31_2025"]["alerts"]
    
    # Move theft, POS, inventory, high-loss to main December period
    dec_main["theft_detection"] = old_alerts["alerts"]["theft_detection"]
    dec_main["pos_health"] = old_alerts["alerts"]["pos_health"]
    dec_main["inventory_accuracy"] = old_alerts["alerts"]["inventory_accuracy"]
    dec_main["high_loss_products"] = old_alerts["alerts"]["high_loss_products"]
    dec_main["transfer_optimization"] = old_alerts["alerts"]["transfer_optimization"]
    dec_main["location_risk_scores"] = old_alerts["alerts"]["location_risk_scores"]
    
    # Move spoilage to November period (with warning)
    nov_period = alerts["data_periods"]["november_2025"]["alerts"]
    nov_period["spoilage_events"] = old_alerts["alerts"]["spoilage_prevention"]
    
    # Add date labels to each alert
    for period_key, period_data in alerts["data_periods"].items():
        for alert_type, alert_list in period_data["alerts"].items():
            for alert in alert_list:
                alert["data_period"] = period_data["period_label"]
                alert["data_source"] = period_data["data_source"]
        
        # Count alerts per period
        total = sum(len(v) for v in period_data["alerts"].values())
        period_data["alert_count"] = total
        alerts["summary"]["total_alerts"] += total
    
    # Update summary counts
    for period_data in alerts["data_periods"].values():
        for alert_list in period_data["alerts"].values():
            for alert in alert_list:
                if alert.get('priority') == 'CRITICAL':
                    alerts['summary']['critical'] += 1
                elif alert.get('priority') == 'HIGH':
                    alerts['summary']['high'] += 1
                else:
                    alerts['summary']['medium'] += 1
    
    # Save
    output_path = 'business_alerts_by_period.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2)
    
    print(f"✅ Alerts separated by date period!")
    print(f"\nPeriod Breakdown:")
    for period_key, period_data in alerts["data_periods"].items():
        print(f"  {period_data['period_label']}: {period_data['alert_count']} alerts")
    print(f"\nSaved to: {output_path}")
    
    # Also update the original file
    with open('business_alerts.json', 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2)
    print(f"Updated: business_alerts.json")

if __name__ == "__main__":
    separate_alerts_by_period()
