# src/utils/json_fix.py

import json
from markdown import markdown

def extract_json_from_markdown(markdown_text):
    """Extract JSON from markdown blocks."""
    html = markdown(markdown_text)
    start_tag = '<pre><code class="language-json">'
    end_tag = '</code></pre>'
    start_index = html.find(start_tag) + len(start_tag)
    end_index = html.find(end_tag, start_index)
    if start_index == -1 or end_index == -1:
        return None
    json_text = html[start_index:end_index].strip()
    return json_text

def auto_fix_json(json_text):
    """Auto-fix common JSON syntax errors."""
    try:
        # Try to parse the JSON as is
        json.loads(json_text)
        return json_text
    except json.JSONDecodeError:
        # Fix trailing commas and unescaped quotes
        fixed_text = json_text.replace(''', '"').replace('}', '}').replace(']', ']')
        return fixed_text

def validate_json_schema(json_text, schema):
    """Validate JSON against a schema."""
    try:
        json_obj = json.loads(json_text)
        import jsonschema
        jsonschema.validate(instance=json_obj, schema=schema)
        return True
    except (json.JSONDecodeError, jsonschema.exceptions.ValidationError):
        return False

# Unit tests for the functions
def test_extract_json_from_markdown():
    markdown_text = "Here is some text.\n\n```json\n{ \"key\": \"value\" }\n```\nMore text."
    assert extract_json_from_markdown(markdown_text) == '{ "key": "value" }'

def test_auto_fix_json():
    malformed_json = '{"key": "value"}'
    fixed_json = auto_fix_json(malformed_json)
    assert json.loads(fixed_json)

def test_validate_json_schema():
    schema = {"type": "object", "properties": {"key": {"type": "string"}}}
    valid_json = '{"key": "value"}'
    invalid_json = '{"key": 123}'
    assert validate_json_schema(valid_json, schema)
    assert not validate_json_schema(invalid_json, schema)

# Run the tests
if __name__ == "__main__":
    import unittest
    unittest.main()
