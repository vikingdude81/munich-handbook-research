"""
Mock LLM function for standalone testing.

This module provides a mock LLM function for testing purposes.
Replace with actual LLM client in production.
"""

import json

def llm(prompt: str, temperature: float = 0, constraints: str = None) -> str:
    """
    Mock LLM function - replace with actual LLM client.

    Args:
        prompt: The distillation prompt
        temperature: Sampling temperature (0.0-1.0)
        constraints: Optional constraint string for strict mode

    Returns:
        Mock LLM response as JSON string
    """
    # TODO: Replace with actual LLM client call
    return json.dumps({
        "spirit_name": "mock_spirit",
        "rank": "mock_rank",
        "provenance": "chunk_0, passage 1-5"
    })