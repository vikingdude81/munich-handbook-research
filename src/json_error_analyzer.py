import os

def analyze_json_errors(input_dir):
    error_patterns = {}
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(input_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = f.read()
                    data = json.loads(json_data)
            except json.JSONDecodeError as e:
                error_type = type(e).__name__
                if error_type not in error_patterns:
                    error_patterns[error_type] = []
                error_patterns[error_type].append(filename)
    
    return error_patterns

def generate_revised_prompt(schema_file):
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_content = f.read()
    prompt_template = f"""
    Given the following JSON data from a research output file, ensure it adheres to the provided schema and return the valid JSON string. If the input does not conform to the schema, raise an exception with a detailed error message indicating which part of the JSON is invalid.
    
    Schema: {schema_content}
    
    Input JSON:
    ---
    {json.dumps(json.loads('{"key": "value"}', object_pairs_hook=OrderedDict), indent=2)}
    ---
    
    Valid JSON Output:
    ---
    {{
        "key": "value"
    }}
    ---

    Raise Exception with detailed error message if input is invalid.
    """
    return prompt_template

# Example usage
input_dir = 'E:\\munich_handbook_research\\src\\raw_outputs'
error_patterns = analyze_json_errors(input_dir)
print(error_patterns)

schema_file_path = 'path_to_schema_file.json'  # Replace with actual path
revised_prompt = generate_revised_prompt(schema_file_path)
print(revised_prompt)