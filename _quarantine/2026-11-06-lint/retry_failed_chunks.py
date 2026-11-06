failed_chunks = [
    "chunk1",
    "chunk3",
    "chunk5"
]

for chunk_id in failed_chunks:
    try:
        # Attempt to run batch_distill_source with 120B Thinker
        result = batch_distill_source(chunk_id, model="120B-Thinker")
        
        if result["success"]:
            print(f"Chunk {chunk_id} distillation succeeded.")
            os.rename(f".tmp/{chunk_id}", f"{chunk_id}")
        else:
            print(f"Chunk {chunk_id} distillation failed: {result['message']}")
    except Exception as e:
        print(f"Error processing chunk {chunk_id}: {e}")

print("Distillation process completed.")
