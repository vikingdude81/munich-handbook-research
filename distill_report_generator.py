import os
from pathlib import Path
import json

# Define the directory path
directory_path = 'distillations/'

# Initialize a list to store report entries
report_entries = []

# Iterate over all files in the directory
for file_name in os.listdir(directory_path):
    if file_name.endswith('.json'):
        file_path = Path(directory_path) / file_name
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                report_entries.append({'chunk_id': file_name, 'status': 'success', 'error': None})
        except json.JSONDecodeError as e:
            report_entries.append({'chunk_id': file_name, 'status': 'failure', 'error': str(e)})

# Write the report to distill_report.json
with open('distill_report.json', 'w') as report_file:
    json.dump(report_entries, report_file, indent=4)
