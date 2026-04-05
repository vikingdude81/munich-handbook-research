#!/bin/bash

# Initialize log file
LOG_FILE="logs/validation_report.md"
touch $LOG_FILE

# Loop through all 39 JSON files in the distillation output directory
for FILE in distillation_output/*.json; do
    # Extract filename without path
    BASENAME=$(basename "$FILE")
    
    # (a) Confirm file exists
    if [ ! -f "$FILE" ]; then
        echo "File not found: $BASENAME" >> $LOG_FILE
        continue
    fi
    
    # (b) Parse as valid JSON
    if ! jq . "$FILE" > /dev/null 2>&1; then
        echo "Invalid JSON: $BASENAME" >> $LOG_FILE
        continue
    fi
    
    # (c) Extract and log missing/empty 'spirits' or 'experiments' arrays
    SPIRITS=$(jq '.spirits | length' "$FILE")
    EXPERIMENTS=$(jq '.experiments | length' "$FILE")
    
    if [ "$SPIRITS" -eq 0 ]; then
        echo "Missing or empty 'spirits' array in $BASENAME" >> $LOG_FILE
    fi
    
    if [ "$EXPERIMENTS" -eq 0 ]; then
        echo "Missing or empty 'experiments' array in $BASENAME" >> $LOG_FILE
    fi
    
    # (d) Collect unique spirit names per chunk with raw_quote
    SPIRIT_NAMES=$(jq '.spirits[] | .name' "$FILE")
    
    for NAME in $SPIRIT_NAMES; do
        echo "Unique Spirit Name: $NAME" >> $LOG_FILE
    done
done

echo "Validation report generated at $LOG_FILE"
