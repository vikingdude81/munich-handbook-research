import os
import json

# Define the range of expected chunk IDs
expected_ids = set(range(39))

# Initialize a list to store the results
results = []

# Scan all JSON files in the directory
for filename in os.listdir('data/distillations/'):
    if filename.endswith('.json'):
        # Extract the chunk_id from the filename
        try:
            chunk_id = int(filename.split('_')[0])
        except ValueError:
            results.append({'chunk_id': None, 'status': 'invalid_json', 'error_message': 'Invalid chunk ID format'})
            continue
        
        # Check if the chunk_id is within the expected range
        if chunk_id not in expected_ids:
            results.append({'chunk_id': chunk_id, 'status': 'missing', 'error_message': 'Chunk ID out of expected range'})
            continue
        
        # Validate the JSON file
        try:
            with open(os.path.join('data/distillations/', filename), 'r') as file:
                json.load(file)
            results.append({'chunk_id': chunk_id, 'status': 'ok', 'error_message': None})
        except json.JSONDecodeError:
            results.append({'chunk_id': chunk_id, 'status': 'invalid_json', 'error_message': 'Invalid JSON format'})

# Output the summary table
print("Chunk ID\tStatus\tError Message")
for result in results:
    print(f"{result['chunk_id']}\t{result['status']}\t{result['error_message']}")