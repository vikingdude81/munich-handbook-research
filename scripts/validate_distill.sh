#!/bin/bash

log_file="distill_status.log"
invalid_count=0
total_files=39

for file in distill/*.json; do
    if [ ! -s "$file" ]; then
        echo "File $file is empty or does not exist." >> $log_file
        ((invalid_count++))
        continue
    fi

    json_data=$(cat "$file")
    if ! echo "$json_data" | jq . > /dev/null 2>&1; then
        echo "JSON parsing error in file $file." >> $log_file
        ((invalid_count++))
        continue
    fi

    spirits=$(echo "$json_data" | jq -r '.spirits[]?')
    if [ -z "$spirits" ]; then
        echo "No 'spirits' list found in file $file." >> $log_file
        ((invalid_count++))
        continue
    fi

    while read spirit; do
        name=$(echo "$spirit" | jq -r '.name?')
        raw_quote=$(echo "$spirit" | jq -r '.raw_quote?')
        chunk_ref=$(echo "$spirit" | jq -r '.chunk_ref?')

        if [ -z "$name" ] || [ -z "$raw_quote" ] || [ -z "$chunk_ref" ]; then
            echo "Invalid spirit entry in file $file: missing 'name', 'raw_quote', or 'chunk_ref'." >> $log_file
            ((invalid_count++))
        fi
    done <<< "$spirits"
done

if (( invalid_count > total_files * 0.1 )); then
    echo "More than 10% of files are invalid. Rerun failed chunks."
else
    echo "All files validated successfully."
fi
