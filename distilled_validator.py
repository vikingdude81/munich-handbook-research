import os
import json

directory = 'distilled/'
chunk_count = 39
files_found = 0
valid_files = 0
missing_files = 0
corrupted_files = 0

for i in range(1, chunk_count + 1):
    filename = f'chunk_{i}.json'
    filepath = os.path.join(directory, filename)
    
    if not os.path.exists(filepath):
        missing_files += 1
        continue
    
    files_found += 1
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            if not data:
                corrupted_files += 1
            else:
                valid_files += 1
    except json.JSONDecodeError:
        corrupted_files += 1

summary = {
    'total_found': files_found,
    'valid': valid_files,
    'missing': missing_files,
    'corrupted': corrupted_files
}

print(summary)
