import json
import os

# List of required fields
required_fields = ['spirit_name', 'raw_quote', 'page_ref']

# Function to validate a single JSON file
def validate_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    errors = []
    for entry in data:
        missing_fields = [field for field in required_fields if field not in entry]
        if missing_fields:
            errors.append(f"Missing fields: {missing_fields}")
        
        # Add more validation checks here (e.g., type checking, format validation)

    return errors

# Function to validate all JSON files
def validate_all_files(file_paths):
    for file_path in file_paths:
        errors = validate_file(file_path)
        if errors:
            print(f"Errors in {file_path}:")
            for error in errors:
                print(error)
            print()

# List of JSON file paths (replace with actual paths)
json_files = [
    'path/to/file1.json',
    'path/to/file2.json',
    # Add more file paths here
]

# Prioritize chunks with errors from iterations 60, 63, 66–67
prioritized_files = [file for file in json_files if 'iteration_60' in file or 'iteration_63' in file or ('iteration_66' in file and 'iteration_67' in file)]

# Validate prioritized files first
validate_all_files(prioritized_files)

# Validate remaining files
validate_all_files([file for file in json_files if file not in prioritized_files])
