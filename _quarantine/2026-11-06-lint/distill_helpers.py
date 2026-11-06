def re_run_batch_distill(chunks_with_issues):
    for chunk in chunks_with_issues:
        if isinstance(chunk, dict) and "spirits" not in chunk or not chunk:
            print(f"Re-running batch_distill_source on invalid chunk: {chunk}")
            # Re-run batch_distill_source only on this specific chunk
            re_run_batch_distill_source(chunk)
