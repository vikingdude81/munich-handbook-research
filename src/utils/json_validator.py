import os
import json

def validate_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            required_fields = ['field1', 'field2', 'field3']  # Replace with actual required fields
            missing_fields = [field for field in required_fields if field not in data]
            return 'complete' if not missing_fields else 'partial', missing_fields
    except FileNotFoundError:
        return 'failed', []
    except json.JSONDecodeError:
        return 'failed', []

def main():
    directory = 'path/to/your/json/files'  # Replace with your directory path
    summary_report = {}

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            status, missing_fields = validate_json(file_path)
            summary_report[filename] = {'status': status, 'missing_fields': missing_fields}

    print(json.dumps(summary_report, indent=4))

if __name__ == "__main__":
    main()
