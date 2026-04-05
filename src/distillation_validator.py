import os
import json

def scan_json_files(directory):
    invalid_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    invalid_files.append((file, str(e)))
    return invalid_files

invalid_json_files = scan_json_files('src/distillations/')
for chunk_id, error in invalid_json_files:
    print(f"Chunk ID: {chunk_id}, Error: {error}")