import os
import jsonlines
import csv

def scan_files(directory):
    results = []
    for filename in os.listdir(directory):
        if filename.endswith('.jsonl'):
            filepath = os.path.join(directory, filename)
            try:
                with jsonlines.open(filepath) as reader:
                    count = sum(1 for _ in reader)
                    results.append({'filename': filename, 'count': count, 'status': 'valid'})
            except jsonlines.InvalidFileError:
                results.append({'filename': filename, 'count': 0, 'status': 'invalid_json'})
            except FileNotFoundError:
                results.append({'filename': filename, 'count': 0, 'status': 'missing'})
    return results

def write_report(results, output_file):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['filename', 'count', 'status'])
        writer.writeheader()
        for result in results:
            writer.writerow(result)

if __name__ == "__main__":
    directory = 'distillations/'
    output_file = 'quality_report.csv'
    results = scan_files(directory)
    write_report(results, output_file)
