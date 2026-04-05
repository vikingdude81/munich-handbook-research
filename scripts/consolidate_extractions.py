import json
import os

def process_distillations():
    input_dir = 'distillations/necro'
    output_file = 'distillations/necro/consolidated_extractions.json'

    spirits = []

    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'r') as f:
                data = json.load(f)

            for entry in data:
                if 'name' in entry:
                    spirit_name = entry['name']
                    chunk_id = entry.get('chunk_id', None)
                    passage_index = entry.get('passage_index', None)
                    needs_verification = False

                    if 'rank' not in entry or 'function' not in entry:
                        needs_verification = True

                    spirits.append({
                        'name': spirit_name,
                        'chunk_id': chunk_id,
                        'passage_index': passage_index,
                        'needs_verification': needs_verification
                    })

    with open(output_file, 'w') as f:
        json.dump(spirits, f, indent=2)

if __name__ == "__main__":
    process_distillations()