import pandas as pd
import json
from datetime import datetime, timedelta
import glob

def build_alert_system():
    """Build comprehensive business alert detection system"""
    
    alerts = {
        "generated_at": datetime.now().isoformat(),
        "period": "December 2025",
        "alert_summary": {
            "total_alerts": 0,
            "critical": 0,
            "high": 0,
            "medium": 0
        },
        "alerts": {
            "theft_detection": [],
            "spoilage_prevention": [],
            "inventory_accuracy": [],
            "transfer_optimization": [],
            "pos_health": [],
            "high_loss_products": [],
            "location_risk_scores": []
        }
    }
    
    # 1. THEFT DETECTION - Ghost Disappearances
    print("Detecting theft (ghost disappearances)...")
    try:
        # Use the verified report data
        with open('n8n_consolidated_report_FINAL_VERIFIED.json', 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        for site in report.get('sites_full', []):
            for product in site.get('products', []):
                shrink = product.get('shrinkage_qty', 0)
                sales = product.get('sales_units', 0)
                
                # Ghost: High shrinkage with zero sales
                if shrink > 5 and sales == 0:
                    alerts['alerts']['theft_detection'].append({
                        "alert_id": f"THEFT-{len(alerts['alerts']['theft_detection'])+1:03d}",
                        "priority": "CRITICAL" if shrink > 20 else "HIGH",
                        "location": site.get('site'),
                        "product_id": product.get('product_id'),
                        "product_name": product.get('product_name'),
                        "units_missing": shrink,
                        "estimated_loss": product.get('shrinkage_value', 0),
                        "evidence": "Zero sales recorded but inventory decreased",
                        "action": "Immediate audit + Review security footage"
                    })
    except Exception as e:
        print(f"Theft detection error: {e}")
    
    # 2. SPOILAGE PREVENTION
    print("Detecting spoilage risks...")
    try:
        # Check if spoilage data exists
        with open('spoilage_report.json', 'r', encoding='utf-8') as f:
            spoilage_data = json.load(f)
        
        for item in spoilage_data.get('risky_items', []):
            exp_date = item.get('expiry_date')
            if exp_date:
                try:
                    exp = datetime.strptime(exp_date, "%Y-%m-%d")
                    days_left = (exp - datetime.now()).days
                    
                    if days_left <= 3:
                        qty = item.get('stock_qty', 0)
                        price = item.get('unit_price', 0)
                        risk_val = qty * price
                        
                        alerts['alerts']['spoilage_prevention'].append({
                            "alert_id": f"SPOIL-{len(alerts['alerts']['spoilage_prevention'])+1:03d}",
                            "priority": "CRITICAL" if days_left <= 1 else "HIGH",
                            "location": item.get('location'),
                            "product": item.get('item_name'),
                            "stock_qty": qty,
                            "days_to_expiry": days_left,
                            "waste_risk_value": round(risk_val, 2),
                            "action": "Bundle/Discount NOW" if days_left == 1 else "Mark for promotion"
                        })
                except:
                    pass
    except Exception as e:
        print(f"Spoilage detection error: {e}")
    
    # 3. INVENTORY ACCURACY ISSUES
    print("Detecting inventory accuracy issues...")
    try:
        # Check for sites with suspicious patterns
        for site in report.get('sites_full', []):
            total_products = len(site.get('products', []))
            zero_shrink_count = sum(1 for p in site.get('products', []) if p.get('shrinkage_qty', 0) == 0)
            
            # If 80%+ products have zero shrinkage, likely counting issue
            if total_products > 10 and (zero_shrink_count / total_products) > 0.8:
                alerts['alerts']['inventory_accuracy'].append({
                    "alert_id": f"INV-{len(alerts['alerts']['inventory_accuracy'])+1:03d}",
                    "priority": "HIGH",
                    "location": site.get('site'),
                    "issue": "Suspicious zero-shrinkage pattern",
                    "products_affected": zero_shrink_count,
                    "total_products": total_products,
                    "evidence": f"{int((zero_shrink_count/total_products)*100)}% of products show zero shrinkage",
                    "action": "Verify counting system + Manual audit"
                })
    except Exception as e:
        print(f"Inventory accuracy error: {e}")
    
    # 4. TRANSFER OPTIMIZATION
    print("Detecting transfer opportunities...")
    # This requires cross-site analysis - simplified version
    try:
        product_by_site = {}
        for site in report.get('sites_full', []):
            for product in site.get('products', []):
                pid = product.get('product_id')
                if pid not in product_by_site:
                    product_by_site[pid] = []
                product_by_site[pid].append({
                    'site': site.get('site'),
                    'shrink': product.get('shrinkage_qty', 0),
                    'sales': product.get('sales_units', 0),
                    'value': product.get('shrinkage_value', 0)
                })
        
        # Find products with high shrink at one site and high sales at another
        for pid, sites in product_by_site.items():
            if len(sites) >= 2:
                high_shrink = [s for s in sites if s['shrink'] > 10 and s['sales'] == 0]
                high_sales = [s for s in sites if s['sales'] > 20]
                
                if high_shrink and high_sales:
                    alerts['alerts']['transfer_optimization'].append({
                        "alert_id": f"XFER-{len(alerts['alerts']['transfer_optimization'])+1:03d}",
                        "priority": "MEDIUM",
                        "product_id": pid,
                        "from_location": high_shrink[0]['site'],
                        "to_location": high_sales[0]['site'],
                        "units_available": high_shrink[0]['shrink'],
                        "potential_savings": high_shrink[0]['value'],
                        "action": f"Transfer {int(high_shrink[0]['shrink'])} units to prevent waste"
                    })
    except Exception as e:
        print(f"Transfer optimization error: {e}")
    
    # 5. POS HEALTH - Check for missing sales data
    print("Detecting POS health issues...")
    try:
        for site in report.get('sites_full', []):
            metrics = site.get('metrics', {})
            sales_val = metrics.get('sales_value_est', 0)
            
            # If sales value is suspiciously low or zero
            if sales_val == 0:
                alerts['alerts']['pos_health'].append({
                    "alert_id": f"POS-{len(alerts['alerts']['pos_health'])+1:03d}",
                    "priority": "CRITICAL",
                    "location": site.get('site'),
                    "issue": "Zero sales recorded",
                    "evidence": "No sales data available for entire period",
                    "action": "Check POS system status + Verify data feeds"
                })
    except Exception as e:
        print(f"POS health error: {e}")
    
    # 6. HIGH-LOSS PRODUCTS
    print("Identifying high-loss products...")
    try:
        product_totals = {}
        for site in report.get('sites_full', []):
            for product in site.get('products', []):
                pid = product.get('product_id')
                if pid not in product_totals:
                    product_totals[pid] = {
                        'name': product.get('product_name'),
                        'total_shrink_qty': 0,
                        'total_shrink_value': 0,
                        'site_count': 0
                    }
                product_totals[pid]['total_shrink_qty'] += product.get('shrinkage_qty', 0)
                product_totals[pid]['total_shrink_value'] += product.get('shrinkage_value', 0)
                product_totals[pid]['site_count'] += 1
        
        # Sort by value and take top 10
        sorted_products = sorted(product_totals.items(), key=lambda x: x[1]['total_shrink_value'], reverse=True)[:10]
        
        for pid, data in sorted_products:
            if data['total_shrink_value'] > 50:
                alerts['alerts']['high_loss_products'].append({
                    "alert_id": f"HLOSS-{len(alerts['alerts']['high_loss_products'])+1:03d}",
                    "priority": "HIGH" if data['total_shrink_value'] > 200 else "MEDIUM",
                    "product_id": pid,
                    "product_name": data['name'],
                    "total_units_lost": data['total_shrink_qty'],
                    "total_value_lost": round(data['total_shrink_value'], 2),
                    "sites_affected": data['site_count'],
                    "action": "Investigate: Theft ring? Damaged packaging? Expiry issues?"
                })
    except Exception as e:
        print(f"High-loss products error: {e}")
    
    # 7. LOCATION RISK SCORING
    print("Calculating location risk scores...")
    try:
        for site in report.get('sites_full', []):
            metrics = site.get('metrics', {})
            
            # Calculate risk score
            ghost_count = sum(1 for p in site.get('products', []) 
                            if p.get('shrinkage_qty', 0) > 5 and p.get('sales_units', 0) == 0)
            shrink_val = metrics.get('shrink_value', 0)
            loss_rate = metrics.get('loss_rate_pct', 0)
            
            risk_score = (ghost_count * 10) + (shrink_val / 10) + (loss_rate * 2)
            
            if risk_score > 30:
                priority = "CRITICAL" if risk_score > 70 else "HIGH" if risk_score > 50 else "MEDIUM"
                
                alerts['alerts']['location_risk_scores'].append({
                    "alert_id": f"RISK-{len(alerts['alerts']['location_risk_scores'])+1:03d}",
                    "priority": priority,
                    "location": site.get('site'),
                    "risk_score": round(risk_score, 1),
                    "ghost_disappearances": ghost_count,
                    "total_loss_value": shrink_val,
                    "loss_rate_pct": loss_rate,
                    "audit_priority": metrics.get('audit_priority', 'MEDIUM'),
                    "action": "Emergency audit within 24 hours" if priority == "CRITICAL" else "Schedule audit within 7 days"
                })
    except Exception as e:
        print(f"Location risk scoring error: {e}")
    
    # Update summary counts
    for alert_type in alerts['alerts'].values():
        for alert in alert_type:
            alerts['alert_summary']['total_alerts'] += 1
            if alert['priority'] == 'CRITICAL':
                alerts['alert_summary']['critical'] += 1
            elif alert['priority'] == 'HIGH':
                alerts['alert_summary']['high'] += 1
            else:
                alerts['alert_summary']['medium'] += 1
    
    # Save to JSON
    output_path = 'business_alerts.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2)
    
    print(f"\n✅ Alert system complete!")
    print(f"Total Alerts: {alerts['alert_summary']['total_alerts']}")
    print(f"  - Critical: {alerts['alert_summary']['critical']}")
    print(f"  - High: {alerts['alert_summary']['high']}")
    print(f"  - Medium: {alerts['alert_summary']['medium']}")
    print(f"\nSaved to: {output_path}")

if __name__ == "__main__":
    build_alert_system()
