def re_distill_plan(validation_failures):
    retry_chunks = [chunk_id for chunk_id in validation_failures]
    log_retries(validation_failures)
    return retry_chunks

def log_retries(failed_chunk_ids):
    # Implementation to log failed chunk IDs separately
    pass
