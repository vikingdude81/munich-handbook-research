#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
src/json_repair.py — THE canonical LLM-JSON recovery module.

Replaces four scattered, unimported implementations (`robust_json_parser.py`,
`src/json_repair_utils.py`, `src/json_recovery.py`, `src/utils/json_fix.py`) and
the inline `_repair_json` in `tools/source_distill.py`. Consolidates the proven
recovery ladder from `scripts/distill_heresy_revolution_v3.py`.

API:
    parse_llm_json(raw) -> (obj | None, recovered: bool)
        Best-effort parse of a model response into a dict. `recovered` is True
        when fallbacks beyond a clean parse were needed.

Recovery ladder:
    1. strip <think>/<thinking> blocks and ```json fences
    2. json.JSONDecoder().raw_decode from the first '{' (ignores trailing prose)
    3. trailing-comma cleanup, retry raw_decode
    4. brace/bracket balancing for truncated output, retry
    5. caller-supplied field extractor (optional) for partial recovery
"""

import json
import re

_THINK_RE = re.compile(r"<think(?:ing)?>\s*.*?\s*</think(?:ing)?>", re.DOTALL)
_FENCE_OPEN = re.compile(r"^```(?:json)?\s*", re.MULTILINE)
_FENCE_CLOSE = re.compile(r"\s*```$", re.MULTILINE)
_TRAILING_COMMA = re.compile(r",\s*([}\]])")


def strip_wrappers(text: str) -> str:
    """Remove think blocks and markdown code fences."""
    text = _THINK_RE.sub("", text)
    text = _FENCE_OPEN.sub("", text)
    text = _FENCE_CLOSE.sub("", text)
    return text.strip()


def clean_trailing_commas(text: str) -> str:
    return _TRAILING_COMMA.sub(r"\1", text)


def _balance_truncated(s: str) -> str:
    """Close unbalanced braces/brackets on truncated JSON (string-aware)."""
    depth_b = depth_s = 0
    in_str = escape = False
    last_obj_close = -1
    for i, c in enumerate(s):
        if escape:
            escape = False
            continue
        if c == "\\" and in_str:
            escape = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == "{":
            depth_b += 1
        elif c == "}":
            depth_b -= 1
            last_obj_close = i
        elif c == "[":
            depth_s += 1
        elif c == "]":
            depth_s -= 1
    if depth_b <= 0 and depth_s <= 0:
        return s
    # Trim back to the last complete object close if we're mid-element
    if last_obj_close > len(s) // 2:
        s = s[: last_obj_close + 1]
    s = re.sub(r",\s*$", "", s.rstrip())
    s += "]" * max(0, s.count("[") - s.count("]"))
    s += "}" * max(0, s.count("{") - s.count("}"))
    return s


def parse_llm_json(raw: str, field_recovery=None):
    """
    Parse a model response into a dict. Returns (obj_or_None, recovered_bool).

    field_recovery: optional callable(raw_str) -> dict, used as a last resort
        for partial field-level extraction from irreparable output.
    """
    if not raw:
        return None, False
    text = strip_wrappers(raw)
    decoder = json.JSONDecoder()

    # 1. clean parse from first brace
    brace = text.find("{")
    if brace != -1:
        try:
            obj, _ = decoder.raw_decode(text, brace)
            return obj, False
        except json.JSONDecodeError:
            pass

    # 2. trailing-comma cleanup
    cleaned = clean_trailing_commas(text)
    brace = cleaned.find("{")
    if brace != -1:
        try:
            obj, _ = decoder.raw_decode(cleaned, brace)
            return obj, True
        except json.JSONDecodeError:
            pass

    # 3. balance truncated output
    if brace != -1:
        balanced = _balance_truncated(cleaned[brace:])
        try:
            return json.loads(balanced), True
        except json.JSONDecodeError:
            pass

    # 4. caller field-level recovery
    if field_recovery is not None:
        try:
            return field_recovery(text), True
        except Exception:
            pass

    return None, False


if __name__ == "__main__":
    # tiny self-test
    tests = [
        '{"a": 1, "b": [1,2,3]}',
        '```json\n{"a": 1,}\n```',
        '<think>hmm</think>{"a": 1, "b": "x"}trailing prose',
        '{"a": 1, "b": [1, 2,',            # truncated
    ]
    for t in tests:
        obj, rec = parse_llm_json(t)
        print(f"recovered={rec}  ->  {obj}")
