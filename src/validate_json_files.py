import os
import json

def validate_json_files(directory):
    valid_count = 0
    invalid_count = 0
    missing_chunk_ids = set()
    errors = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        chunk_id = data.get('chunk_id', None) or file.split('.')[0]
                        if not chunk_id:
                            missing_chunk_ids.add(chunk_id)
                        valid_count += 1
                except Exception as e:
                    invalid_count += 1
                    errors.append((file_path, str(e)))

    with open('validation_report.txt', 'w') as report_file:
        report_file.write(f"Valid JSON files: {valid_count}\n")
        report_file.write(f"Invalid JSON files: {invalid_count}\n")
        if missing_chunk_ids:
            report_file.write("Missing chunk IDs:\n")
            for chunk_id in missing_chunk_ids:
                report_file.write(chunk_id + '\n')
        if errors:
            report_file.write("\nErrors encountered:\n")
            for file_path, error in errors:
                report_file.write(f"{file_path}: {error}\n")

# Run the validation script
validate_json_files('E:\\munich_handbook_research\\distillations')
