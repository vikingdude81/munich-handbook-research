#!/bin/bash

# Define variables
DISTILLATIONS_DIR="src/distillations"
LOG_FILE="logs/audit_report_24.txt"

# Initialize log file
> $LOG_FILE

# Function to validate JSON and count spirits
validate_and_count() {
    local json_file=$1
    local spirit_count=0
    local missing_fields=()

    # Validate JSON syntax
    if ! jq . "$json_file" > /dev/null 2>&1; then
        echo "Invalid JSON syntax in $json_file" >> $LOG_FILE
        return 1
    fi

    # Count spirits and check for missing fields
    while IFS= read -r line; do
        spirit_count=$((spirit_count + 1))
        if ! jq '.name' <<< "$line" > /dev/null 2>&1 || ! jq '.rank' <<< "$line" > /dev/null 2>&1 || ! jq '.page_folio' <<< "$line" > /dev/null 2>&1 || ! jq '.raw_quote' <<< "$line" > /dev/null 2>&1; then
            missing_fields+=("$json_file")
        fi
    done < "$json_file"

    # Report missing fields
    if [ ${#missing_fields[@]} -gt 0 ]; then
        echo "Missing fields in $json_file: ${missing_fields[*]}" >> $LOG_FILE
    fi

    echo "File: $json_file, Spirits Count: $spirit_count" >> $LOG_FILE
}

# Scan all JSON files and validate
for json_file in "$DISTILLATIONS_DIR"/*.json; do
    if [ -f "$json_file" ]; then
        validate_and_count "$json_file"
    fi
done

echo "Audit completed. Summary logged to $LOG_FILE"
