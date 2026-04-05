#!/bin/bash

# Define the directory containing the JSON files
json_dir="src/distillations/"

# Define the required fields
required_fields=("spirit_name" "rank" "function" "appearance" "legion_count" "conjuration_method" "experiment_ref" "page_folio" "raw_quote")

# Initialize an array to store validation results
validation_results=()

# Loop through all JSON files in the directory
for json_file in "$json_dir"/*.json; do
    # Check if file exists
    if [ ! -f "$json_file" ]; then
        echo "File not found: $json_file"
        continue
    fi

    # Validate JSON format
    if ! jq . "$json_file" > /dev/null 2>&1; then
        echo "Invalid JSON format in file: $json_file"
        continue
    fi

    # Check for required fields
    missing_fields=()
    for field in "${required_fields[@]}"; do
        if ! jq -e --arg field "$field" '. | has($field)' "$json_file" > /dev/null 2>&1; then
            missing_fields+=("$field")
        fi
    done

    # Store validation result
    if [ ${#missing_fields[@]} -eq 0 ]; then
        validation_results+=("PASS: $json_file")
    else
        validation_results+=("FAIL: $json_file (Missing fields: ${missing_fields[*]})")
    fi
done

# Output summary report to logs/validation_report_67.txt
echo "Validation Report:" > logs/validation_report_67.txt
for result in "${validation_results[@]}"; do
    echo "$result" >> logs/validation_report_67.txt
done

echo "Validation complete. Summary report saved to logs/validation_report_67.txt"
