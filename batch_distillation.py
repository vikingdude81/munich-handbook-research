def run_batch_distillation(source_files):
    for file in source_files:
        try:
            batch_distill_source(file, --retry-on-error)
        except Exception as e:
            if retries < 3:
                retries += 1
                print(f"Retrying distillation on {file} ({retries}/3)")
                run_batch_distillation([file])
            else:
                print(f"Failed to distill {file}. Applying fallback heuristic extraction.")
                # Apply regex and keyword search for salvage spirit names/ranks from raw text

# Example usage
run_batch_distillation(["source1.txt", "source2.txt"])
