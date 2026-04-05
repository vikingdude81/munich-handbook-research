#!/bin/bash

# Define directories
DATA_DIR="data/necro/"
DISTILLED_DIR="distilled/"

# List all chunk files in data/necro/
echo "Chunk Files:"
ls $DATA_DIR | grep -E '\.chunk$'

# List all .json files in the expected distilled/ output dir
echo "\nJSON Files:"
ls $DISTILLED_DIR | grep -E '\.json$'

# Compute diff and report missing/mismatched filenames
diff_output=$(comm -3 <(ls $DATA_DIR | grep -E '\.chunk$' | sort) <(ls $DISTILLED_DIR | grep -E '\.json$' | sort))

echo "\nMissing/Mismatched Filenames:"
echo "$diff_output"

# Inspect first 3 failing JSONs for content
if [ ! -z "$diff_output" ]; then
    echo "\nSample Error Snippets from Failing JSONs:"
    while IFS= read -r file; do
        if [[ $file == *.json ]]; then
            content=$(cat "$DISTILLED_DIR/$file")
            if [[ $content == *"error:"* ]] || [[ $content == *"null"* ]] || [[ ${#content} -lt 100 ]]; then
                echo "File: $file"
                echo "Content: $content"
                echo ""
            fi
        fi
    done <<< "$diff_output" | head -n 3
fi