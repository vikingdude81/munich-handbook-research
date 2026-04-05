#!/bin/bash

# Define the directory containing the JSON files
DIR="data/distillations/"

# Loop through each file in the directory
for FILE in "$DIR"/*.json; do
  # Check if the file exists
  if [ ! -f "$FILE" ]; then
    echo "File not found: $FILE"
    continue
  fi

  # Use jq to validate the JSON file
  if ! jq . "$FILE" > /dev/null 2>&1; then
    echo "Malformed JSON in file: $FILE"
    # Extract chunk ID from filename (assuming format is chunk_XXX.json)
    CHUNK_ID=$(basename "$FILE" | sed 's/^chunk_\([0-9]*\)\.json/\1/')
    echo "Chunk ID: $CHUNK_ID"
  fi
done
