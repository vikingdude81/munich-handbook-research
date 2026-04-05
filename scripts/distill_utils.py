import json
import os
from datetime import datetime
import logging
from functools import wraps
import time

LOG_DIR = "logs/distill_failures"
os.makedirs(LOG_DIR, exist_ok=True)

def retry_with_logging(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                    # Resume from last successful chunk
                    with open("resume_pos.txt", "r") as f:
                        resume_chunk = int(f.read())
                    # Write to resume_pos.txt after success
                    with open("resume_pos.txt", "w") as f:
                        f.write(str(resume_chunk + 1))
                    return result
                except Exception as e:
                    logging.error(f"Attempt {retries+1} failed: {str(e)}")
                    if retries < max_retries:
                        logging.info(f"Retrying in {delay}s...")
                        time.sleep(delay)
                        retries += 1
                    else:
                        # Log failure and exit
                        with open(os.path.join(LOG_DIR, f"failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"), 'w') as f:
                            json.dump({"error": str(e), "response": str(result)}, f)
                        return None
            return None
        return wrapper
    return decorator

def validate_json(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a dictionary")
    if not data.get("data") or not isinstance(data["data"], list):
        raise ValueError("Missing or invalid 'data' field in JSON")
    for chunk in data["data"]:
        if not isinstance(chunk, dict) or not chunk.get("content"):
            raise ValueError(f"Invalid chunk: {chunk}")
    return data

def distill_with_retry_and_logging(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Validate JSON before writing back
        try:
            validate_json(kwargs["data"])
        except Exception as e:
            logging.error(f"JSON validation failed: {str(e)}")
            return None
        
        # Attempt distillation with retries
        retry_decorator = retry_with_logging()
        result = retry_decorator(func, *args, **kwargs)
        if result is not None:
            # Save resume position
            with open("resume_pos.txt", "w") as f:
                f.write(str(result["chunk"]))
            return result
        else:
            return None

    return wrapper