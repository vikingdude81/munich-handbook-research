import json
import re
from time import sleep

def clean_markdown_fences(text):
    return re.sub(r"```.*?\n", "", text, flags=re.DOTALL)

def validate_json(json_str):
    try:
        json.loads(json_str)
        return True
    except ValueError as e:
        print(f"Invalid JSON: {e}")
        return False

def batch_distill_source(input_files, output_file, max_attempts=3):
    with open(output_file, "w") as out_file:
        for chunk in split_into_chunks(input_files):
            for attempt in range(max_attempts):
                try:
                    results = []
                    for file_path in chunk:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = clean_markdown_fences(f.read())
                            if validate_json(content):
                                json_str = json.dumps(json.loads(content))
                                results.append((file_path, json_str))
                    
                    # Write all chunks to output file
                    for result in sorted(results, key=lambda x: x[0]):
                        out_file.write(result[1] + "\n\n")
                    
                    break  # Exit loop if valid JSON is found and written
                except Exception as e:
                    print(f"Failed to process chunk {chunk}: {e}")
                    sleep(2 ** attempt)  # Exponential backoff

def split_into_chunks(files, max_size=10):
    for i in range(0, len(files), max_size):
        yield files[i:i + max_size]

# Example usage
batch_distill_source(["file1.txt", "file2.md"], "output.json")
