import os
import json

def audit_chunk_files(directory):
    results = []
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        if not filename.endswith('.json'):
            continue
        
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                status = 'Success'
                issues = []
        except json.JSONDecodeError as e:
            status = 'Fail'
            issues = [f'JSON decode error: {e}']
        except Exception as e:
            status = 'Fail'
            issues = [f'Other error: {e}']
        
        results.append({
            'Filename': filename,
            'Status': status,
            'Issues': issues
        })
    
    return results

def print_summary(results):
    print(f"{'Filename':<20} {'Status':<10} {'Issues'}")
    print('-' * 50)
    
    for result in results:
        issues_str = ', '.join(result['Issues']) if result['Issues'] else 'None'
        print(f"{result['Filename']:<20} {result['Status']:<10} {issues_str}")

# Example usage
directory_path = '/path/to/chunk/files'
results = audit_chunk_files(directory_path)
print_summary(results)
