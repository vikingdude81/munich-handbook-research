#!/bin/bash

# Define the directory containing the JSON files
output_dir="path/to/output/directory"

# Loop through all 39 distilled JSON files
for i in {01..39}
do
    file="${output_dir}/necro_${i}_distilled.json"
    
    # Check if the file exists and has non-zero size
    if [ ! -s "$file" ]; then
        echo "Missing or incomplete file: $file"
    fi
done
