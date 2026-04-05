#!/bin/bash

# Generate list of chunk IDs that are missing/invalid JSON
find /path/to/json/files -type f -name "*.json" | while read json_file; do
  chunk_id=$(basename "$json_file" .json)
  if ! jq --exit-status . <"$json_file"; then
    echo "Invalid or missing JSON: $chunk_id"
  fi
done > logs/missing_chunks_71.txt

# Spawn batch_distill_source for each with retries and timeout, log success/failure per chunk
while read -r json_file; do
  chunk_id=$(basename "$json_file" .json)
  echo "Processing chunk: $chunk_id"
  output_log="${json_file%.json}_distilled.log"
  if ! batch_distill_source --retries=3 --timeout=600 "$json_file" >"$output_log"; then
    echo "Chunk $chunk_id failed to distill."
  else
    echo "Chunk $chunk_id successfully distilled."
  fi
done < logs/missing_chunks_71.txt

echo "Distillation process completed. Logs are in logs/distillation_repair_71.log"
cat logs/*.log > logs/distillation_repair_71.log
