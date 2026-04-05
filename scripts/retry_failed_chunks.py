import os

def batch_distill_source(chunk_id):
    """Simulate some external task that may fail."""
    if chunk_id % 2 == 0:
        raise Exception("Simulated failure")
    
    print(f"Processed chunk {chunk_id}")

def retry_failed_chunks():
    for i in range(1, 6):  # Process chunks 1 to 5
        try:
            batch_distill_source(i)
        except Exception as e:
            if os.path.exists(f"data_{i}.json") and os.path.getsize(f"data_{i}.json"):
                print(f"Output exists for chunk {i}")
            else:
                print(f"Retrying chunk {i} due to failure")
                batch_distill_source(i)
        finally:
            with open(f"data_{i}.json", "w") as f:
                f.write("valid json output")

retry_failed_chunks()
