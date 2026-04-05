import os
import json

def audit_distillation_outputs(directory):
    valid_files = []
    malformed_files = []
    missing_files = []

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if 'spirits' in data and 'raw_quote' in data:
                        valid_files.append(filename)
                    else:
                        malformed_files.append(filename)
            except json.JSONDecodeError:
                malformed_files.append(filename)

    missing_files = [f for f in os.listdir(directory) if f.endswith('.json') and f not in valid_files + malformed_files]

    return {
        'valid_files': valid_files,
        'malformed_files': malformed_files,
        'missing_files': missing_files
    }
