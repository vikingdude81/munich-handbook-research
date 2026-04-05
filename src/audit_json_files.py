import json
from collections import defaultdict

def audit_json_files(file_paths):
    valid_count = 0
    invalid_count = 0
    missing_count = 0
    errors = defaultdict(list)

    for file_path in file_paths:
        try:
            with open(file_path, 'r') as file:
                json.load(file)
                valid_count += 1
        except FileNotFoundError:
            missing_count += 1
        except json.JSONDecodeError as e:
            invalid_count += 1
            errors[e.lineno].append(file_path)

    print(f"Valid files: {valid_count}")
    print(f"Invalid files: {invalid_count}")
    print(f"Missing files: {missing_count}")

    if errors:
        print("Failed chunks:")
        for line, files in errors.items():
            print(f"Line {line}: {', '.join(files)}")

# Example usage
file_paths = ['path/to/file1.json', 'path/to/file2.json']
audit_json_files(file_paths)
