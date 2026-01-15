import json
import os

def safe_float(x):
    if x is None: return 0.0
    try:
        return float(x)
    except:
        return 0.0

def validate_report():
    # Load files
    with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    with open('n8n_shrinkage_report_minified.json', 'r', encoding='utf-8') as f:
        minified = json.load(f)
    
    ranking = report.get("location_ranking", [])
    
    total_errors = 0
    total_warnings = 0
    issues = []
    
    for loc_entry in ranking:
        loc_name = loc_entry.get("location", "Unknown")
        
        reported_shrink_qty = safe_float(loc_entry.get("total_shrinkage_qty"))
        reported_start = safe_float(loc_entry.get("start_qty"))
        reported_sales = safe_float(loc_entry.get("sales_units"))
        reported_end = safe_float(loc_entry.get("end_qty"))
        
        report_products = loc_entry.get("shrinkage_products", [])
        calc_shrink_qty = sum(safe_float(p.get("shrinkage_qty")) for p in report_products)
        
        loc_issues = []
        
        # Check 1: Product sum matches total
        if abs(reported_shrink_qty - calc_shrink_qty) > 0.01:
            loc_issues.append(f"SHRINK_MISMATCH: Reported={reported_shrink_qty}, Calc={calc_shrink_qty}")
            total_errors += 1
        
        # Check 2: Inventory equation
        expected_shrink = reported_start - reported_sales - reported_end
        if abs(expected_shrink - reported_shrink_qty) > 0.01:
            loc_issues.append(f"INVENTORY_EQ: Expected={expected_shrink}, Reported={reported_shrink_qty}")
            total_warnings += 1
        
        # Check 3: Misplaced products
        misplaced = [p for p in report_products if p.get("location") and p.get("location") != loc_name]
        if misplaced:
            loc_issues.append(f"MISPLACED: {len(misplaced)} products")
            total_errors += 1
        
        if loc_issues:
            issues.append({"location": loc_name, "issues": loc_issues})
    
    # Write results
    with open('VALIDATION_RESULTS.json', 'w', encoding='utf-8') as f:
        json.dump({
            "total_locations": len(ranking),
            "locations_with_issues": len(issues),
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "status": "PASS" if total_errors == 0 else "FAIL",
            "issues": issues[:20]  # First 20
        }, f, indent=2)
    
    print(f"Validated {len(ranking)} locations")
    print(f"Errors: {total_errors}, Warnings: {total_warnings}")
    print(f"Status: {'PASS' if total_errors == 0 else 'FAIL'}")
    print(f"Results saved to VALIDATION_RESULTS.json")

if __name__ == "__main__":
    validate_report()
