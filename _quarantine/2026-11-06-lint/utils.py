def batch_distill_source(source):
    def extract_json(text):
        import json
        import re
        pattern = r'```json
(.*?)
```'
        matches = re.findall(pattern, text)
        return [json.loads(match) for match in matches]

    if not source:
        return []

    lines = source.split('\n')
    start_line = None
    end_line = None

    for i, line in enumerate(lines):
        if '```' in line and ('```' not in lines[i+1] or (i == len(lines)-1)):
            start_line = i
            break

    if not start_line:
        return []

    for i, line in enumerate(reversed(lines)):
        if '```' in line and ('```' in lines[-(i+2)] or i == 0):
            end_line = len(lines) - i - 1
            break

    if not end_line:
        return []

    content = '\n'.join(lines[start_line:end_line+1])
    json_lines = extract_json(content)
    
    # Fallback to partial parsing for non-JSON responses
    fallback_lines = [line for line in lines if start_line <= lines.index(line) < end_line]
    fallback_data = {}
    for i, line in enumerate(fallback_lines):
        key, value = line.split(':', 1)
        fallback_data[key.strip()] = value.strip()

    return json_lines + [fallback_data]

# Unit tests
import unittest

class TestBatchDistillSource(unittest.TestCase):
    def test_missing_braces(self):
        self.assertEqual(batch_distill_source('```json\n{'), [{'': ''}])

    def test_trailing_comma(self):
        self.assertEqual(batch_distill_source('```json\n{}\n```'), [{}, {}])

    def test_extra_text_before_json(self):
        self.assertEqual(batch_distill_source('extra text ```json\n{} extra text ```'),
                         [{}, {}])

    def test_extra_text_after_json(self):
        self.assertEqual(batch_distill_source('```json\n{}\nextra text ```'),
                         [{'': ''}, {}])

    def test_missing_braces_in_middle(self):
        self.assertEqual(batch_distill_source('```json\n{'), [{'': ''}])

    def test_fallback_to_partial_parsing(self):
        self.assertEqual(batch_distill_source('```json\n{} extra text ```extra json\n{}\n'),
                         [{}, {}, {}])

if __name__ == '__main__':
    unittest.main()
