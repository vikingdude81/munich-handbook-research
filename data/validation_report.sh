#!/bin/bash

# Define the output file
output_file="data/validation_report.json"

# Initialize an empty array to store validation results
results=()

# Loop through all distilled JSON files
for json_file in data/distilled/chunk_*.json; do
  # Extract chunk_id from filename
  chunk_id=$(basename "$json_file" .json)

  # Validate JSON and capture output
  json_output=$(jq . "$json_file" 2>&1)

  if [ $? -eq 0 ]; then
    status="success"
  else
    status="failed"
    error_type=$(echo "$json_output" | grep -oP 'error: \K.*')
    results+=("{\"chunk_id\": \"$chunk_id\", \"status\": \"$status\", \"error_type\": \"$error_type\"}")
  fi

  # Log validation result
  echo "Chunk ID: $chunk_id, Status: $status"
done

# Write results to output file
echo "[${results[*]}]" > "$output_file"

# Summary report
echo "Validation complete. Results saved in $output_file"
