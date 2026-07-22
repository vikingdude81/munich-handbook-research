#!/usr/bin/env python3
from pathlib import Path
from openai import OpenAI
import json

LM_STUDIO_URL = 'http://192.168.50.150:1234/v1'
MODEL = 'nvidia/nemotron-3-nano-omni'
client = OpenAI(base_url=LM_STUDIO_URL, api_key='lm-studio')
chunk = Path('data/sources/malleus_marx/malleus_maleficarum/chunk_003.txt').read_text(encoding='utf-8')[:800]
prompt = 'Respond with ONLY a JSON object (no markdown, no extra text):\n{"primary_mode": "Deconstruction", "entropy_score": 7, "summary": "test"}\n\nTEXT: ' + chunk
resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {'role': 'system', 'content': 'Respond only with JSON'},
        {'role': 'user', 'content': prompt},
    ],
    max_tokens=200,
    temperature=0.1,
)
print('TYPE:', type(resp))
print('RESP:', resp)
print('CHOICES:', getattr(resp, 'choices', None))
if getattr(resp, 'choices', None):
    print('CONTENT repr:', repr(resp.choices[0].message.content))
print('JSON DUMP:', json.dumps(resp, default=str)[:4000])
