import json
import os

input_dir = '.'  # Current directory by default
output_path = os.path.join('distillations', 'merged_distillations.jsonl')

seen_quotes = set()
merged_entries = []

for filename in os.listdir(input_dir):
    if not filename.endswith('.jsonl'):
        continue
    file_path = os.path.join(input_dir, filename)
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            if 'raw_quote' in data and data['raw_quote'] not in seen_quotes:
                seen_quotes.add(data['raw_quote'])
                merged_entries.append(data)

with open(output_path, 'w') as f:
    for entry in merged_entries:
        f.write(json.dumps(entry) + '\n')