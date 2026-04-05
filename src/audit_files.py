import os
import json

# Define the directory containing the JSON outputs
directory = r'E:\munich_handbook_research\src\distillations'

# List of expected file names (39 in total)
expected_files = [f'file_{i}.json' for i in range(1, 40)]

# Initialize a list to store missing/corrupt files
audit_report = []

# Iterate over each expected file
for file_name in expected_files:
    # Construct the full file path
    file_path = os.path.join(directory, file_name)
    
    # (a) Check if the file exists
    if not os.path.exists(file_path):
        audit_report.append(f'Missing: {file_name}')
        continue
    
    # (b) Validate as parseable JSON
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        audit_report.append(f'Corrupt: {file_name}')
        continue
    
    # (c) Extract and log number of spirits/experiments found
    num_spirits_experiments = len(data.get('spirits', [])) + len(data.get('experiments', []))
    print(f'{file_name}: Number of spirits/experiments - {num_spirits_experiments}')

# Write audit report to src/audit_report.md
with open(os.path.join(directory, 'audit_report.md'), 'w') as report_file:
    for item in audit_report:
        report_file.write(f'- {item}\n')

print('Audit report generated successfully.')
