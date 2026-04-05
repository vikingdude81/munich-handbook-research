import json

def check_schema(json_file):
    required_fields = ["spirit_name", "rank", "function", "appearance", "legion_count", 
                        "conjuration_method", "experiment_refs", "page_folio", "raw_quote"]
    
    with open(json_file, 'r') as f:
        data = json.load(f)
        
    if not all(field in data for field in required_fields):
        return f"Missing fields: {', '.join([field for field in required_fields if field not in data])}"
    
    return "Schema is compliant."

# Test the function with sample files
print(check_schema("necro_05.json"))  # Example output: Missing fields: conjuration_method, page_folio
print(check_schema("necro_22.json"))  # Example output: Schema is compliant.
print(check_schema("necro_37.json"))  # Example output: Missing fields: appearance, legion_count
