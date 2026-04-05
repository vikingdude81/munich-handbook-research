import json
import os

def aggregate_spirits_experiments(input_dir):
    spirits = []
    experiments = []

    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            with open(os.path.join(input_dir, filename), 'r') as f:
                data = json.load(f)
                for entry in data:
                    if 'spirit' in entry:
                        if 'chunk_id' in entry and 'raw_quote' in entry:
                            spirits.append({
                                'spirit': entry['spirit'],
                                'chunk_id': entry['chunk_id'],
                                'raw_quote': entry['raw_quote'],
                                'verified': True
                            })
                        else:
                            spirits.append({
                                'spirit': entry['spirit'],
                                'chunk_id': entry['chunk_id'],
                                'raw_quote': entry['raw_quote'],
                                'verified': False
                            })
                    elif 'experiment' in entry:
                        if 'chunk_id' in entry and 'raw_quote' in entry:
                            experiments.append({
                                'experiment': entry['experiment'],
                                'chunk_id': entry['chunk_id'],
                                'raw_quote': entry['raw_quote'],
                                'verified': True
                            })
                        else:
                            experiments.append({
                                'experiment': entry['experiment'],
                                'chunk_id': entry['chunk_id'],
                                'raw_quote': entry['raw_quote'],
                                'verified': False
                            })

    with open('aggregated_spirits.json', 'w') as f:
        json.dump(spirits, f, indent=2)

    with open('aggregated_experiments.json', 'w') as f:
        json.dump(experiments, f, indent=2)

if __name__ == '__main__':
    aggregate_spirits_experiments('/path/to/input/directory')
