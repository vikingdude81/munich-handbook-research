# Distillation Failures Report

## Iterations 136-143 Failure Summary

| Chunk ID | Error Type | Sample Raw Output |
|----------|------------|--------------------|
| chunk_05 | JSONDecodeError: invalid character in json text at position 2 | {"key": "value\u0000"} |
| chunk_17 | ValueError: unsupported operand type(s) for -: 'str' and 'int' | "3 - 4" |
| chunk_29 | KeyError: 'missing_field' | {"data": ["some", "values"]} |
| chunk_41 | TypeError: can only concatenate str (not "list") to str | [1, 2] |
| chunk_53 | UnicodeEncodeError: 'charmap' codec can't encode character at position 7 | "hello\u0000world" |

## Notes:
- Chunk IDs are in the format `chunk_<number>`.
- Error types and sample raw outputs are provided for each failure.
- Ensure to handle these errors appropriately in your codebase.