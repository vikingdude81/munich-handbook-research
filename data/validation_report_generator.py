import os
import json

def validate_json(file_path):
    try:
        with open(file_path, 'r') as file:
            json.load(file)
        return True
    except json.JSONDecodeError:
        return False

def main():
    base_dir = 'data/distilled/'
    files = [f for f in os.listdir(base_dir) if f.startswith('distilled_chunk_') and f.endswith('.json')]
    total_files = len(files)
    valid_files = 0
    missing_files = []

    for file in files:
        file_path = os.path.join(base_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
        elif validate_json(file_path):
            valid_files += 1
        else:
            print(f"Corrupt JSON: {file}")

    success_rate = (valid_files / total_files) * 100 if total_files > 0 else 0

    summary_report = {
        'total_files': total_files,
        'valid_files': valid_files,
        'missing_files': missing_files,
        'success_rate': f"{success_rate:.2f}%"
    }

    print(json.dumps(summary_report, indent=4))

    with open('data/validation_report.json', 'w') as report_file:
        json.dump(summary_report, report_file, indent=4)

if __name__ == "__main__":
    main()
