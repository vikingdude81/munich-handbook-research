# Distillation Issues Analysis

## Common Problems Observed

1. **Improperly formatted JSON input**: Ensure prompts are correctly structured to enforce proper JSON syntax.

2. **Missing or incorrect field values**: Use more specific and contextually relevant examples in the prompt to guide correct responses.

3. **Inconsistent data types**: Implement stricter schema validation with additional type checks within the LLM post-processing.

4. **Incorrect date/time formats**: Provide explicit examples of valid date/time formats in the prompt, along with regex for validating input.

5. **Ambiguous or missing context**: Clarify context and provide more detailed examples to guide responses, possibly using chunk splitting heuristics to break down complex prompts into manageable parts.

## Recommendations

- Validate all JSON outputs against a strict schema before processing
- Include example values in prompts for fields that may be ambiguous
- Use regex patterns to validate date/time formats
- Consider implementing post-processing validation layers
