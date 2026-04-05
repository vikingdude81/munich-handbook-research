import os
import json

def verify_distillation_completeness(directory, expected_count):
    files = [f for f in os.listdir(directory) if f.endswith('.json')]
    if len(files) != expected_count:
        print(f"Error: Expected {expected_count} JSON files, found {len(files)}")
        return False
    
    missing_files = []
    malformed_files = []
    
    for file in files:
        file_path = os.path.join(directory, file)
        try:
            with open(file_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError:
            malformed_files.append(file)
        except FileNotFoundError:
            missing_files.append(file)
    
    if missing_files or malformed_files:
        print("Missing files:", missing_files)
        print("Malformed files:", malformed_files)
        return False
    
    print("All JSON files are valid.")
    return True

# Usage
verify_distillation_completeness('distill/', 39)
