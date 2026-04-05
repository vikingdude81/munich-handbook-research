import json
import re
import os
from typing import List

def batch_distill_source(data: List[str], log_dir: str) -> None:
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    for item in data:
        try:
            # Attempt to parse JSON directly
            parsed_json = json.loads(item)
        except json.JSONDecodeError:
            # Fallback to regex-based extraction
            match = re.search(r'\{.*\}', item, re.DOTALL)
            if match:
                parsed_json = json.loads(match.group())
            else:
                raise ValueError("No valid JSON found in input")

        # Validate required fields
        required_fields = ['id', 'content']
        for field in required_fields:
            if field not in parsed_json:
                raise KeyError(f"Missing required field: {field}")

        # Writeback validated data
        with open(os.path.join(log_dir, f"{parsed_json['id']}.json"), 'w') as f:
            json.dump(parsed_json, f)

        # Retry logic (max 2 retries)
        for _ in range(2):
            try:
                # Simulate write operation that might fail
                pass
            except Exception as e:
                print(f"Write failed: {e}")
            else:
                break