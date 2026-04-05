import os
import json

base_path = r'E:\munich_handbook_research\distilled\necro\\'
file_names = [f'chunk_{i:03d}.json' for i in range(1, 40)]

missing_files = []
malformed_files = []

for file_name in file_names:
    file_path = os.path.join(base_path, file_name)
    
    if not os.path.exists(file_path):
        missing_files.append(file_name)
    else:
        try:
            with open(file_path, 'r') as file:
                json.load(file)
        except json.JSONDecodeError:
            malformed_files.append(file_name)

if missing_files:
    print(f"Missing files: {', '.join(missing_files)}")
else:
    print("All files are present.")

if malformed_files:
    print(f"Malformed files: {', '.join(malformed_files)}")
else:
    print("All files have valid JSON structure.")