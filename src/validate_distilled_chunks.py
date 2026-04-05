import os
import json

# Directory containing distilled JSON files
output_dir = 'distilled/necro/'

# Initialize counters and error dictionary
valid_count = 0
failed_count = 0
error_types = {}

# Iterate through each file in the directory
for filename in os.listdir(output_dir):
    if filename.endswith('.json'):
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'r') as file:
                json.load(file)
            valid_count += 1
        except json.JSONDecodeError as e:
            failed_count += 1
            error_type = str(e).split(':')[0].strip()
            if error_type in error_types:
                error_types[error_type] += 1
            else:
                error_types[error_type] = 1

# Print results
print(f"Valid JSON chunks: {valid_count}")
print(f"Failed JSON chunks: {failed_count}")
print("Error types:")
for error, count in error_types.items():
    print(f"{error}: {count}")

# Inspect chunk #17's raw input and partial outputs
chunk_17_input = 'distilled/necro/chunk_17_raw.txt'
chunk_17_output = 'distilled/necro/chunk_17_output.json'

if os.path.exists(chunk_17_input):
    with open(chunk_17_input, 'r') as file:
        print("Chunk #17 raw input:")
        print(file.read())

if os.path.exists(chunk_17_output):
    try:
        with open(chunk_17_output, 'r') as file:
            print("Chunk #17 partial output:")
            print(json.load(file))
    except json.JSONDecodeError as e:
        print(f"Failed to parse chunk #17 partial output: {e}")