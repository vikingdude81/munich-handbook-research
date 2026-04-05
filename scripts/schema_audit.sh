#!/bin/bash

# Define the directory containing JSON files
json_dir="distillations/necro/"

# Initialize log file
log_file="logs/schema_audit.txt"

# Check if log file exists, create it otherwise
touch $log_file

# Loop through all JSON files in the directory
for json_file in "$json_dir"/*.json; do
    # Extract filename without path and extension
    filename=$(basename "$json_file" .json)
    
    # Use jq to check for missing fields and malformed entries
    jq -e '. | 
        if has("spirit_name") then .spirit_name else error("Missing spirit_name in $filename") end |
        if has("rank") then .rank else error("Missing rank in $filename") end |
        if has("function") then .function else error("Missing function in $filename") end |
        if has("appearance") then .appearance else error("Missing appearance in $filename") end |
        if has("legion_count") then .legion_count else error("Missing legion_count in $filename") end |
        if has("conjuration_method") then .conjuration_method else error("Missing conjuration_method in $filename") end |
        if has("experiment_ref") then .experiment_ref else error("Missing experiment_ref in $filename") end |
        if has("page_folio") then .page_folio else error("Missing page_folio in $filename") end |
        if has("raw_quote") then .raw_quote else error("Missing raw_quote in $filename") end' "$json_file" > /dev/null 2>> "$log_file"
    
    # Check if jq encountered an error
    if [ $? -ne 0 ]; then
        echo "Error found in $filename. Details logged in $log_file."
    else
        echo "No errors found in $filename."
    fi
done

echo "Schema audit completed. Summary report available in $log_file."
