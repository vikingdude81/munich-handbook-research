import json
import os

def main():
    directory = 'distillations'
    spirits = []

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                for entry in data.get('distillations', []):
                    spirit = entry.get('spirit')
                    chunk_id = entry.get('chunk_id')
                    raw_quote = entry.get('raw_quote')
                    if not spirit or not chunk_id or not raw_quote:
                        needs_verification = True
                    else:
                        needs_verification = False
                    spirits.append({
                        'spirit': spirit,
                        'chunk_id': chunk_id,
                        'raw_quote': raw_quote,
                        'needs_verification': needs_verification
                    })

    unique_spirits = {}
    for s in spirits:
        if s['spirit'] not in unique_spirits:
            unique_spirits[s['spirit']] = s

    print("Normalized Spirits:")
    for s in unique_spirits.values():
        print(f"{s['spirit']} - Chunk {s['chunk_id']}, Quote: {s['raw_quote']}, Needs Verification: {s['needs_verification']}")

if __name__ == "__main__":
    main()
