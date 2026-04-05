import json

def validate_and_aggregate(json_files):
    spirits = []
    for file in json_files:
        try:
            with open(file, 'r') as f:
                data = json.load(f)
            if 'spirit_name' in data and 'rank' in data and 'provenance' in data:
                provenance = data['provenance']
                if isinstance(provenance, dict) and all(k in provenance for k in ['chunk_id', 'raw_quote']):
                    spirits.append(data)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    return spirits

# Example usage (replace with actual file paths)
json_files = ["spirit1.json", "spirit2.json"]
aggregated_spirits = validate_and_aggregate(json_files)

with open("temp_spirit_inventory.json", "w") as f:
    json.dump(aggregated_spirits, f, indent=4)
