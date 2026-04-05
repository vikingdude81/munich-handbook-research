import os
import json

# Define the directory containing JSON files
directory = r'E:\munich_handbook_research\src\distillations'

# Define the expected schema (example)
expected_schema = {
    "field1": str,
    "field2": int,
    "field3": bool
}

# Initialize a dictionary to store field coverage per file
field_coverage = {}

# Iterate over all files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        
        # Read the JSON file
        with open(filepath, 'r') as file:
            data = json.load(file)
            
            # Check for 'write success' message
            if 'write success' in data.get('message', ''):
                # Validate schema compliance
                missing_fields = [field for field, expected_type in expected_schema.items() if field not in data or not isinstance(data[field], expected_type)]
                
                # Update field coverage dictionary
                if filename not in field_coverage:
                    field_coverage[filename] = {'total': 0, 'missing': 0}
                field_coverage[filename]['total'] += len(expected_schema)
                field_coverage[filename]['missing'] += len(missing_fields)

# Print summary table of field coverage per file
print("Summary Table of Field Coverage:")
for filename, coverage in field_coverage.items():
    print(f"{filename}: {coverage['total']} fields total, {coverage['missing']} missing")