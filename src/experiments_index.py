import json

# Assume distilled_data is loaded from a file or source
experiments_index = {}

for entry in distilled_data:
    spirit = entry['spirit']
    experiment_refs = entry['experiment_ref'].split(',')
    for ref in experiment_refs:
        exp_id = ref.strip()
        if exp_id not in experiments_index:
            experiments_index[exp_id] = []
        experiments_index[exp_id].append(spirit)

with open('src/experiments_index.json', 'w') as f:
    json.dump(experiments_index, f, indent=2)
