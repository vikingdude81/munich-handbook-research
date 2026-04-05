import os
import json

def scan_chunks_and_distillations():
    chunks_dir = 'data/necro/chunks/'
    distillations_dir = 'data/distillations/'

    chunk_ids = [f.split('.')[0] for f in os.listdir(chunks_dir) if f.endswith('.json')]
    results = {}

    for chunk_id in chunk_ids:
        chunk_path = os.path.join(chunks_dir, f'{chunk_id}.json')
        distillation_path = os.path.join(distillations_dir, f'{chunk_id}.json')

        if not os.path.exists(chunk_path):
            results[chunk_id] = 'missing'
            continue

        with open(chunk_path, 'r') as chunk_file:
            chunk_data = json.load(chunk_file)

        if not os.path.exists(distillation_path):
            results[chunk_id] = 'partial' if 'raw_quote' in chunk_data else 'corrupt'
            continue

        with open(distillation_path, 'r') as distillation_file:
            try:
                _ = json.load(distillation_file)
                results[chunk_id] = 'success'
            except json.JSONDecodeError:
                results[chunk_id] = 'corrupt'

    return results

def print_summary_table(results):
    print("Chunk ID\tStatus")
    for chunk_id, status in results.items():
        print(f"{chunk_id}\t{status}")

# Run the diagnostic script
results = scan_chunks_and_distillations()
print_summary_table(results)
