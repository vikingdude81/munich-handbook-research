import os
import json

def validate_chunk(chunk):
    required_fields = ['id', 'data']
    missing_fields = [field for field in required_fields if field not in chunk]
    return missing_fields, {'needs_verification': bool(missing_fields)}

def consolidate_chunks(directory):
    consolidated_data = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r') as file:
                chunk = json.load(file)
                missing_fields, verification_flag = validate_chunk(chunk)
                if not missing_fields:
                    consolidated_data.append(chunk)
                else:
                    chunk.update(verification_flag)
    return consolidated_data

# Usage
directory_path = 'distilled/'
validated_dataset = consolidate_chunks(directory_path)
print(json.dumps(validated_dataset, indent=2))
