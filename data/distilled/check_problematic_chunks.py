import os
import json

problematic_chunk_ids = []

for filename in os.listdir('data/distilled/'):
    if filename.endswith('.json'):
        file_path = os.path.join('data/distilled/', filename)
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                if not data.get('spirits'):
                    problematic_chunk_ids.append(filename.split('.')[0])
        except json.JSONDecodeError:
            problematic_chunk_ids.append(filename.split('.')[0])

print(problematic_chunk_ids)