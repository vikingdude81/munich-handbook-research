import os
import json

# Initialize counters and data structure for results
results = {
    "total_files": 0,
    "valid_files": 0,
    "invalid_files": 0,
    "metadata": {
        "spirits_count": 0,
        "experiments_count": 0,
        "raw_quote_presence": 0
    }
}

# Scan all JSON files in the dist/ directory
for filename in os.listdir('dist'):
    if filename.endswith('.json'):
        results["total_files"] += 1
        file_path = os.path.join('dist', filename)
        
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                
                # Validate JSON syntax
                if isinstance(data, dict):
                    results["valid_files"] += 1
                    
                    # Extract metadata
                    if "spirits_count" in data:
                        results["metadata"]["spirits_count"] += data["spirits_count"]
                    if "experiments_count" in data:
                        results["metadata"]["experiments_count"] += data["experiments_count"]
                    if "raw_quote" in data:
                        results["metadata"]["raw_quote_presence"] += 1
                else:
                    print(f"{filename} is not a valid JSON object.")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON syntax in {filename}: {e}")
            results["invalid_files"] += 1

# Output summary report to reports/distillation_validation_71.json
with open('reports/distillation_validation_71.json', 'w') as file:
    json.dump(results, file, indent=4)

print("Validation complete. Summary report saved.")
