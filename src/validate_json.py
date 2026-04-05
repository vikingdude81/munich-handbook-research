import os
import json

def validate_json_files(directory):
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "timestamp": {"type": "integer", "format": "date-time"},
            "data": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string"},
                            "language": {"type": "string"}
                        },
                        "required": ["source", "language"]
                    }
                },
                "required": ["text", "metadata"]
            }
        },
        "required": ["id", "timestamp", "data"]
    }

    compliant = []
    non_compliant = []

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if not schema_check(data, schema):
                        non_compliant.append({"file": filename, "error": "Schema validation failed"})
                    else:
                        compliant.append(filename)
            except Exception as e:
                non_compliant.append({"file": filename, "error": f"Error reading {filename}: {str(e)}"})

    return compliant, non_compliant

def schema_check(data, schema):
    if not isinstance(data, dict):
        return False
    for required in schema["required"]:
        if required not in data:
            return False
    for prop, type_spec in schema["properties"].items():
        if prop not in data:
            continue
        if not isinstance(data[prop], type_spec.get("type", str)):
            return False
        if "format" in type_spec and not isinstance(type_spec["format"], str):
            return False
    return True

if __name__ == "__main__":
    directory = '.'  # Default to current directory
    compliant, non_compliant = validate_json_files(directory)
    print("Compliant files:")
    for file in compliant:
        print(file)
    print("\nNon-compliant files:")
    for error in non_compliant:
        print(f"File: {error['file']}, Error: {error['error']}")