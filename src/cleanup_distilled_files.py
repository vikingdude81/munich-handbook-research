import os
import json
import logging

logging.basicConfig(level=logging.INFO)

def cleanup_distilled_files(directory):
    invalid_files = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if not os.path.isfile(file_path):
            continue
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception:
            logging.warning(f"Error reading {file_path}")
            continue
        
        if 'raw_quote' not in data:
            invalid_files.append((filename, file_path))
            logging.warning(f"{file_path} missing 'raw_quote'")
        
        if os.path.getsize(file_path) < 100:
            os.remove(file_path)
            logging.info(f"Deleted {file_path} (empty or <100 bytes)")
    
    return invalid_files
