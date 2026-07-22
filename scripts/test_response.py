#!/usr/bin/env python3
"""Test actual LLM response format."""

import json
from pathlib import Path
from openai import OpenAI

LM_STUDIO_URL = "http://192.168.50.150:1234/v1"
MODEL = "nvidia/nemotron-3-nano-omni"

client = OpenAI(base_url=LM_STUDIO_URL, api_key='lm-studio')

# Get a chunk
chunk_file = Path('data/sources/malleus_marx/malleus_maleficarum/chunk_003.txt')
chunk_text = chunk_file.read_text(encoding='utf-8')[:2000]

prompt = f"""Respond with ONLY a JSON object (no markdown, no extra text):
{{"primary_mode": "Deconstruction", "entropy_score": 7, "summary": "test"}}

TEXT: {chunk_text}"""

print("Sending request...")
resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {'role': 'system', 'content': 'Respond only with JSON'},
        {'role': 'user', 'content': prompt},
    ],
    max_tokens=500,
    temperature=0.1,
)

print("\nRESPONSE CONTENT:")
print(repr(resp.choices[0].message.content))

print("\nFORMATTED:")
print(resp.choices[0].message.content)
