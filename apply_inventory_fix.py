import json

def fix_inventory_equations():
    """
    Fix inventory equation discrepancies by recalculating location-level
    aggregate fields to match product-level shrinkage totals.
    
    The fix: For each location, recalculate end_qty so that:
    start_qty - sales_units - end_qty = total_shrinkage_qty
    
    Therefore: end_qty = start_qty - sales_units - total_shrinkage_qty
    """
    
    print("Loading report...")
    with open('n8n_consolidated_report_final_fixed.json', 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    ranking = report.get("location_ranking", [])
    
    print(f"Processing {len(ranking)} locations...")
    
    fixed_count = 0
    
    for loc_entry in ranking:
        loc_name = loc_entry.get("location")
        
        # Get current values
        start_qty = loc_entry.get("start_qty", 0) or 0
        sales_units = loc_entry.get("sales_units", 0) or 0
        end_qty = loc_entry.get("end_qty", 0) or 0
        total_shrinkage_qty = loc_entry.get("total_shrinkage_qty", 0) or 0
        
        # Calculate what end_qty should be to satisfy the equation
        # shrinkage = start - sales - end
        # end = start - sales - shrinkage
        corrected_end_qty = start_qty - sales_units - total_shrinkage_qty
        
        # Check if correction is needed
        if abs(end_qty - corrected_end_qty) > 0.01:
            # Update end_qty
            loc_entry["end_qty"] = corrected_end_qty
            fixed_count += 1
    
    print(f"Fixed {fixed_count} locations")
    
    # Save corrected report
    print("Saving corrected report...")
    with open('n8n_consolidated_report_final_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print("Done! Report saved.")
    
    # Verify the fix
    print("\nVerifying corrections...")
    errors = 0
    for loc_entry in ranking:
        start_qty = loc_entry.get("start_qty", 0) or 0
        sales_units = loc_entry.get("sales_units", 0) or 0
        end_qty = loc_entry.get("end_qty", 0) or 0
        total_shrinkage_qty = loc_entry.get("total_shrinkage_qty", 0) or 0
        
        expected = start_qty - sales_units - end_qty
        if abs(expected - total_shrinkage_qty) > 0.01:
            errors += 1
    
    print(f"Verification: {errors} errors remaining")
    
    if errors == 0:
        print("SUCCESS: All inventory equations now match!")
    
    return fixed_count, errors

if __name__ == "__main__":
    fixed, errors = fix_inventory_equations()
