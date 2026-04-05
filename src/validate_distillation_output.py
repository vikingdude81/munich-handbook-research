import os
import json

def validate_json(file_path):
    try:
        with open(file_path, 'r') as file:
            json.load(file)
        return True
    except json.JSONDecodeError:
        print(f"Invalid JSON in {file_path}")
        return False

def check_required_fields(data):
    required_fields = ['spirits', 'experiments']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        print(f"Missing fields: {missing_fields} in {data.get('filename')}")
        return False
    return True

def scan_directory(directory):
    valid_files = []
    invalid_files = []
    missing_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                data = {'filename': file}
                with open(file_path, 'r') as f:
                    data.update(json.load(f))
                
                if validate_json(file_path) and check_required_fields(data):
                    valid_files.append(file_path)
                else:
                    invalid_files.append(file_path)

    return valid_files, invalid_files, missing_files

def main():
    output_dir = 'distillation_output'
    valid_files, invalid_files, missing_files = scan_directory(output_dir)

    if invalid_files or missing_files:
        print("Validation failed:")
        if invalid_files:
            print(f"Invalid JSON files: {invalid_files}")
        if missing_files:
            print(f"Missing required fields in: {missing_files}")
        exit(1)
    else:
        print("All files are valid.")

if __name__ == "__main__":
    main()
