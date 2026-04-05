# scripts/validate_distilled.py

import json
from collections import defaultdict

def extract_spirit_info(json_data):
    spirit_name = None
    provenance = None
    completeness = 'NEEDS_VERIFICATION'
    
    if isinstance(json_data, dict) and 'spirit' in json_data:
        spirit_name = json_data['spirit']
        completeness = 'complete' if all(k in json_data for k in ('chunk_id', 'raw_quote')) else 'partial'
        
    return {'name': spirit_name, 'provenance': provenance, 'completeness': completeness}

def deduplicate_spirits(spirits):
    seen = set()
    result = []
    
    for s in spirits:
        if s['name'] not in seen:
            seen.add(s['name'])
            result.append(s)
            
    return result

def main():
    all_spirits = defaultdict(list)
    
    # Assuming you have a function to get all JSON files
    json_files = get_all_json_files()
    
    for file_path in json_files:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    all_spirits[item['chunk_id']].append(item)
            elif isinstance(data, dict):
                all_spirits[data['chunk_id']].append(data)
    
    spirits = []
    for ids, items in all_spirits.items():
        for item in items:
            spirits.append(extract_spirit_info(item))
            
    deduplicated_spirits = deduplicate_spirits(spirits)
    
    with open('data/validation/spirit_inventory.json', 'w') as f:
        json.dump(deduplicated_spirits, f, indent=2)

if __name__ == "__main__":
    main()
