import os
import json

def inspect_json_files(directory):
    valid_count = 0
    invalid_count = 0
    problematic_files = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename.endswith('.json'):
            try:
                with open(file_path, 'r') as file:
                    json.load(file)
                valid_count += 1
            except json.JSONDecodeError:
                invalid_count += 1
                problematic_files.append((filename, os.path.getsize(file_path), file.read(200)))

    print(f"Valid JSON files: {valid_count}")
    print(f"Invalid JSON files: {invalid_count}")
    if problematic_files:
        print("Problematic files:")
        for filename, size, content in problematic_files:
            print(f"{filename} - Size: {size} bytes - Content: {content}")

# Example usage
inspect_json_files('distillation_output_directory')
