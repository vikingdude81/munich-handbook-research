import os
import json

def verify_distillation():
    valid_files = 0
    missing_chunks = []
    
    for filename in os.listdir('data/distilled/'):
        if filename.startswith('necro_chunk_') and filename.endswith('.json'):
            file_path = os.path.join('data/distilled/', filename)
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if 'spirit_name' in data and 'raw_quote' in data:
                        valid_files += 1
                    else:
                        missing_chunks.append(filename)
            except (json.JSONDecodeError, FileNotFoundError):
                missing_chunks.append(filename)
    
    report = {
        'valid_files': valid_files,
        'missing_chunks': missing_chunks
    }
    
    with open('distillation_report.json', 'w') as report_file:
        json.dump(report, report_file, indent=4)

verify_distillation()
