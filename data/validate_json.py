import os
import json

def validate_json(file_path):
    try:
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        
        # Define the expected keys or structure here
        required_keys = ['name', 'value']
        for key in required_keys:
            if key not in json_data:
                return False
        
        # Add more checks based on your JSON structure and requirements
        return True
    except json.JSONDecodeError:
        print(f"Invalid JSON file: {file_path}")
        return False

def main():
    report = []
    
    for root, dirs, files in os.walk('data'):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                valid = validate_json(file_path)
                report.append({
                    'file': file_path,
                    'valid': valid
                })
    
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
