# Prompt Template: Phase 2 - spirit_vectors.py Generation
*Enforce provenance (chunk ID + raw_quote) and NEEDS_VERIFICATION flags*

## Requirements:

1. **Chunk ID**: Must be a string in format `chunk_001`, `chunk_002`, etc.
2. **Raw Quote**: Must be a string containing the original text (e.g., `"This is a sample quote"`).
3. **NEEDS_VERIFICATION**: Boolean flag (`True`/`False`).

## Valid Example:

```python
{
  "chunk_id": "chunk_001",
  "raw_quote": "This is a sample quote",
  "needs_verification": True
}
```

## Invalid Examples:

- Missing `chunk_id`: `{"raw_quote": "text"}`
- Invalid chunk ID: `{"chunk_id": "chunk_1", "raw_quote": "text"}`
- Non-string raw_quote: `{"chunk_id": "chunk_001", "raw_quote": 123, "needs_verification": True}`

## Usage:
Generate entries for vector training, ensuring metadata is correctly formatted.
