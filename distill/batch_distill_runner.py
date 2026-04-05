import logging
from typing import List, Dict

def run_distillation(chunk_id: int) -> bool:
    """Simulate distillation process for a given chunk."""
    try:
        # Simulate distillation process
        logging.info(f"Distilling chunk {chunk_id}")
        return True  # Assume successful distillation
    except Exception as e:
        logging.error(f"Failed to distill chunk {chunk_id}: {e}")
        return False

def resilient_batch_runner(tasks: List[int], retries: int = 3) -> List[int]:
    """Run batch distillation with retry logic for failed chunks."""
    for _ in range(retries):
        failed_chunks = []
        for task in tasks:
            if not run_distillation(task):
                failed_chunks.append(task)
        if not failed_chunks:
            break
    else:  # Loop body executed without breaking out of the loop
        logging.error("All retries failed, some chunks may be incomplete.")
    
    return failed_chunks

# Example usage: distill chunks 141-150 with retry logic
failed_chunks = resilient_batch_runner([141 + i for i in range(10)], retries=3)
logging.info(f"Failed to distill chunks: {failed_chunks}")