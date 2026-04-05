import os
import json

def audit_json_files(directory):
    report = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    report.append({
                        'file': file,
                        'size': os.path.getsize(file_path),
                        'valid': True
                    })
                except json.JSONDecodeError as e:
                    report.append({
                        'file': file,
                        'size': os.path.getsize(file_path),
                        'valid': False,
                        'error_type': str(e),
                        'first_200_chars': open(file_path, 'r', encoding='utf-8').read()[:200]
                    })
    
    return report
