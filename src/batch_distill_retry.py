import time

def run_batch_distill(chunk_id):
    # Simulate distillation process
    if not isinstance(chunk_id, int) or chunk_id < 0:
        raise ValueError("Invalid chunk ID")
    
    error_logs = {
        "not found": True,
        "JSON decode error": False
    }
    
    if error_logs.get(f"not found", False):
        print(f"Re-running batch_distill_source for chunk {chunk_id} due to 'not found' error.")
        # Simulate retry logic with exponential backoff
        time.sleep(2)  # First attempt
        time.sleep(4)  # Second attempt, double the previous delay
        time.sleep(8)  # Third attempt, quadruple the previous delay
        batch_distill_source(chunk_id)
    elif error_logs.get("JSON decode error", False):
        print(f"Re-running batch_distill_source for chunk {chunk_id} due to 'JSON decode error'.")
        # Simulate retry logic with exponential backoff
        time.sleep(2)  # First attempt
        time.sleep(4)  # Second attempt, double the previous delay
        time.sleep(8)  # Third attempt, quadruple the previous delay
        batch_distill_source(chunk_id)
    else:
        print(f"batch_distill_source executed successfully for chunk {chunk_id}.")

def batch_distill_source(chunk_id):
    # Placeholder function to simulate distillation process
    print(f"Executing batch_distill_source for chunk {chunk_id}")

# Example usage: Identify and re-run specific chunks
invalid_chunk_ids = [1, 3, 5]  # List of invalid chunk IDs
for id in invalid_chunk_ids:
    run_batch_distill(id)
