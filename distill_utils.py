import os
import json

def run_integrity_check(directory):
    invalid_files = []
    empty_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if not data:
                        empty_files.append(filename)
                    elif 'chunk_id' not in data or not data['chunk_id']:
                        invalid_files.append(filename)
            except json.JSONDecodeError:
                invalid_files.append(filename)

    print("Invalid files:", invalid_files)
    print("Empty files:", empty_files)
    return [filename.split('.')[0] for filename in invalid_files + empty_files]

# Run the integrity check
invalid_chunk_ids = run_integrity_check('E:/munich_handbook_research/distillations/')
print("Chunk IDs needing re-distillation:", invalid_chunk_ids)
