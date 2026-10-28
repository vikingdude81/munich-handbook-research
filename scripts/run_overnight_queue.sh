#!/usr/bin/env bash
# run_overnight_queue.sh — NIGHTLY DISTILL RUNNER. GATED: do not run until the
# user explicitly says to start (staging 2026-10-27; ingestion pre-authorized as
# a batch, execution on user word only).
#
# Usage:  bash scripts/run_overnight_queue.sh [maxTier]   (default A; B or C to include more)
# Resumable: distill_source.py skips already-distilled chunks, so re-running
# after a crash/power loss continues where it left off.
set -u
cd "$(dirname "$0")/.."

MAXTIER="${1:-A}"
LOG=_meta/overnight_run_$(date +%Y%m%d_%H%M%S).log
QUEUE=_meta/overnight_queue.json
GOALS=_meta/overnight_goals.json

# --- endpoint (same env the goetia run used) ---
export MHR_REASONING_SERVER="${MHR_REASONING_SERVER:-http://localhost:11434/v1}"
export MHR_REASONING_MODEL_ID="${MHR_REASONING_MODEL_ID:-qwen3.5:122b}"
export MHR_REASONING_NUM_CTX="${MHR_REASONING_NUM_CTX:-32768}"
export MHR_REASONING_TIMEOUT_SEC="${MHR_REASONING_TIMEOUT_SEC:-3600}"
export MHR_REASONING_KEEP_ALIVE="${MHR_REASONING_KEEP_ALIVE:-60m}"

echo "[$(date -Is)] QUEUE START maxTier=$MAXTIER model=$MHR_REASONING_MODEL_ID" | tee -a "$LOG"

# health check: ollama reachable?
if ! curl -sf "${MHR_REASONING_SERVER%/v1}/api/tags" >/dev/null 2>&1; then
    echo "[$(date -Is)] ABORT: reasoning endpoint not reachable ($MHR_REASONING_SERVER)" | tee -a "$LOG"
    exit 1
fi

ids=$(python -c "
import json
q = json.load(open('$QUEUE', encoding='utf-8'))
print(' '.join(t['id'] for t in q['queue'] if t['tier'] <= '$MAXTIER'))")

for id in $ids; do
    goal=$(python -c "import json;print(json.load(open('$GOALS', encoding='utf-8'))['$id'])")
    echo "[$(date -Is)] SMOKE $id (1 chunk)" | tee -a "$LOG"
    python scripts/distill_source.py --id "$id" --goal "$goal" --max-chunks 1 >>"$LOG" 2>&1
    if [ $? -ne 0 ]; then
        echo "[$(date -Is)] SMOKE FAILED $id — skipping track" | tee -a "$LOG"
        continue
    fi
    echo "[$(date -Is)] FULL $id" | tee -a "$LOG"
    python scripts/distill_source.py --id "$id" --goal "$goal" >>"$LOG" 2>&1
    echo "[$(date -Is)] DONE $id rc=$?" | tee -a "$LOG"
done

echo "[$(date -Is)] QUEUE COMPLETE maxTier=$MAXTIER — distilled outputs in data/distilled/<id>/ (NOT yet merged)" | tee -a "$LOG"
python scripts/munich_pipeline_diagnostic.py >>"$LOG" 2>&1
