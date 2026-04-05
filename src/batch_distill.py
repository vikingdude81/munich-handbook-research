import os
from retry import retry

def batch_distill_source(chunk_number):
    try:
        # Simulate distillation process
        result = f"distilled_chunk_{chunk_number}.json"
        with open(f"distillations/necro/{result}", "w") as f:
            f.write("distilled_data")
        return True
    except Exception as e:
        print(f"Error processing chunk {chunk_number}: {e}")
        return False

for chunk in range(21, 40):
    if batch_distill_source(chunk):
        print(f"Chunk {chunk} processed successfully.")
    else:
        print(f"Retry chunk {chunk} (attempt 1/3).")
