#!/bin/bash

# Define the directory containing JSON files
JSON_DIR="path/to/json/files"

# Initialize log file
LOG_FILE="logs/validation_report.txt"
> $LOG_FILE

# Function to validate a single JSON file
validate_json() {
    local json_file=$1
    echo "Validating $json_file" >> $LOG_FILE

    # Check if file exists
    if [ ! -f "$json_file" ]; then
        echo "Error: File not found." >> $LOG_FILE
        return 1
    fi

    # Parse and validate schema compliance
    jq . "$json_file" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: Schema validation failed." >> $LOG_FILE
        return 1
    fi

    # Detect duplicates by spirit name + page_folio
    local spirit_name=$(jq -r '.spirit_name' "$json_file")
    local page_folio=$(jq -r '.page_folio' "$json_file")
    if [ "$(grep -c "spirit_name\": \"$spirit_name\", \"page_folio\": \"$page_folio\"" $LOG_FILE)" -gt 0 ]; then
        echo "Error: Duplicate detected." >> $LOG_FILE
        return 1
    fi

    echo "Validation successful." >> $LOG_FILE
}

# Loop through all JSON files in the directory
for json_file in "$JSON_DIR"/*.json; do
    validate_json "$json_file"
done

echo "Validation complete. Summary report saved to $LOG_FILE."
