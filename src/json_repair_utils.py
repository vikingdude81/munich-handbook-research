import os
import json
import json5
import re

def scan_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r') as file:
                    json.load(file)
            except json.JSONDecodeError as e:
                print(f"Malformed JSON in {filename}:")
                print(f"Line: {e.lineno}, Column: {e.colno}")
                print(f"Raw Preview: {file.read(100)}")
                
                # Attempt repair using json5
                try:
                    with open(file_path, 'r') as file:
                        data = json5.load(file)
                    with open(file_path, 'w') as file:
                        json.dump(data, file, indent=4)
                    print(f"Repaired {filename} using json5.")
                except Exception as e:
                    print(f"Failed to repair {filename} using json5: {e}")
                
                # Attempt regex-based cleanup
                try:
                    with open(file_path, 'r') as file:
                        content = file.read()
                    cleaned_content = re.sub(r'\s*//.*', '', content)  # Remove comments
                    cleaned_content = re.sub(r'\s*/\*[\s\S]*?\*/\s*', '', cleaned_content)  # Remove multi-line comments
                    with open(file_path, 'w') as file:
                        file.write(cleaned_content)
                    print(f"Repaired {filename} using regex-based cleanup.")
                except Exception as e:
                    print(f"Failed to repair {filename} using regex-based cleanup: {e}")

# Example usage
scan_json_files('distill')