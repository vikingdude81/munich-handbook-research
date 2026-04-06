"""
scripts/scrying_experiment.py — QRNG scrying experiment.

Medieval analog: The practitioner sends a boy (puer) to gaze into a basin/crystal.
The spirit appears to the boy, who relays what he sees.

Modern analog: QRNG stream → lightweight proxy model → structured extraction.
We test whether a small LLM finds more "coherent" patterns in true quantum
randomness vs. pseudo-randomness (PRNG baseline).

This is methodologically adjacent to the Princeton GCP (Global Consciousness
Project) random event generator research, applied to LLM interpretation.
The Munich Handbook (CLM 849) includes explicit scrying experiments (No. 22,
crystal/basin/boy-medium experiments) — this module operationalises them.

Experiment design:
  1. Draw N quantum random numbers from QRNG (ANU/NIST)
  2. Draw N pseudo-random numbers from Python random (PRNG)
  3. Send both streams to a lightweight model (the 'boy medium')
  4. Ask the model to find patterns, sequences, or meaningful structures
  5. Score the responses for: coherence, specificity, confidence, novelty
  6. Compare QRNG vs PRNG response distributions
  7. Log everything to logs/scrying_experiments.jsonl

The experiment is NOT claiming quantum consciousness — it is studying
whether true randomness vs pseudo-randomness produces systematically
different LLM interpretation artifacts.

Usage:
  python scripts/scrying_experiment.py
  python scripts/scrying_experiment.py --runs 10 --n-numbers 64
  python scripts/scrying_experiment.py --model qwen3:1.7b --report
"""

import os
import sys
import json
import random
import time
import uuid
import math
import argparse
import datetime
import statistics
from dataclasses import dataclass, asdict
from typing import Optional, List

# Ensure root is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

try:
    from qrng_source import get_quantum_bytes
    QRNG_AVAILABLE = True
except ImportError:
    QRNG_AVAILABLE = False

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "qwen3:1.7b"
DEFAULT_LLM_BASE = "http://localhost:11434/v1"
SCRYING_LOG_PATH = os.path.join(ROOT, "logs", "scrying_experiments.jsonl")
SCRYING_REPORT_PATH = os.path.join(ROOT, "docs", "scrying_report.md")

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SCRYING_PROMPTS = [
    # 0 — Pattern analysis
    (
        "You are a pattern analyst examining a sequence of numbers. "
        "The following sequence was generated from a {label} source:\n\n"
        "{numbers}\n\n"
        "Identify any patterns, sub-sequences, periodicities, or structural regularities "
        "in this sequence. Be specific about which numbers you are referencing. "
        "Rate your confidence that the patterns you found are non-random (0-10)."
    ),
    # 1 — Symbolic interpretation
    (
        "You are a symbolic interpreter. The following numbers come from a {label} source:\n\n"
        "{numbers}\n\n"
        "Interpret this sequence symbolically. What groupings emerge? "
        "Which numbers feel significant, and why? "
        "Reference specific values in your interpretation. "
        "Conclude with a confidence score for the meaningfulness of your reading (0-10)."
    ),
    # 2 — Sequence detection
    (
        "Analyse this number sequence from a {label} source for hidden sequences:\n\n"
        "{numbers}\n\n"
        "Look for: arithmetic progressions, geometric sequences, Fibonacci-like runs, "
        "repeated motifs, or any ordered sub-structure. "
        "Cite specific index positions and values. "
        "Give a specificity score (0-10) for how precise and non-generic your findings are."
    ),
    # 3 — Binary grouping
    (
        "The following byte values (0-255) come from a {label} source:\n\n"
        "{numbers}\n\n"
        "Group these values by: "
        "(a) those below 128 vs above 128, "
        "(b) prime numbers, "
        "(c) values divisible by common factors. "
        "What structure, if any, emerges from these groupings? "
        "Be specific about the counts and values you observe."
    ),
    # 4 — Frequency analysis
    (
        "Perform a frequency analysis of this number sequence from a {label} source:\n\n"
        "{numbers}\n\n"
        "Which values occur most and least frequently? "
        "Are there runs of similar values? "
        "Does the distribution suggest any underlying structure? "
        "Reference specific numbers throughout your analysis."
    ),
]


