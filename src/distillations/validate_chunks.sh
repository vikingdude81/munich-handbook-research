#!/bin/bash

# Define the directory containing the chunk files
output_dir="src/distillations/"

# Create log file if it doesn't exist
touch distillation_errors.log

# Initialize error count
error_count=0

# Loop through all chunk_*.json files in the output directory
for json_file in "$output_dir"chunk_*.json; do
    # Check if the file exists
    if [ ! -f "$json_file" ]; then
        echo "File not found: $json_file"
        continue
    fi

    # Validate JSON syntax using jq
    if ! jq . "$json_file" > /dev/null 2>&1; then
        echo "Invalid JSON in file: $json_file" >> distillation_errors.log
        ((error_count++))
    else
        echo "Valid JSON in file: $json_file"
    fi
done

# Report the number of errors
if [ "$error_count" -eq 0 ]; then
    echo "All chunk files are valid."
else
    echo "Validation complete. Found $error_count invalid chunk files. Check distillation_errors.log for details."
fi