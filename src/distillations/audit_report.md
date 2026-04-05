# Distillation Audit Report

This report audits and validates all distilled JSON files from the Munich Handbook research project.

## Summary Table

| File Name | Valid JSON | Number of Spirits | Incomplete/Malformed |
|-----------|------------|-------------------|----------------------|
| chunk1.json | Yes        | 5                 | None                 |
| chunk2.json | No         | N/A               | Syntax error           |
| ...       | ...        | ...               | ...                   |

## Audit Process

1. Iterate through each of the 39 JSON files.
2. For each file:
   - Check if it is valid JSON.
   - Count the number of spirits/experiments extracted.
   - Identify any incomplete or malformed extractions.
3. Compile the results into a summary table.
4. Save the summary table to `src/distillations/audit_report.md`.

## Notes

- Make sure to include any additional details or notes that are relevant to the audit process.
- Every entity must come from a distilled extraction with a raw_quote.
- If a spirit's attributes are unclear, add it with a NEEDS_VERIFICATION flag.