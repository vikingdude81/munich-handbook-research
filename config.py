"""
config.py — standalone configuration for the distillation tools.

`tools/source_distill.py` was written to run inside a parent "AI Command Center"
host and did `import config` for the reasoning-model endpoint. That host module
is not part of this repo, so the tool could not run on its own. This file
restores standalone operation; every value is overridable by environment
variable so no secrets or box-specific paths are hard-coded.
"""

import os

# ── Reasoning / distillation model (OpenAI-compatible endpoint, e.g. LM Studio) ──
REASONING_SERVER = os.environ.get("MHR_REASONING_SERVER", "http://192.168.50.150:1234/v1")
REASONING_MODEL_ID = os.environ.get("MHR_REASONING_MODEL_ID", "google/gemma-4-26b-a4b")
REASONING_API_KEY = os.environ.get("MHR_REASONING_API_KEY", "lm-studio")
REASONING_MAX_TOKENS=int(os.environ.get("MHR_REASONING_MAX_TOKENS", "8192"))
# Ollama's OpenAI-compat endpoint defaults to a small context window and silently
# truncates long prompts; pass its native options.num_ctx through extra_body.
# 0 = do not send (LM Studio manages context server-side).
REASONING_NUM_CTX=int(os.environ.get("MHR_REASONING_NUM_CTX", "0"))
# Request timeout in seconds. Ollama loading an 81 GB model can far exceed the
# OpenAI SDK default (600 s). Also keeps the model resident between chunks.
REASONING_TIMEOUT_SEC=int(os.environ.get("MHR_REASONING_TIMEOUT_SEC", "600"))
REASONING_KEEP_ALIVE=os.environ.get("MHR_REASONING_KEEP_ALIVE", "")  # e.g. "60m"

# ── Context limits ───────────────────────────────────────────────────────────
# Max chars returned to the caller when echoing a chunk or distillation back.
PROJECT_MAX_READ_CHARS = int(os.environ.get("MHR_PROJECT_MAX_READ_CHARS", "30000"))
