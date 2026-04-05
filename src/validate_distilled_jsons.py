import json

def audit_distilled_files(total_files=39):
    """
    Audit the 39 distilled JSON files to validate parseability and extract metadata.
    
    Args:
        total_files: Number of JSON files to process (default 39)
    
    Returns:
        Dictionary with success/failure counts and lists of failures/retry candidates
    """
    success_count = 0
    failure_count = 0
    failures = []
    retry_candidates = []
    
    for i in range(1, total_files + 1):
        filename = f"file_{i}.json"
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                raw_quote = data.get('raw_quote')
                chunk_id = data.get('chunk_id')
                if raw_quote is not None and chunk_id is not None:
                    success_count += 1
                else:
                    failure_count += 1
                    failures.append(filename)
                    retry_candidates.append(filename)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON in {filename}: {e}")
            failure_count += 1
            failures.append(filename)
    
    # Generate summary report
    print(f"Total files: {total_files}")
    print(f"Success count: {success_count}")
    print(f"Failure count: {failure_count}")
    print("Failures:")
    for fail in failures:
        print(fail)
    print("Retry candidates:")
    for retry in retry_candidates:
        print(retry)
    
    return {
        "total_files": total_files,
        "success_count": success_count,
        "failure_count": failure_count,
        "failures": failures,
        "retry_candidates": retry_candidates
    }
