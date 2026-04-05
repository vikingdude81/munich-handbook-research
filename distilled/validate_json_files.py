import os
import json

log_file = 'E:\\munich_handbook_research\\distilled\\distillation_status.log'

with open(log_file, 'w') as log:
    for filename in os.listdir('E:\\munich_handbook_research\\distilled'):
        if filename.endswith('.json'):
            file_path = os.path.join('E:\\munich_handbook_research\\distilled', filename)
            try:
                with open(file_path, 'r') as json_file:
                    json.load(json_file)
            except json.JSONDecodeError as e:
                log.write(f'Invalid JSON in {filename}: {e}\n')
            except Exception as e:
                log.write(f'Missing or invalid file: {filename}, Error: {e}\n')
