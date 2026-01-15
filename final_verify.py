import json
import re

json_path = "n8n_consolidated_report_final.json"
with open(json_path, 'r') as f:
    data = json.load(f)

issues = []

def check(p, loc):
    p_id = p.get("product_id", "")
    p_name = p.get("product_name", "").strip()
    
    # Is it a code? (AVR... or PC...)
    is_code = re.match(r'^(AVR|PC)\d+$', p_name)
    is_empty = not p_name
    
    if is_code or is_empty:
        issues.append({
            "location": loc,
            "id": p_id,
            "name": p_name,
            "type": "EMPTY" if is_empty else "CODE"
        })

if "location_ranking" in data:
    for loc in data["location_ranking"]:
        l_name = loc.get("location", "Unknown")
        for p in loc.get("shrinkage_products", []): check(p, l_name)
        opts = loc.get("transfer_opportunities", {})
        for p in opts.get("outbound_suggestions", []): check(p, l_name)
        for p in opts.get("inbound_opportunities", []): check(p, l_name)

if "network_transfer_optimization" in data:
    for p in data["network_transfer_optimization"].get("top_recommendations", []):
        check(p, "Network Top Rec")

print(f"Total Issues Found: {len(issues)}")
if issues:
    print("\nFirst 10 issues:")
    for iss in issues[:10]:
        print(f"Loc: {iss['location']} | ID: {iss['id']} | Name: {iss['name']} ({iss['type']})")

with open("final_verification_results.txt", "w") as f:
    f.write(f"Total Issues (Generic/Missing Names): {len(issues)}\n")
    for iss in issues:
        f.write(f"{iss['location']} | {iss['id']} | {iss['name']}\n")
