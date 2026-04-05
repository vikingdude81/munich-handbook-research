import os
import json

# Define the directory containing the JSON files
directory = 'path/to/distill_*.json'

# Initialize a list to store the extracted data
data = []

# Iterate over all JSON files in the directory
for filename in os.listdir(directory):
    if filename.startswith('distill_') and filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        
        # Open and read the JSON file
        with open(filepath, 'r') as file:
            content = json.load(file)
            
            # Extract spirits and experiments
            for entry in content:
                spirit = entry.get('spirit')
                experiment = entry.get('experiment')
                
                # Check if required fields are missing
                if not spirit or not experiment:
                    data.append({
                        'chunk_id': entry.get('chunk_id'),
                        'raw_quote': entry.get('raw_quote'),
                        'provenance': f"{filename}:{entry.get('chunk_id')}",
                        'status': 'NEEDS_VERIFICATION'
                    })
                else:
                    data.append({
                        'spirit': spirit,
                        'experiment': experiment,
                        'provenance': f"{filename}:{entry.get('chunk_id')}"
                    })

# Write the extracted data to src/spirit_vectors.py
with open('src/spirit_vectors.py', 'w') as file:
    file.write("data = " + json.dumps(data, indent=4))