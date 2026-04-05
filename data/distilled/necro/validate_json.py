import os
import json

# Define required keys
required_keys = ['spirit_name', 'rank', 'function', 'appearance', 'legion_count', 'conjuration_method', 'experiment_ref', 'page_folio', 'raw_quote']

# Initialize counters and lists
total_files = 0
valid_files = 0
invalid_files = 0
missing_fields = []
malformed_entries = []
NEEDS_VERIFICATION = []

# Function to validate JSON file
def validate_json(file_path):
    global valid_files, invalid_files, missing_fields, malformed_entries, NEEDS_VERIFICATION
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            if all(key in data for key in required_keys):
                valid_files += 1
            else:
                missing_fields.extend([key for key in required_keys if key not in data])
                invalid_files += 1
    except json.JSONDecodeError:
        malformed_entries.append(file_path)
        invalid_files += 1

# Iterate over all JSON files in the directory
for filename in os.listdir('data/distilled/necro/'):
    if filename.endswith('.json'):
        total_files += 1
        validate_json(os.path.join('data/distilled/necro/', filename))

# Generate summary report
summary_report = {
    'total_files': total_files,
    'valid_files': valid_files,
    'invalid_files': invalid_files,
    'missing_fields': missing_fields,
    'malformed_entries': malformed_entries,
    'NEEDS_VERIFICATION': NEEDS_VERIFICATION
}

print(json.dumps(summary_report, indent=4))
