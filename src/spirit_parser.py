import json

def parse_chunk_jsons(chunk_jsons):
    unified_list = []
    for chunk in chunk_jsons:
        entry = {}
        
        # Name and rank(s)
        name = chunk.get('name')
        ranks = chunk.get('rank', [])
        if not (name and ranks):
            entry['status'] = 'NEEDS_VERIFICATION'
            continue
        
        # Function(s) is a list, no need for normalization
        functions = chunk.get('function', [])
        
        # Appearance
        appearance = chunk.get('appearance')
        
        # Legion_count as int or None
        legion_count = chunk.get('legion_count', None)
        if isinstance(legion_count, str):
            legion_count = None
        
        # Conjuration_method
        conjuration_method = chunk.get('conjuration_method')
        
        # Experiment_refs (list)
        experiment_refs = chunk.get('experiment_refs', [])
        
        # Provenance (chunk_id + raw_quote)
        provenance = f"{chunk['id']}: {chunk['raw_quote']}"

        entry.update({
            'name': name,
            'ranks': ranks,
            'functions': functions,
            'appearance': appearance,
            'legion_count': legion_count,
            'conjuration_method': conjuration_method,
            'experiment_refs': experiment_refs,
            'provenance': provenance
        })
        
        unified_list.append(entry)
    
    return unified_list

# Example usage:
chunk_jsons = [
    {
        "name": "Soulas",
        "rank": ["Great"],
        "function": ["Healer", "Support"],
        "appearance": "Glowing blue aura",
        "legion_count": 5,
        "conjuration_method": "Summoning",
        "experiment_refs": [
            {"id": 1, "type": "test"},
            {"id": 2, "type": "test"}
        ],
        "raw_quote": "Soulas is a powerful healer"
    },
    # Add more chunk JSONs here
]

unified_list = parse_chunk_jsons(chunk_jsons)
print(unified_list)