import os
import json

def validate_json_files(directory):
    with open('distillation_validation_report.txt', 'w') as report:
        for i, filename in enumerate(os.listdir(directory)):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                try:
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        required_fields = ['spirit_name', 'rank', 'raw_quote', 'page_folio']
                        missing_fields = [field for field in required_fields if field not in data]
                        if missing_fields:
                            report.write(f"File {i+1}: {filename} is missing fields: {', '.join(missing_fields)}\n")
                except json.JSONDecodeError:
                    report.write(f"File {i+1}: {filename} is not a valid JSON file.\n")
