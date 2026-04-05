import json
from collections import defaultdict

def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def write_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def aggregate_spirits():
    aggregated_data = defaultdict(dict)
    
    for chunk_id in range(1, 5):  # Assuming there are up to 4 chunks named necro_chunk_X.json
        file_path = f'necro_chunk_{chunk_id}.json'
        data = read_json(file_path)
        
        for entry in data:
            if 'name' not in entry or 'rank' not in entry:
                continue
            
            key = (entry['name'], entry['rank'])
            
            if key in aggregated_data and len(aggregated_data[key]) == 1:
                # If the entry is already in the list, skip it to avoid duplicates
                continue
            
            aggregated_data[key].update(entry)
    
    for key, value in aggregated_data.items():
        if 'chunk_id' not in value or 'raw_quote' not in value:
            value['needs_verification'] = True
    
    write_json(aggregated_data, 'aggregated_spirits.json')

aggregate_spirits()