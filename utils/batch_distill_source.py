import os
import time

def batch_distill_source(data, filename, max_retries=2, delay=1):
    temp_filename = f"{filename}.tmp"
    for attempt in range(max_retries + 1):
        try:
            with open(temp_filename, 'w') as f:
                json.dump(data, f)
            os.rename(temp_filename, filename)
            return
        except (FileExistsError, PermissionError) as e:
            if attempt < max_retries:
                time.sleep(delay)
                continue
        except Exception as e:
            if attempt < max_retries:
                time.sleep(delay)
            else:
                raise
