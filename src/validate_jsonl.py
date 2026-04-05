import json
import glob

def validate_jsonl_files():
    valid_chunks = []
    failed_chunks = []

    for file in glob.glob("distilled/*.jsonl"):
        with open(file, 'r') as f:
            for line_number, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    chunk_id = data.get('chunk_id')
                    if not isinstance(chunk_id, int) or chunk_id <= 0:
                        failed_chunks.append({'file': file, 'line': line_number})
                    else:
                        valid_chunks.append({'file': file, 'line': line_number})
                except json.JSONDecodeError as e:
                    failed_chunks.append({'file': file, 'line': line_number})

    with open('valid_chunks.txt', 'w') as valid_file, open('failed_chunks.json', 'w') as failed_file:
        for chunk in sorted(valid_chunks, key=lambda x: (x['file'], x['line'])):
            valid_file.write(f"{chunk['file']}:{chunk['line']}\n")
        
        for chunk in sorted(failed_chunks, key=lambda x: (x['file'], x['line'])):
            failed_file.write(json.dumps(chunk) + '\n')

validate_jsonl_files()
