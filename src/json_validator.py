import json
import os

def validate_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    required_fields = ['spirit_name', 'rank', 'function', 'appearance', 'legion_count', 'conjuration_method', 'experiment_ref', 'page_folio', 'raw_quote']
    
    if not all(field in data for field in required_fields):
        print(f"Missing fields in {file_path}: {required_fields}")
        return False
    
    try:
        json.dumps(data)
        print(f"{file_path} is valid JSON.")
        return True
    except ValueError as e:
        print(f"Invalid JSON in {file_path}: {e}")
        return False

def validate_all_json_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                validate_json(file_path)

# Run the validation script
validate_all_json_files('path_to_your_directory')
