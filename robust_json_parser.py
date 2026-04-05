# robust_json_parser.py

import json

def extract_json_from_response(response_text: str) -> dict | None:
    try:
        # Remove markdown-like wrapping (e.g., `{{` and `}}`)
        response_text = response_text.strip('[]')
        
        # Fix trailing commas
        while ',' in response_text[-2:]:
            response_text = response_text[:-1]
        
        # Fix unescaped quotes
        response_text = response_text.replace('"', '"')
        
        return json.loads(response_text)
    except (json.JSONDecodeError, IndexError):
        return None