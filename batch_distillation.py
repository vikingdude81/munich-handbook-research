def run_batch_distillation(source_files, retry_on_error=True):
    for file in source_files:
        retries = 0
        max_retries = 3
        while True:
            try:
                batch_distill_source(file, retry_on_error=retry_on_error)
                break
            except Exception as e:
                retries += 1
                if retries < max_retries:
                    print(f"Retrying distillation on {file} ({retries}/{max_retries}): {e}")
                else:
                    print(f"Failed to distill {file} after {max_retries} attempts. "
                          f"Applying fallback heuristic extraction.")
                    # Apply regex and keyword search to salvage spirit names/ranks from raw text
                    break


# Example usage
# run_batch_distillation(["source1.txt", "source2.txt"])
