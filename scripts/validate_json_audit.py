import json
from collections import defaultdict
import os

def validate_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            # Add validation logic here
            return True
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Failed to decode JSON or file not found: {e}")
        return False

def audit_json_files(directory):
    results = defaultdict(int)
    unique_spirits = set()
    missing_fields = set()

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            is_valid = validate_json(file_path)
            results['successes' if is_valid else 'failures'] += 1

            # Extract unique spirits and identify missing fields
            with open(file_path, 'r') as file:
                data = json.load(file)
                for item in data:
                    spirit_name = item.get('spirit_name')
                    if spirit_name:
                        unique_spirits.add((spirit_name, item['provenance']))
                    else:
                        missing_fields.add(filename)

    return results, unique_spirits, missing_fields

def main():
    directory_path = 'path/to/your/json/files'
    results, unique_spirits, missing_fields = audit_json_files(directory_path)

    # Output summary report
    print(f"Total successes: {results['successes']}")
    print(f"Total failures: {results['failures']}")

    # List of unique spirits with provenance
    print("Unique Spirits:")
    for spirit in unique_spirits:
        print(f"{spirit[0]} - {spirit[1]}")

    # Files needing manual review due to missing fields
    print("\nFiles needing manual review (missing 'spirit_name' field):")
    for file in missing_fields:
        print(file)

if __name__ == "__main__":
    main()
