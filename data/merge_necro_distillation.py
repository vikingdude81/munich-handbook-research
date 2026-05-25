import os
import json

# Define the directory containing the JSON files
directory = 'data/distillations/necro/'

# Initialize an empty list to store all valid entries
valid_entries = []

# Loop through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        
        # (a) Check parseability
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
        except json.JSONDecodeError:
            print(f"File {filename} is not parseable.")
            continue
        
        # (b) Extract and deduplicate spirits/experiments with provenance
        seen_provenances = set()
        for entry in data['entries']:
            provenance = (entry['chunk_id'], entry.get('raw_quote'))
            if provenance not in seen_provenances:
                valid_entries.append(entry)
                seen_provenances.add(provenance)
        
        # (c) Flag entries missing required fields
        required_fields = {'chunk_id', 'raw_quote'}
        for entry in data['entries']:
            if not required_fields.issubset(entry):
                print(f"Entry in {filename} is missing required fields.")
                continue

# Output a validated merged JSON to data/merged_necro_distillation.json
with open('data/merged_necro_distillation.json', 'w') as file:
    json.dump({'entries': valid_entries}, file, indent=4)
