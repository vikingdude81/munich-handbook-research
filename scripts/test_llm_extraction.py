#!/usr/bin/env python
"""Quick test of LLM extraction to debug response format."""

import json
import sys
from openai import OpenAI
from pathlib import Path

# Connect to LM Studio
client = OpenAI(base_url='http://192.168.50.150:1234', api_key='lm-studio')

# Load a chunk
chunk_path = Path('data/sources/malleus_marx/malleus_maleficarum/chunk_001.txt')
chunk_text = chunk_path.read_text(encoding='utf-8')[:1000]  # First 1000 chars

prompt = f"""Classify this text as Deconstructionist or Constructive. Respond with ONLY a JSON object.

{{"primary_mode": "Deconstruction" or "Construction" or "Mixed", "summary": "1 sentence"}}

TEXT: {chunk_text}"""

print("=" * 80)
print("PROMPT:")
print(prompt)
print("=" * 80)

try:
    response = client.chat.completions.create(
        model='qwen/qwen3.5-9b',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.3,
        max_tokens=200
    )
    
    print(f"\nRESPONSE OBJECT: {response}")
    print(f"CHOICES: {response.choices}")
    
    if not response.choices or len(response.choices) == 0:
        print("ERROR: No choices in response")
        sys.exit(1)
    
    choice = response.choices[0]
    print(f"FIRST CHOICE: {choice}")
    print(f"MESSAGE: {choice.message}")
    
    if choice.message is None:
        print("ERROR: Message is None")
        sys.exit(1)
    
    response_text = choice.message.content
    print("\nRAW RESPONSE:")
    print(repr(response_text))
    print("\nFORMATTED:")
    print(response_text)
    
    # Try to parse
    try:
        data = json.loads(response_text)
        print("\nPARSED JSON:")
        print(json.dumps(data, indent=2))
    except json.JSONDecodeError as e:
        print(f"\nJSON PARSE ERROR: {e}")
        print(f"Error at position {e.pos}")
        
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
