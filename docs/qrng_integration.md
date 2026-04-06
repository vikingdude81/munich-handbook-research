# QRNG Integration — Munich Handbook Research

## Overview

This document explains the rationale and implementation of Quantum Random Number Generation (QRNG) integration into the Munich Handbook research project. QRNG provides true quantum entropy for seeding inference runs, scheduling decisions, and experimental context injection.

---

## Why QRNG? The Philosophical Basis

### The Munich Handbook's Position on "True" Timing

The Munich Handbook (CLM 849, c. 1440–1460) and related medieval texts do not treat timing as arbitrary. Practitioners used:

- **Planetary hours** (Chaldean sequence) — timing derived from observed celestial motion, not personal preference
- **Lunar phases** — operations assigned to waxing/waning moon periods
- **Astronomical tables** — Alfonsine tables and similar resources for computing exact planetary positions

The underlying assumption is that timing drawn from external, objective, cosmic sources is categorically different from timing invented by the practitioner. The planets are not under human control; their cycles constitute a source of "true" external structure.

**QRNG maps directly to this concept.** Quantum random numbers are generated from physical processes (photon arrival times, vacuum fluctuations, radioactive decay) that are genuinely non-deterministic. They are not fabricated by the computational system — they arrive from outside the deterministic machine. This is the modern equivalent of reading an astronomical table.

Pseudo-random numbers (PRNG), by contrast, are *deterministically generated from a seed*. Once the seed is known, every "random" number is fixed. The medieval analog would be a practitioner who *invented* their own timing system without reference to astronomical observation — technically structured, but not externally grounded.

---

## The Princeton GCP Connection

