import json
from jsonschema import validate, ValidationError
from retry_decorator import retry, retry_count

@retry(max_retries=2)
def batch_distill_source(chunk_id, strict=True):
    # Simulated distillation process
    if chunk_id % 2 == 0:
        return {"status": "success", "chunk_id": chunk_id}
    else:
        raise ValidationError("Chunk failed to distill")

def main():
    schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
            "chunk_id": {"type": "integer"}
        },
        "required": ["status", "chunk_id"]
    }
    
    try:
        # Enforce strict JSON schema via system message
        print("Enforcing strict JSON schema...")
        validate(instance={"status": "success", "chunk_id": 1}, schema=schema)
        
        # Process failed chunks
        for chunk_id in range(1, 10):
            result = batch_distill_source(chunk_id)
            if result["status"] == "failure":
                print(f"Re-distilling chunk {chunk_id}")
                # Re-process with strict mode
                reprocessed_result = batch_distill_source(chunk_id, strict=True)
                print(f"Processed chunk {chunk_id} successfully")
    except ValidationError as e:
        print(f"Validation error: {e.message}")

if __name__ == "__main__":
    main()