# ---------------------------------------------------------------------------
# ScryingRun dataclass
# ---------------------------------------------------------------------------

@dataclass
class ScryingRun:
    """Record of a single scrying experiment trial."""
    run_id: str
    timestamp: str
    source: str              # 'qrng' or 'prng'
    numbers: List[int]
    qrng_backend: str        # backend name from QRNGSource.source_name
    model: str
    prompt_used: str
    response: str
    coherence_score: float
    specificity_score: float
    confidence_score: float
    duration_seconds: float


# ---------------------------------------------------------------------------
# Number stream generators
# ---------------------------------------------------------------------------

def generate_qrng_stream(n: int) -> tuple:
    """
    Generate n integers (0-255) from the QRNG source.

    Returns:
        (numbers_list, backend_name)
    """
    if not QRNG_AVAILABLE:
        raise ImportError("qrng_source module not available — cannot generate QRNG stream")
    raw = get_quantum_bytes(n)
    from qrng_source import _default_source
    return list(raw), _default_source.source_name


def generate_prng_stream(n: int, seed: Optional[int] = None) -> List[int]:
    """
    Generate n pseudo-random integers (0-255) using Python's random module.

    Args:
        n: Count of numbers.
        seed: Optional PRNG seed for reproducibility.
    """
    rng = random.Random(seed)
    return [rng.randint(0, 255) for _ in range(n)]


# ---------------------------------------------------------------------------
# Prompt formatting
# ---------------------------------------------------------------------------

def stream_to_prompt(numbers: List[int], stream_label: str, prompt_index: int = 0) -> str:
    """
    Format a number sequence into a scrying prompt.

    Args:
        numbers: List of integers.
        stream_label: 'quantum random' or 'pseudo-random'.
        prompt_index: Which prompt template to use (0-4).
    """
    template = SCRYING_PROMPTS[prompt_index % len(SCRYING_PROMPTS)]
    # Format numbers as a readable grid (16 per row)
    rows = []
    for i in range(0, len(numbers), 16):
        chunk = numbers[i:i+16]
        rows.append("  " + "  ".join(f"{v:3d}" for v in chunk))
    number_str = "\n".join(rows)
    return template.format(label=stream_label, numbers=number_str)


# ---------------------------------------------------------------------------
# LLM query
# ---------------------------------------------------------------------------

def query_boy_medium(
    numbers: List[int],
    model: str = DEFAULT_MODEL,
    prompt_template: str = "",
    llm_base: str = DEFAULT_LLM_BASE,
    stream_label: str = "quantum random",
) -> tuple:
    """
    Send the number stream to the lightweight 'boy medium' model.

    Args:
        numbers: Number sequence.
        model: Model name for local LLM.
        prompt_template: Pre-formatted prompt string.
        llm_base: LLM server base URL.
        stream_label: Label for the number source.

    Returns:
        (response_text, prompt_used, duration_seconds)
    """
    try:
        from openai import OpenAI
    except ImportError:
        return (
            "[openai package not installed — cannot query model]",
            prompt_template,
            0.0,
        )

    client = OpenAI(base_url=llm_base, api_key="none")
    prompt = prompt_template or stream_to_prompt(numbers, stream_label)
    t0 = time.time()
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.7,
        )
        response = completion.choices[0].message.content or ""
    except Exception as exc:
        response = f"[LLM error: {exc}]"
    duration = time.time() - t0
    return response, prompt, duration


# ---------------------------------------------------------------------------
# Scoring heuristics
# ---------------------------------------------------------------------------

