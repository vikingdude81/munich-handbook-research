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
REASONING_MAX_TOKENS = int(os.environ.get("MHR_REASONING_MAX_TOKENS", "8192"))

# ── Context limits ───────────────────────────────────────────────────────────
# Max chars returned to the caller when echoing a chunk or distillation back.
PROJECT_MAX_READ_CHARS = int(os.environ.get("MHR_PROJECT_MAX_READ_CHARS", "30000"))
