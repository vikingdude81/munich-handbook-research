import os
import json

def validate_jsonl_files(directory):
    invalid_lines = []
    duplicates = set()
    required_fields = {'spirit_name', 'rank', 'page'}
    
    for filename in os.listdir(directory):
        if not filename.endswith('.jsonl'):
            continue
        
        file_path = os.path.join(directory, filename)
        
        for line_number, line in enumerate(open(file_path), start=1):
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                invalid_lines.append((file_path, line_number, str(e)))
                continue
            
            data = json.loads(line)
            
            if not required_fields.issubset(data.keys()):
                invalid_lines.append((file_path, line_number, "Missing required fields"))
                
            if data in duplicates:
                invalid_lines.append((file_path, line_number, "Duplicate entry"))
            else:
                duplicates.add(data)

    return invalid_lines

directory = r'E:\munich_handbook_research\distill\necro'
invalid_lines = validate_jsonl_files(directory)
print("Invalid JSON lines found:")
for file_path, line_number, error in sorted(invalid_lines):
    print(f"File: {file_path}, Line: {line_number}, Error: {error}")