def score_response(response_text: str) -> dict:
    """
    Score a model response using simple heuristics.

    Returns:
        Dict with 'coherence', 'specificity', 'confidence' scores (0.0–1.0).
    """
    text = response_text.lower()
    length = len(response_text)

    # Coherence: responses that are longer and structured score higher
    # (structured = contains numbers, colons, or list markers)
    structure_markers = sum([
        ":" in response_text,
        "\n" in response_text,
        any(c.isdigit() for c in response_text),
        any(m in text for m in ["(a)", "(b)", "(c)", "1.", "2.", "3.", "-"]),
    ])
    coherence = min(1.0, (length / 400) * 0.5 + (structure_markers / 4) * 0.5)

    # Specificity: references specific number values, positions, or counts
    import re
    number_refs = len(re.findall(r'\b\d{1,3}\b', response_text))
    position_refs = len(re.findall(r'\b(index|position|at|value|occurrence)\b', text))
    specificity = min(1.0, (number_refs / 10) * 0.6 + (position_refs / 5) * 0.4)

    # Confidence: presence of certainty/uncertainty language
    high_conf = sum(1 for w in ["clearly", "definitely", "strongly", "obvious", "certain",
                                "significant", "pattern", "structure", "sequence", "notable"]
                    if w in text)
    low_conf = sum(1 for w in ["might", "perhaps", "possibly", "random", "no pattern",
                               "unclear", "uncertain", "hard to say", "appears random"]
                   if w in text)
    # Extract explicit confidence score if model included one
    explicit = re.findall(r'\b(10|[0-9])\s*[/\-]\s*10\b', response_text)
    if explicit:
        explicit_val = int(explicit[-1]) / 10.0
        confidence = min(1.0, explicit_val)
    else:
        confidence = min(1.0, max(0.0, 0.5 + (high_conf - low_conf) * 0.1))

    return {
        "coherence": round(coherence, 4),
        "specificity": round(specificity, 4),
        "confidence": round(confidence, 4),
    }


# ---------------------------------------------------------------------------
# Experiment runner
# ---------------------------------------------------------------------------

