import json
from os import listdir

# Define the path to the directory containing the JSON files
json_dir = 'path/to/json/files'

# Define the required keys
required_keys = ['spirits', 'experiments', 'raw_quote']

# Initialize a list to store validation results
validation_results = []

# Iterate over all files in the directory
for filename in listdir(json_dir):
    if filename.endswith('.json'):
        file_path = f'{json_dir}/{filename}'
        
        # Check if the file exists
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                
                # Check for required keys
                missing_keys = [key for key in required_keys if key not in data]
                if missing_keys:
                    validation_results.append({
                        'filename': filename,
                        'error': f'Missing required keys: {", ".join(missing_keys)}'
                    })
                else:
                    validation_results.append({
                        'filename': filename,
                        'status': 'Valid'
                    })
        except json.JSONDecodeError:
            validation_results.append({
                'filename': filename,
                'error': 'Not parseable as JSON'
            })

# Write the validation results to a report file
with open('distill_validation_report.json', 'w') as report_file:
    json.dump(validation_results, report_file, indent=4)

# Check if all files are valid
all_valid = all(result['status'] == 'Valid' for result in validation_results)
if not all_valid:
    raise Exception("Validation failed. Please check distill_validation_report.json for details.")
