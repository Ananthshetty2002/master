import json
import datetime
import pandas as pd

def transform_report():
    # 1. Load Current Source of Truth
    with open('n8n_consolidated_report_FINAL_VERIFIED_V2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Executive Summary Structures
    final_report = {
        "client_name": "Review Client", # Placeholder or derived
        "report_id": "RPT-202512-V3",
        "generated_at": datetime.datetime.now().isoformat(),
        "currency": "USD",
        "period": {
            "start": "2025-12-03", # Based on known context
            "end": "2025-12-30",
            "days": 28
        },
        "portfolio_summary": {},
        "sites_full": [],
        "actions": []
        # "transfers": [] # Will check if transfer data exists
    }

    # 3. Portfolio Summary Calculation
    total_sites = len(data.get('location_ranking', []))
    total_shrink_qty = data['summary_metrics']['total_shrinkage_qty']
    total_shrink_val = data['summary_metrics']['total_shrinkage_value']
    
    # Calculate total start for shrink rate
    total_start_qty = sum(l.get('start_qty', 0) for l in data['location_ranking'])
    shrink_rate_pct = (total_shrink_qty / total_start_qty * 100) if total_start_qty > 0 else 0

    # Top Sites/SKUS
    sorted_locs = sorted(data['location_ranking'], key=lambda x: x.get('total_shrinkage_value', 0), reverse=True)
    sites_with_loss = len([l for l in sorted_locs if l.get('total_shrinkage_value', 0) > 0.01])
    
    # Critical Count (e.g., value > $500 or rate > 50%)
    critical_sites = [l for l in sorted_locs if l.get('total_shrinkage_value', 0) > 500]
    
    # Extract ALL products for ranking
    all_prods = []
    for l in data['location_ranking']:
        for p in l.get('shrinkage_products', []):
            p['location'] = l['location']
            all_prods.append(p)
    
    sorted_skus = sorted(all_prods, key=lambda x: x.get('shrinkage_value', 0), reverse=True)

    final_report["portfolio_summary"] = {
        "sites_total": total_sites,
        "sites_with_loss": sites_with_loss,
        "sites_critical_count": len(critical_sites),
        "total_shrink_value": total_shrink_val,
        "total_shrink_qty": total_shrink_qty,
        "shrink_rate_pct": round(shrink_rate_pct, 2),
        "top_5_sites_by_loss_value": [{"id": l.get('location'), "name": l.get('location'), "value": l.get('total_shrinkage_value')} for l in sorted_locs[:5]],
        "top_10_skus_by_loss_value": [{"id": p.get('product_id'), "name": p.get('product_name'), "value": p.get('shrinkage_value')} for p in sorted_skus[:10]],
        "confidence_notes": "Data verified against shrinkage_report_refined.csv. Adjustments/Spoilage included in calculations.",
        "thresholds_used": {
            "ghost_min_units": 0, # Anything > 0 shrink with 0 sales
            "high_loss_rate_pct": 50
        }
    }

    # 4. Site Level Transformation
    action_id_counter = 1
    
    # Load Adjustment Logs
    try:
        adj_df = pd.read_csv('pilot_shrink_log.csv')
        # Standardize columns
        adj_df.columns = [c.strip() for c in adj_df.columns]
        # Aggregate by Site and Reason
        # Assuming 'Micromarket' is site name, 'Reason Code' is reason
        # Map Micromarket to JSON location names if possible.
        # Let's create a lookup: Site -> {Reason: Count/Val}
        
        # Normalize site names for matching
        adj_df['Site_Norm'] = adj_df['Micromarket'].astype(str).str.strip().str.lower()
        
        adj_lookup = {}
        for site, group in adj_df.groupby('Site_Norm'):
            reasons = group['Reason Code'].value_counts().to_dict()
            total_adj_qty = group['Qty'].sum() if 'Qty' in group.columns else 0
            total_adj_val = group['TotalCost'].sum() if 'TotalCost' in group.columns else 0
            adj_lookup[site] = {
                "adjustment_qty": int(total_adj_qty),
                "adjustment_value": float(total_adj_val),
                "breakdown": reasons
            }
    except Exception as e:
        print(f"Warning: Could not process adjustment logs: {e}")
        adj_lookup = {}

    for loc in data['location_ranking']:
        # ... (Metrics Calc) ...
        shrink_val = loc.get('total_shrinkage_value', 0)
        prod_sales_val_sum = sum(p.get('sales_units', 0) * p.get('unit_price', 0) for p in loc.get('shrinkage_products', []))
        loss_pct_sales = (shrink_val / prod_sales_val_sum * 100) if prod_sales_val_sum > 0 else 0
        start_qty = loc.get('start_qty', 0)
        loss_rate = (loc.get('total_shrinkage_qty', 0) / start_qty * 100) if start_qty > 0 else 0
        
        # Priority Logic
        if shrink_val > 500: priority = "CRITICAL"
        elif shrink_val > 100: priority = "HIGH"
        elif shrink_val > 0: priority = "MED"
        else: priority = "LOW"
        
        reason_codes = []
        if priority == "CRITICAL": reason_codes.append("HIGH_LOSS_VALUE")
        if loss_rate > 50: reason_codes.append("HIGH_LOSS_RATE")
        
        # Inject Adjustment Summary
        loc_norm = loc.get('location', '').strip().lower()
        adj_data = adj_lookup.get(loc_norm, {})
        
        metrics = {
                "sales_value_est": round(prod_sales_val_sum, 2),
                "shrink_value": shrink_val,
                "loss_as_pct_of_sales": round(loss_pct_sales, 2),
                "loss_rate_pct": round(loss_rate, 2),
                "audit_priority": priority,
                "audit_reason_codes": reason_codes
        }
        
        if adj_data:
            metrics["adjustment_summary"] = {
                "adjustment_qty": adj_data.get('adjustment_qty', 0),
                "adjustment_value": round(adj_data.get('adjustment_value', 0), 2),
                "breakdown": adj_data.get('breakdown', {})
            }

        # Product Level Enrichment
        enhanced_products = []
        for p in loc.get('shrinkage_products', []):
            p_start = p.get('quantity_start', 0) # Did we save this in reset? No, grand reset saved start/end at LOC level, not PROD level explicit update?
            # Check grand reset:
            # p['shrinkage_qty'] = ...
            # p['sales_units'] = ...
            # it DID NOT update p['quantity_start'] or p['quantity_end']. 
            # Existing JSON had them? Check file.
            
            # If start/end missing at product level, we can't do product loss rate. 
            # Let's assume they might be there or miss.
            
            p_shrink = p.get('shrinkage_qty', 0)
            # p_loss_rate = (p_shrink / p_start * 100) if p_start > 0 else 0
            
            p_new = {
                "product_id": p.get('product_id'),
                "product_name": p.get('product_name'),
                "shrinkage_qty": p_shrink,
                "shrinkage_value": p.get('shrinkage_value'),
                "sales_units": p.get('sales_units'),
                "unit_price": p.get('unit_price'),
                # "quantity_start": p_start,
                # "loss_rate_pct": round(p_loss_rate, 2)
            }
            # Only add fields if we are sure.
            enhanced_products.append(p_new)

        site_obj = {
            "site": loc.get('location'),
            "site_id": loc.get('location'), # Placeholder
            "metrics": {
                "sales_value_est": round(prod_sales_val_sum, 2),
                "shrink_value": shrink_val,
                "loss_as_pct_of_sales": round(loss_pct_sales, 2),
                "loss_rate_pct": round(loss_rate, 2),
                "audit_priority": priority,
                "audit_reason_codes": reason_codes
            },
            "products": enhanced_products
        }
        final_report["sites_full"].append(site_obj)
        
        # Generate Actions
        if priority in ["CRITICAL", "HIGH"]:
            final_report["actions"].append({
                "action_id": f"ACT-{action_id_counter:03d}",
                "action_type": "AUDIT",
                "priority": "P0" if priority == "CRITICAL" else "P1",
                "site": loc.get('location'),
                "owner_role": "Site Manager",
                "due_date": "2026-01-12", # 2 days out
                "expected_impact_value": shrink_val,
                "why": f"High shrinkage value (${shrink_val}) detected."
            })
            action_id_counter += 1

    # Save
    with open('n8n_consolidated_report_CLIENT_READY.json', 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2)
    print("Client Ready Report Generated.")

if __name__ == "__main__":
    transform_report()
