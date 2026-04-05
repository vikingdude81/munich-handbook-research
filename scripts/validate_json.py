import os
import json

def is_valid_json(file_path):
    try:
        with open(file_path, 'r') as file:
            json.load(file)
        return True
    except (json.JSONDecodeError, FileNotFoundError):
        return False

directory = 'distillations/necro/'
valid_files = 0
missing_files = []
invalid_files = []

for filename in os.listdir(directory):
    if filename.endswith('.json'):
        file_path = os.path.join(directory, filename)
        if is_valid_json(file_path):
            valid_files += 1
        else:
            invalid_files.append(filename)

if valid_files == 39 and not invalid_files:
    print("All 39 valid JSON files exist.")
else:
    print(f"Expected 39 valid JSON files, found {valid_files}.")
    if missing_files:
        print("Missing files:", missing_files)
    if invalid_files:
        print("Invalid files:", invalid_files)