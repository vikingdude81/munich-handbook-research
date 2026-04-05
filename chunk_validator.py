import os
import json

# Define the directory containing the chunk distillation files
chunk_dir = 'path/to/chunk/distillations'

# Initialize counters
total_chunks = 0
successful = 0
failed = 0
retry_count = 0

# Iterate over all files in the directory
for filename in os.listdir(chunk_dir):
    if filename.endswith('.json'):
        total_chunks += 1
        file_path = os.path.join(chunk_dir, filename)
        
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                successful += 1
        except (FileNotFoundError, json.JSONDecodeError):
            failed += 1
            retry_count += 1
            # Re-distill the chunk
            # Add code here to re-distill the chunk and save it back to the directory

# Log summary
print(f"Total chunks: {total_chunks}")
print(f"Successful: {successful}")
print(f"Failed: {failed}")
print(f"Retry count: {retry_count}")