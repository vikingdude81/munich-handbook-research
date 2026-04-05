import os
import json
from datetime import datetime

# Define the directory containing the distilled JSON files
DISTILL_DIR = 'distill/necro/'
LOG_FILE = 'logs/distill_validation.log'
NUM_FILES = 39

# Expected keys in each JSON file
EXPECTED_KEYS = {'spirits', 'experiments', 'raw_quote'}

def validate_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("JSON is not a dictionary")
            missing_keys = EXPECTED_KEYS - set(data.keys())
            if missing_keys:
                raise KeyError(f"Missing keys: {', '.join(missing_keys)}")
            return True
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        with open(LOG_FILE, 'a') as log:
            log.write(f"{datetime.now()}: File not found: {file_path}\n")
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {file_path}")
        with open(LOG_FILE, 'a') as log:
            log.write(f"{datetime.now()}: Invalid JSON in file: {file_path}\n")
    except Exception as e:
        print(f"Error processing file: {file_path} - {e}")
        with open(LOG_FILE, 'a') as log:
            log.write(f"{datetime.now()}: Error processing file: {file_path} - {e}\n")
    return False

def main():
    valid_files = 0
    for i in range(1, NUM_FILES + 1):
        file_name = f'distilled_output_{i}.json'
        file_path = os.path.join(DISTILL_DIR, file_name)
        if validate_json_file(file_path):
            valid_files += 1

    summary_report = f"Validation Report - {datetime.now()}\n"
    summary_report += f"Total files: {NUM_FILES}\n"
    summary_report += f"Valid files: {valid_files}\n"
    summary_report += f"Invalid files: {NUM_FILES - valid_files}\n"

    print(summary_report)
    with open(LOG_FILE, 'a') as log:
        log.write(summary_report)

if __name__ == "__main__":
    main()
