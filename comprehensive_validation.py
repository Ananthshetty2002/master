import json
import os
import sys

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def safe_float(x):
    """Safely convert to float, handling None"""
    if x is None: return 0.0
    try:
        return float(x)
    except:
        return 0.0

def validate_report():
    """Comprehensive validation of n8n_consolidated_report_final_fixed.json"""
    
    print("="*80)
    print("COMPREHENSIVE VALIDATION REPORT")
    print("="*80)
    
    # Load the report to validate
    report_file = 'n8n_consolidated_report_final_fixed.json'
    if not os.path.exists(report_file):
        print(f"ERROR: {report_file} not found!")
        return
    
    with open(report_file, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # Load source data
    minified_file = 'n8n_shrinkage_report_minified.json'
    if not os.path.exists(minified_file):
        print(f"ERROR: {minified_file} not found!")
        return
        
    with open(minified_file, 'r', encoding='utf-8') as f:
        minified = json.load(f)
    
    source_products = minified.get("data", [])
    
    # Group source products by location
    source_by_location = {}
    for p in source_products:
        loc = p.get("location")
        if loc not in source_by_location:
            source_by_location[loc] = []
        source_by_location[loc].append(p)
    
    print(f"\nSource Data: {len(source_products)} total products across {len(source_by_location)} locations")
    
    # Get location ranking from report
    ranking = report.get("location_ranking", [])
    print(f"Report Data: {len(ranking)} locations\n")
    
    # Validation results
    total_errors = 0
    total_warnings = 0
    locations_validated = 0
    locations_with_issues = []
    
    print("="*80)
    print("VALIDATING ALL LOCATIONS...")
    print("="*80)
    
    for loc_entry in ranking:
        loc_name = loc_entry.get("location", "Unknown")
        
        # Get reported values
        reported_shrink_qty = safe_float(loc_entry.get("total_shrinkage_qty"))
        reported_shrink_val = safe_float(loc_entry.get("total_shrinkage_value"))
        reported_sales = safe_float(loc_entry.get("sales_units"))
        reported_start = safe_float(loc_entry.get("start_qty"))
        reported_end = safe_float(loc_entry.get("end_qty"))
        
        # Get products from report
        report_products = loc_entry.get("shrinkage_products", [])
        
        # Calculate from report products
        calc_shrink_qty = sum(safe_float(p.get("shrinkage_qty")) for p in report_products)
        calc_shrink_val = sum(safe_float(p.get("shrinkage_value")) for p in report_products)
        
        has_error = False
        errors_for_loc = []
        
        # Validate shrinkage qty matches sum of products
        if abs(reported_shrink_qty - calc_shrink_qty) > 0.01:
            errors_for_loc.append(f"Shrink Qty mismatch: Reported={reported_shrink_qty}, Calculated={calc_shrink_qty}")
            total_errors += 1
            has_error = True
        
        # Validate shrinkage value
        if abs(reported_shrink_val - calc_shrink_val) > 0.01:
            errors_for_loc.append(f"Shrink Value mismatch: Reported=${reported_shrink_val:,.2f}, Calculated=${calc_shrink_val:,.2f}")
            total_errors += 1
            has_error = True
        
        # Validate inventory equation: Shrinkage = Start - Sales - End
        expected_shrink = reported_start - reported_sales - reported_end
        if abs(expected_shrink - reported_shrink_qty) > 0.01:
            errors_for_loc.append(f"Inventory equation: Expected={expected_shrink}, Reported={reported_shrink_qty}")
            total_warnings += 1
            has_error = True
        
        # Check for misplaced products
        misplaced = [p for p in report_products if p.get("location") and p.get("location") != loc_name]
        if misplaced:
            errors_for_loc.append(f"{len(misplaced)} misplaced products found")
            total_errors += 1
            has_error = True
        
        if has_error:
            locations_with_issues.append({
                "location": loc_name,
                "errors": errors_for_loc
            })
        
        locations_validated += 1
    
    # Summary
    print(f"\n{'='*80}")
    print("VALIDATION SUMMARY")
    print(f"{'='*80}")
    print(f"Locations Validated: {locations_validated}")
    print(f"Locations with Issues: {len(locations_with_issues)}")
    print(f"Total Errors: {total_errors}")
    print(f"Total Warnings: {total_warnings}")
    
    if locations_with_issues:
        print(f"\n{'='*80}")
        print("LOCATIONS WITH ISSUES:")
        print(f"{'='*80}")
        for item in locations_with_issues[:10]:  # Show first 10
            print(f"\nLocation: {item['location']}")
            for err in item['errors']:
                print(f"  - {err}")
    
    if total_errors == 0 and total_warnings == 0:
        print("\n" + "="*80)
        print("SUCCESS: ALL VALIDATIONS PASSED! Report is 100% accurate.")
        print("="*80)
    elif total_errors == 0:
        print(f"\nWARNING: Report has {total_warnings} warnings but no critical errors.")
    else:
        print(f"\nERROR: Report has {total_errors} errors that need to be fixed!")
    
    print(f"\n{'='*80}\n")
    
    return total_errors, total_warnings

if __name__ == "__main__":
    validate_report()
