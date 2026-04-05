import json
import os

# Initialize an empty list to store failed chunks
failed_chunks = []

# Loop through all 39 chunk files
for i in range(1, 40):
    file_name = f'distilled_{i}.json'
    try:
        # Attempt to parse the JSON file
        with open(file_name, 'r') as file:
            json.load(file)
    except json.JSONDecodeError as e:
        # If parsing fails, log the chunk ID and error type
        failed_chunks.append({'chunk_id': i, 'error_type': str(e)})

# Write the summary report to data/audit_report.json
with open('data/audit_report.json', 'w') as file:
    json.dump(failed_chunks, file, indent=4)

print("Audit and validation complete. Summary report saved in data/audit_report.json")