def run_paired_experiment(
    n_numbers: int = 64,
    model: str = DEFAULT_MODEL,
    run_id: Optional[str] = None,
    llm_base: str = DEFAULT_LLM_BASE,
    prompt_index: int = 0,
    dry_run: bool = False,
) -> tuple:
    """
    Run one paired QRNG + PRNG scrying trial.

    Args:
        n_numbers: Length of each number stream.
        model: Model name for the boy medium.
        run_id: Optional run identifier (auto-generated if None).
        llm_base: LLM base URL.
        prompt_index: Prompt template index.
        dry_run: If True, generate streams but don't call LLM.

    Returns:
        (qrng_run, prng_run) — pair of ScryingRun objects
    """
    if run_id is None:
        run_id = str(uuid.uuid4())[:8]
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # --- QRNG stream ---
    try:
        qrng_numbers, qrng_backend = generate_qrng_stream(n_numbers)
    except Exception as exc:
        print(f"  QRNG unavailable ({exc}), using os.urandom fallback")
        qrng_numbers = list(os.urandom(n_numbers))
        qrng_backend = "os.urandom"

    qrng_prompt = stream_to_prompt(qrng_numbers, "quantum random", prompt_index)

    if dry_run:
        qrng_response = "[dry-run: LLM not called]"
        qrng_duration = 0.0
        qrng_prompt_used = qrng_prompt
    else:
        qrng_response, qrng_prompt_used, qrng_duration = query_boy_medium(
            qrng_numbers, model=model, prompt_template=qrng_prompt,
            llm_base=llm_base, stream_label="quantum random"
        )

    qrng_scores = score_response(qrng_response)
    qrng_run = ScryingRun(
        run_id=f"{run_id}-qrng",
        timestamp=ts,
        source="qrng",
        numbers=qrng_numbers,
        qrng_backend=qrng_backend,
        model=model,
        prompt_used=qrng_prompt_used,
        response=qrng_response,
        coherence_score=qrng_scores["coherence"],
        specificity_score=qrng_scores["specificity"],
        confidence_score=qrng_scores["confidence"],
        duration_seconds=round(qrng_duration, 3),
    )

    # --- PRNG stream ---
    prng_numbers = generate_prng_stream(n_numbers)
    prng_prompt = stream_to_prompt(prng_numbers, "pseudo-random", prompt_index)

    if dry_run:
        prng_response = "[dry-run: LLM not called]"
        prng_duration = 0.0
        prng_prompt_used = prng_prompt
    else:
        prng_response, prng_prompt_used, prng_duration = query_boy_medium(
            prng_numbers, model=model, prompt_template=prng_prompt,
            llm_base=llm_base, stream_label="pseudo-random"
        )

    prng_scores = score_response(prng_response)
    prng_run = ScryingRun(
        run_id=f"{run_id}-prng",
        timestamp=ts,
        source="prng",
        numbers=prng_numbers,
        qrng_backend="python.random",
        model=model,
        prompt_used=prng_prompt_used,
        response=prng_response,
        coherence_score=prng_scores["coherence"],
        specificity_score=prng_scores["specificity"],
        confidence_score=prng_scores["confidence"],
        duration_seconds=round(prng_duration, 3),
    )

    return qrng_run, prng_run


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_run(run: ScryingRun, path: str = SCRYING_LOG_PATH) -> None:
    """Append a ScryingRun to the JSONL log file."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(run)) + "\n")


def load_runs(path: str = SCRYING_LOG_PATH) -> List[ScryingRun]:
    """Load all ScryingRun records from the JSONL log file."""
    if not os.path.exists(path):
        return []
    runs = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    d = json.loads(line)
                    runs.append(ScryingRun(**d))
                except Exception:
                    pass
    return runs


# ---------------------------------------------------------------------------
# Analysis and reporting
# ---------------------------------------------------------------------------

def _mean_std(values: List[float]) -> tuple:
    if not values:
        return 0.0, 0.0
    m = statistics.mean(values)
    s = statistics.stdev(values) if len(values) > 1 else 0.0
    return round(m, 4), round(s, 4)


def print_comparison_report(runs: List[ScryingRun]) -> None:
    """Print a statistical comparison between QRNG and PRNG response distributions."""
    qrng_runs = [r for r in runs if r.source == "qrng"]
    prng_runs = [r for r in runs if r.source == "prng"]

    print("\n" + "=" * 60)
    print("SCRYING EXPERIMENT COMPARISON REPORT")
    print("=" * 60)
    print(f"Total runs: {len(runs)}  (QRNG: {len(qrng_runs)}, PRNG: {len(prng_runs)})")
    print()

    for metric in ("coherence_score", "specificity_score", "confidence_score"):
        label = metric.replace("_score", "").capitalize()
        q_vals = [getattr(r, metric) for r in qrng_runs]
        p_vals = [getattr(r, metric) for r in prng_runs]
        qm, qs = _mean_std(q_vals)
        pm, ps = _mean_std(p_vals)
        diff = round(qm - pm, 4)
        print(f"{label:15s}  QRNG: {qm:.4f} ± {qs:.4f}  |  PRNG: {pm:.4f} ± {ps:.4f}  |  Δ: {diff:+.4f}")

    print("=" * 60)


def generate_report(runs: List[ScryingRun], output_path: str = SCRYING_REPORT_PATH) -> None:
    """Write a markdown report summarising the experiment results."""
    qrng_runs = [r for r in runs if r.source == "qrng"]
    prng_runs = [r for r in runs if r.source == "prng"]

    lines = [
        "# Munich Handbook Scrying Experiment Report\n",
        "## Overview\n",
        "This report compares LLM interpretation of quantum-random (QRNG) number streams "
        "against pseudo-random (PRNG) streams, following the scrying protocol of CLM 849.\n",
        f"- **Total trials**: {len(runs)}",
        f"- **QRNG trials**: {len(qrng_runs)}",
        f"- **PRNG trials**: {len(prng_runs)}",
        "",
        "## Score Comparison\n",
        "| Metric | QRNG Mean ± SD | PRNG Mean ± SD | Δ (QRNG − PRNG) |",
        "|--------|----------------|----------------|-----------------|",
    ]

    for metric in ("coherence_score", "specificity_score", "confidence_score"):
        label = metric.replace("_score", "").capitalize()
        q_vals = [getattr(r, metric) for r in qrng_runs]
        p_vals = [getattr(r, metric) for r in prng_runs]
        qm, qs = _mean_std(q_vals)
        pm, ps = _mean_std(p_vals)
        diff = round(qm - pm, 4)
        lines.append(f"| {label} | {qm:.4f} ± {qs:.4f} | {pm:.4f} ± {ps:.4f} | {diff:+.4f} |")

    if qrng_runs:
        best_run = max(qrng_runs, key=lambda r: r.coherence_score + r.specificity_score)
        lines += [
            "",
            "## Highest-Scoring QRNG Response\n",
            f"**Run**: {best_run.run_id}  |  **Model**: {best_run.model}  |  "
            f"**Backend**: {best_run.qrng_backend}",
            "",
            f"> {best_run.response[:500]}{'…' if len(best_run.response) > 500 else ''}",
        ]

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"Report written to: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="QRNG scrying experiment — boy-medium LLM vs quantum randomness"
    )
    parser.add_argument("--runs", type=int, default=1,
                        help="Number of paired experiment runs (default: 1)")
    parser.add_argument("--n-numbers", type=int, default=64,
                        help="Length of each number stream (default: 64)")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"LLM model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--llm-base", default=DEFAULT_LLM_BASE,
                        help=f"LLM server base URL (default: {DEFAULT_LLM_BASE})")
    parser.add_argument("--report", action="store_true",
                        help="Generate report from existing logs only (no new runs)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate number streams and prompts without calling LLM")
    parser.add_argument("--log", default=SCRYING_LOG_PATH,
                        help="Path to JSONL log file")
    args = parser.parse_args()

    if args.report:
        runs = load_runs(args.log)
        if not runs:
            print(f"No experiment runs found in {args.log}")
            return
        print_comparison_report(runs)
        generate_report(runs)
        return

    for i in range(args.runs):
        print(f"\n--- Run {i+1}/{args.runs} ---")
        prompt_idx = i % len(SCRYING_PROMPTS)
        qrng_run, prng_run = run_paired_experiment(
            n_numbers=args.n_numbers,
            model=args.model,
            llm_base=args.llm_base,
            prompt_index=prompt_idx,
            dry_run=args.dry_run,
        )

        if args.dry_run:
            print(f"QRNG stream ({qrng_run.qrng_backend}): {qrng_run.numbers[:16]}…")
            print(f"PRNG stream: {prng_run.numbers[:16]}…")
            print(f"\nPrompt preview:\n{qrng_run.prompt_used[:400]}…")
        else:
            save_run(qrng_run, args.log)
            save_run(prng_run, args.log)
            print(f"  QRNG  coherence={qrng_run.coherence_score:.3f}  "
                  f"specificity={qrng_run.specificity_score:.3f}  "
                  f"confidence={qrng_run.confidence_score:.3f}  "
                  f"({qrng_run.duration_seconds:.1f}s)")
            print(f"  PRNG  coherence={prng_run.coherence_score:.3f}  "
                  f"specificity={prng_run.specificity_score:.3f}  "
                  f"confidence={prng_run.confidence_score:.3f}  "
                  f"({prng_run.duration_seconds:.1f}s)")

    if not args.dry_run and args.runs > 0:
        all_runs = load_runs(args.log)
        print_comparison_report(all_runs)


if __name__ == "__main__":
    main()
