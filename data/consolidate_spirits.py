import json

# Step 1: Read all files
files = ['file1.json', 'file2.json', ..., 'file39.json']  # Replace with actual file names
data = []

for file in files:
    with open(file, 'r') as f:
        data.extend(json.load(f))

# Step 2 & 3: Extract and deduplicate data
seen = set()
consolidated_data = []

for item in data:
    raw_quote = item.get('raw_quote')
    if raw_quote not in seen:
        seen.add(raw_quote)
        consolidated_data.append(item)

# Step 4 & 5: Add provenance and handle ambiguities
for item in consolidated_data:
    if 'chunk_id' not in item or 'raw_quote' not in item:
        item['NEEDS_VERIFICATION'] = True

# Step 6: Output to JSON
with open('consolidated_spirits.json', 'w') as f:
    json.dump(consolidated_data, f, indent=4)
