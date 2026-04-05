# Distillation Validation Notes

## Error Handling Function

```python
def validate_and_write(jsonl_line):
    try:
        json.loads(jsonl_line)
    except Exception as e:
        logging.error(f"Chunk ID: %s, Line Number: %s, Error: {e}", chunk_id, line_number)
        with open("distill_errors.log", "a") as log_file:
            log_file.write(f"{jsonl_line}\n")
```

**Note:** This code assumes `chunk_id` and `line_number` are defined elsewhere in the context where this function is used. The error message includes both the chunk ID and line number, along with the exception details, which can be helpful for debugging.

## JSONL File Scanner

The `scan_jsonl_files()` function provides a utility to validate all distilled JSONL files:
- Returns a dictionary mapping filenames to their validation status
- Tracks valid lines vs corrupted lines per file
- Reports overall status as "fully valid" or "partially corrupted"

## Usage

```python
report = scan_jsonl_files('src/distilled/')
for file, data in report.items():
    print(f"{file}: {data['status']} ({data['valid']}/{data['corrupted']})")
```

This will output a summary of all distilled files and their integrity status.