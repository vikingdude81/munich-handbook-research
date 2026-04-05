import os
import json

def validate_distillations(directory):
    files = [f for f in os.listdir(directory) if f.endswith('.json')]
    results = []
    
    for file in files:
        path = os.path.join(directory, file)
        try:
            with open(path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            results.append((file, "Invalid JSON"))
        else:
            if 'spirits' in data and 'experiments' in data and 'page_ref' in data:
                results.append((file, "Valid"))
            else:
                results.append((file, "Missing required keys"))
    
    return results

def main():
    results = validate_distillations('.')
    print("Summary Report:")
    print(f"Total files: {len(results)}")
    valid_count = sum(1 for status in results if status[1] == "Valid")
    invalid_count = len(results) - valid_count
    print(f"Valid: {valid_count}")
    print(f"Invalid: {invalid_count}")
    
    print("\nDetailed Report:")
    for file, status in results:
        print(f"{file}: {status}")

if __name__ == "__main__":
    main()
