import csv

def audit_csv_structure():
    csv_path = 'shrinkage_report.csv'
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        header = next(reader)
        expected_cols = len(header)
        print(f"Header has {expected_cols} columns: {header}")
        
        errors = []
        for i, row in enumerate(reader):
            if len(row) != expected_cols:
                errors.append((i+2, len(row), row))
                
        print(f"Total rows with incorrect column count: {len(errors)}")
        if errors:
            print("\nSample errors:")
            for line_no, count, row in errors[:5]:
                print(f"Line {line_no}: expected {expected_cols}, got {count}")
                print(f"Row: {row}")

if __name__ == "__main__":
    audit_csv_structure()
