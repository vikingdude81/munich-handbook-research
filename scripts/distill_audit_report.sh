#!/bin/bash

# Define variables
output_dir="E:/munich_handbook_research/distillations"
report_file="distill_audit_report.md"

# Initialize report file
echo "# Distillation Audit Report" > $report_file

# Loop through all chunks in the output directory
for chunk_file in "$output_dir"/*.json; do
    # Check if the file is a valid JSON
    if jq . >/dev/null 2>&1; then
        echo "Valid JSON: $(basename $chunk_file)" >> $report_file
    else
        # Identify error type
        error_type=$(jq . 2>&1 | grep -oP 'error: \K.*')
        echo "Malformed JSON: $(basename $chunk_file) - Error Type: $error_type" >> $report_file
    fi
done

# Count valid and malformed files
valid_count=$(grep -c "Valid JSON:" $report_file)
malformed_count=$(grep -c "Malformed JSON:" $report_file)

# Add summary to report file
echo "" >> $report_file
echo "Summary:" >> $report_file
echo "- Valid JSON Files: $valid_count" >> $report_file
echo "- Malformed JSON Files: $malformed_count" >> $report_file

echo "Audit completed. Report saved to $report_file"
