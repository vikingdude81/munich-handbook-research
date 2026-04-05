import os
import json
from datetime import datetime

def validate_json(file_path):
    try:
        with open(file_path, 'r') as file:
            json.load(file)
        return True
    except (json.JSONDecodeError, FileNotFoundError):
        return False

def run_chunk(chunk_id, prompt_variant):
    # Placeholder for running chunk logic
    print(f"Running chunk {chunk_id} with prompt variant: '{prompt_variant}'")
    # Simulate success or failure
    import random
    if random.choice([True, False]):
        return True
    else:
        return False

def main():
    log_file = 'scripts/retry_log.txt'
    with open(log_file, 'a') as log:
        for chunk_id in os.listdir('distilled/'):
            file_path = os.path.join('distilled/', chunk_id)
            if validate_json(file_path):
                print(f"Chunk {chunk_id} is valid.")
            else:
                print(f"Chunk {chunk_id} is invalid. Retrying with stricter prompt...")
                success = run_chunk(chunk_id, 'Output ONLY valid JSON, no markdown, no explanations')
                if success:
                    log.write(f"{datetime.now()}: Chunk {chunk_id} succeeded after retry.\n")
                else:
                    log.write(f"{datetime.now()}: Chunk {chunk_id} failed after retry.\n")

if __name__ == "__main__":
    main()
