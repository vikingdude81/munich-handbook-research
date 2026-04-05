import json
import os

def audit_json_files(directory):
    total_files = 0
    valid_files = []
    invalid_files = []

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    total_files += 1
                    if 'chunk_id' in data and isinstance(data['spirits'], list) and isinstance(data['experiments'], list):
                        valid_files.append(filename)
                    else:
                        invalid_files.append((filename, data))
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON in {filename}: {e}")
                invalid_files.append((filename, None))

    print(f"Total files: {total_files}")
    print(f"Valid files: {len(valid_files)}")
    print(f"Invalid files: {len(invalid_files)}")

    if valid_files:
        print("Sample of 3 successful files:")
        for file in valid_files[:3]:
            with open(os.path.join(directory, file), 'r') as f:
                print(json.dumps(json.load(f), indent=2))

    if invalid_files:
        print("Sample of 2 failed files:")
        for file, data in invalid_files[:2]:
            print(f"File: {file}")
            if data is not None:
                print(json.dumps(data, indent=2))
            else:
                print("Failed to decode JSON")

# Example usage
audit_json_files('path/to/json/files')