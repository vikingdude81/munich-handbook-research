#!/bin/bash

# Define the directory to scan
DIR="distill/"

# Function to validate and repair a JSON file
repair_json() {
    local file=$1
    local retries=0
    while [ $retries -lt 2 ]; do
        if jq . "$file" > /dev/null 2>&1; then
            echo "Success: $file is valid."
            return 0
        else
            echo "Error: $file is corrupt. Retrying..."
            retries=$((retries + 1))
        fi
    done
    echo "Failure: $file could not be repaired after 2 attempts."
    return 1
}

# Scan the directory for .json files and repair them
for file in "$DIR"/*.json; do
    if [ -f "$file" ]; then
        repair_json "$file"
    fi
done
