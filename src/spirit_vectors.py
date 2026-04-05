import json
import os

def parse_json_files(directory):
    spirit_vectors = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                data = json.load(file)
                
                spirit_entry = {
                    'name': data.get('name', {'needs_verification': True}),
                    'rank': data.get('rank', {'needs_verification': True}),
                    'function': data.get('function', {'needs_verification': True}),
                    'appearance': data.get('appearance', {'needs_verification': True}),
                    'legion_count': data.get('legion_count', {'needs_verification': True}),
                    'conjuration_method': data.get('conjuration_method', {'needs_verification': True}),
                    'experiment_refs': data.get('experiment_refs', [{'needs_verification': True}]),
                    'raw_quote': data.get('raw_quote', {'needs_verification': True})
                }
                
                spirit_entry['provenance'] = {
                    'chunk_id': str(data.get('chunk_id', {'needs_verification': True})),
                    'passage': str(data.get('passage', {'needs_verification': True}))
                }
                
                spirit_vectors.append(spirit_entry)
    
    return spirit_vectors

# Example usage
directory_path = 'path/to/distilled/json/files'
spirit_vectors = parse_json_files(directory_path)

# Save to src/spirit_vectors.py
with open('src/spirit_vectors.py', 'w') as file:
    file.write(f"spirit_vectors = {spirit_vectors}")