The Princeton [Global Consciousness Project](https://noosphere.princeton.edu/) (GCP) operated a network of hardware Random Event Generators (REGs) to test whether global human attention events (e.g., major disasters, cultural events) correlate with deviations from expected random behaviour. The methodology involves:

1. Continuous sampling of quantum/physical RNG devices
2. Statistical comparison of observed distributions against theoretical random baseline
3. Identification of deviations correlated with external events

**Key methodological distinction from this project**: The GCP makes ontological claims about consciousness affecting physical randomness. This project makes no such claim. We use QRNG strictly as:

- A reproducible, externally-sourced entropy pool
- A baseline comparison against PRNG for LLM interpretation studies
- A provenance-traceable seed source for audit trail purposes

The scrying experiment (`scripts/scrying_experiment.py`) is designed to test a specific, limited hypothesis: *Does a lightweight LLM produce systematically different interpretation outputs when given quantum-random vs pseudo-random number sequences?* This is a study of LLM interpretation artifacts, not quantum consciousness.

---

## Module Reference

### `qrng_source.py`

Core QRNG utility. Provides quantum entropy via three backends in priority order.

```python
from qrng_source import get_quantum_seed, get_quantum_float, get_quantum_bytes, QRNGSource

# Simple convenience functions
seed = get_quantum_seed()        # 32-bit integer seed from quantum entropy
val  = get_quantum_float()       # float in [0.0, 1.0)
raw  = get_quantum_bytes(n=8)    # n raw bytes

# Full class interface
src = QRNGSource(timeout=5)
seed = src.get_seed(n_bytes=4)          # get seed + log provenance
temp = src.get_temperature(base=0.1, variance=0.3)  # LLM temperature
print(src.source_name)                  # which backend was used
```

#### Backends

| Priority | Backend | URL | Notes |
|----------|---------|-----|-------|
| 1 | ANU QRNG | `https://qrng.anu.edu.au/API/jsonI.php` | Free, no API key needed |
| 2 | NIST Beacon | `https://beacon.nist.gov/beacon/2.0/pulse/last` | 60-second update interval |
| 3 | `os.urandom()` | (local) | CSPRNG fallback, not quantum |

#### Rate Limits

- **ANU QRNG**: No published rate limit for public API; use reasonable intervals (< 1 request/second for batch operations)
- **NIST Beacon**: Updated once per minute; fetching more frequently returns the same pulse value; no rate limit enforced

### `planetary_scheduler.py`

Maps current time to a planetary assignment, which resolves to a specific GPU node and model.

```python
from planetary_scheduler import PlanetaryScheduler, get_current_planetary_hour, get_model_for_now

scheduler = PlanetaryScheduler()

# Current assignment
assignment = scheduler.get_assignment()
print(assignment.planet)     # e.g. "Mars"
print(assignment.model)      # e.g. "qwen3.5:9b"
print(assignment.node)       # e.g. "4070-worker"

# Next optimal time for a work type
next_time = scheduler.get_best_time_for_work("knowledge_retrieval")

# Print full week grid
scheduler.print_week_schedule()
```

### `scripts/scrying_experiment.py`

QRNG scrying experiment: quantum stream → lightweight LLM → structured interpretation.

```bash
# Single paired run (QRNG vs PRNG)
python scripts/scrying_experiment.py

# Multiple runs with custom settings
python scripts/scrying_experiment.py --runs 10 --n-numbers 64 --model qwen3:1.7b

# Dry run (no LLM call; inspect prompts only)
python scripts/scrying_experiment.py --dry-run

# Generate report from existing logs
python scripts/scrying_experiment.py --report
```

---

## QRNG Audit Trail

Every call to `QRNGSource.get_seed()` (and via `get_quantum_seed()`) appends a record to `logs/qrng_log.jsonl`:

```json
{
  "timestamp": "2026-04-06T17:32:00Z",
  "seed": 2847361092,
  "source": "anu_qrng",
  "n_bytes": 4
}
```

This enables:
- **Reproducibility auditing**: Given the log, you can identify which external entropy source was used for each experiment run
- **Fallback detection**: Log entries with `source: "os.urandom"` indicate that quantum sources were unavailable at that time
- **Timeline reconstruction**: Timestamps allow correlating inference runs with external events

To replay an experiment with a logged seed:
```python
import random
seed = 2847361092  # from qrng_log.jsonl
rng = random.Random(seed)
# ... use rng to reproduce the same stochastic decisions
```

---

## Research Questions

The scrying experiment is designed to investigate the following:

1. **Do coherence scores differ between QRNG and PRNG streams?**  
   Null hypothesis: LLMs produce statistically identical interpretations of QRNG and PRNG sequences.

2. **Do specificity scores differ?**  
   Does the LLM cite more specific values (actual numbers from the sequence) when interpreting QRNG vs PRNG?

3. **Is there prompt-template sensitivity?**  
   The 5 prompt templates (pattern analysis, symbolic interpretation, sequence detection, binary grouping, frequency analysis) may interact differently with QRNG vs PRNG.

4. **Does the model size matter?**  
   Compare `qwen3:1.7b` (the "boy medium") against larger models. A larger model may show less variance; a smaller model may be more sensitive to input structure.

5. **Does QRNG-seeded temperature affect extraction quality?**  
   Use `get_quantum_temperature()` to modulate LLM temperature and measure effect on entity extraction coherence.

---

## Interpreting Divergence in the AI Mapping

The cross-source divergence analysis (`scripts/cross_source_divergence.py`) produces composite divergence scores for each entity. In the context of the AI mapping:

| Divergence Level | Manuscript Interpretation | AI Interpretation |
|-----------------|--------------------------|-------------------|
| **High** (> 0.6) | Sources fundamentally disagree about this entity's nature/role | Different models produce wildly different outputs for tasks involving this entity |
| **Medium** (0.2–0.6) | Sources partially agree; some attributes conflict | Models produce partially overlapping outputs; requires reconciliation |
| **Low** (< 0.2) | Sources are highly consistent in their description | Models agree; this entity/task type is well-specified |

**Contested entities** (composite score > 0.4) are the most interesting for AI research: they represent the "hard cases" where the source material itself is ambiguous, and therefore no single model response can be definitively correct.
