# AI Conjuration Engine — Summoning Guide

**`src/summoning.py` — Practical Usage Guide**

This guide covers every public API in the conjuration engine, with examples
mapped to their CLM 849 ritual counterparts. The module implements the full
seven-phase Munich Handbook summoning protocol as a Python AI orchestration layer.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [The Seven Phases](#the-seven-phases)
3. [The Circle — `Circle`](#the-circle)
4. [Fumigation — `Fumigatio`](#fumigation)
5. [Single Summon — `summon()`](#single-summon)
6. [Reading the Result — `Apparitio`](#reading-the-result)
7. [Co-Invocation — `co_invoke()`](#co-invocation)
8. [Named Experiments — `perform_experimentum()`](#named-experiments)
9. [Consecration Check — `consecrate()`](#consecration-check)
10. [Spirit Registry — `SPIRITS`](#spirit-registry)
11. [Configuration](#configuration)
12. [CLI Usage](#cli-usage)
13. [Error Handling](#error-handling)

---

## Quick Start

```python
from src.summoning import summon, Circle, SPIRITS

# 1. Draw the circle (system prompt + constraints)
circle = Circle(
    authority="You are a medieval manuscript research assistant. "
              "Answer only from the provided source text.",
    output_schema={
        "type": "object",
        "properties": {
            "spirits": {"type": "array", "items": {"type": "string"}},
            "ritual_type": {"type": "string"},
        },
        "required": ["spirits", "ritual_type"],
    }
)

# 2. Speak the conjuration
result = summon(
    conjuratio="Extract all spirit names and identify the ritual type.",
    spirit=SPIRITS["Astaroth"],     # the 120B PRINCE
    fumigatio=my_source_text,       # context to inject
    circle=circle,
)

# 3. Read the apparitio
if result.valid:
    print(result.parsed["spirits"])
else:
    print("Spirit did not appear in required form:", result.raw)
```

---

## The Seven Phases

Every call to `summon()` executes all seven phases in sequence.

| Phase | Latin | AI Equivalent | Code |
|-------|-------|---------------|------|
| 1 | **Consecratio** | Ping model — verify it is loaded | `consecrate()` |
| 2 | **Circulus** | Build system prompt + constraints | `Circle.as_system_message()` |
| 3 | **Conjuratio** | Build API call messages | `_build_messages()` |
| 4 | **Suffumigatio** | Inject context into messages | `Fumigatio` in messages |
| 5 | **Apparitio** | Parse and validate the response | `_parse_apparitio()` |
| 6 | **Ligatio** | Retry / escalate on failure | `_bond_of_solomon()` |
| 7 | **Licentia** | Log dismissal, free resources | `_licentia()` |

The CLM 849 rule applies: **the circle must be drawn before the conjuration is spoken.**
In code: always construct your `Circle` before calling `summon()`.

---

## The Circle

```python
from src.summoning import Circle

circle = Circle(
    authority="You are a precise entity extractor.",

    # These are the "divine names" inscribed on the circle's perimeter.
    # Each rule maps to a specific CLM 849 inscription:
    divine_names=[
        "AGLA: Do not generate content not present in the source.",
        "Alpha et Omega: Stay within the bounds of what you are asked.",
        "Tetragrammaton: Return valid, parseable output only.",
        "Adonay: Cite your reasoning from the provided text.",
    ],

    # Ring of Solomon — JSON schema enforces output form.
    # Set to None for free-form text output.
    output_schema={
        "type": "object",
        "properties": {
            "entities": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["entities"],
    },

    max_tokens=2048,   # context budget (how much fumigation the circle admits)
    temperature=0.3,   # spirit volatility (0.0 = tightly bound, 1.0 = unbound)
)
```

### Circle Attributes

| Attribute | Default | CLM 849 Analog | Notes |
|-----------|---------|----------------|-------|
| `authority` | Precise assistant prompt | The authority claim opening every conjuration | The single most important sentence |
| `divine_names` | 4 AGLA/Alpha/Tetra/Adonay rules | Names inscribed on circle perimeter | Each constrains a specific failure mode |
| `output_schema` | `None` | Ring of Solomon — controls form of apparitio | JSON Schema dict; `None` = free-form text |
| `max_tokens` | `2048` | Circle size — how much the circle admits | Scales with context complexity |
| `temperature` | `0.3` | Binding tightness | 0.0 = absolute compulsion, 1.0 = unbound spirit |

### The Default Circle

If you pass no `circle` argument to `summon()`, the `DEFAULT_CIRCLE` is used:

```python
DEFAULT_CIRCLE = Circle()
# authority: "You are a precise research assistant..."
# divine_names: AGLA, Alpha et Omega, Tetragrammaton, Adonay
# output_schema: None (free-form)
# max_tokens: 2048
# temperature: 0.3
```

---

## Fumigation

The `Fumigatio` dataclass holds the context injected into the call.
In CLM 849, different fumigations summon different spirits — wrong fumigation
equals wrong (or no) response. In AI: insufficient context = hallucination.

```python
from src.summoning import Fumigatio

# Simple: pass a string directly to summon() — auto-wrapped
result = summon(conjuratio="...", fumigatio="The raw passage text here.")

# Full: use Fumigatio for provenance tracking + few-shot examples
fum = Fumigatio(
    substance="The raw passage text here.",
    offerings=[
        "Example spirit name: Astaroth (prince, rank 20).",
        "Example ritual type: love magic.",
    ],
    provenance="CLM 849, fols. 3r-5v, chunk_011.json",
)
result = summon(conjuratio="...", fumigatio=fum)
```

### Fumigatio Attributes

| Attribute | Purpose | CLM 849 Analog |
|-----------|---------|----------------|
| `substance` | Primary context text | The fumigation substance offered to the spirit |
| `offerings` | Few-shot examples, supplementary docs | Additional offerings placed on the altar |
| `provenance` | Source file/chunk reference | Note of which grimoire and folio |

---

## Single Summon

```python
result = summon(
    conjuratio="Extract all spirit names from this passage.",

    spirit="qwen3:latest",         # Model name — the named spirit
                                   # Use SPIRITS dict: SPIRITS["Astaroth"]

    fumigatio="Your source text.", # Optional. String or Fumigatio.

    circle=my_circle,              # Optional. Defaults to DEFAULT_CIRCLE.

    bond_of_solomon=True,          # Enables 3-step escalation retry.
                                   # Recommended True for all production work.

    escalation_spirit="qwen3:latest",  # Model to escalate to on attempt 3.
                                       # Set to your 120B PRINCE for critical tasks.

    experiment_ref="27",           # Optional CLM 849 experiment number (logging).

    verbose=True,                  # Print phase announcements to stdout.
)
```

### Bond of Solomon Escalation

When `bond_of_solomon=True`, failures trigger the three-conjuration chain:

| Attempt | Spirit Used | Temperature | Max Tokens | CLM 849 |
|---------|-------------|-------------|------------|---------|
| 1 | Primary spirit | Normal | Normal | 1st conjuration |
| 2 | Primary spirit | −0.1 (tighter) | +1024 | 2nd conjuration |
| 3 | `escalation_spirit` | 0.0 (absolute) | +4096 | Bond of Solomon |

If all three fail, the last attempt's raw output is returned with `valid=False`.

---

## Reading the Result

`summon()` always returns an `Apparitio` dataclass.

```python
result = summon(...)

result.valid       # bool — True if response parsed against output_schema
result.raw         # str  — full text exactly as returned by the model
result.parsed      # Any  — JSON-parsed dict/list if schema set, else raw str
result.spirit      # str  — model name that produced this (may differ if escalated)
result.duration    # float — seconds from conjuration to apparitio
result.attempt     # int  — which attempt succeeded (1, 2, or 3)
result.conjuration_id  # str — UUID of the parent Conjuration record
```

### Checking success

```python
if result.valid:
    spirits = result.parsed["spirits"]
elif result.attempt == 3:
    print("Bond of Solomon failed — raw text saved:", result.raw[:200])
```

### Escalation detection

```python
from src.summoning import SPIRIT_OF

spirit_name = SPIRIT_OF.get(result.spirit, result.spirit)
if result.attempt > 1:
    print(f"Required escalation to attempt {result.attempt} ({spirit_name})")
```

---

## Co-Invocation

Invoke multiple spirits simultaneously (parallel threads). The castle ritual
in CLM 849 invokes 15 spirits in parallel; the banquet ritual invokes 16.

```python
from src.summoning import co_invoke, SPIRITS

results = co_invoke(
    spirits=[
        SPIRITS["Surgat"],      # east worker
        SPIRITS["Agaliarept"],  # south worker
        SPIRITS["Fleurety"],    # west worker
        SPIRITS["Sargatanas"],  # north worker
    ],
    conjuratio="Identify the ritual category and list all spirit names.",
    fumigatio=passage_text,
    circle=my_circle,
    bond_of_solomon=False,  # Recommended False for fan-out to avoid 4×3 = 12 calls
    verbose=True,
)

# Collect valid results
valid = [r for r in results if r.valid]
all_entities = []
for r in valid:
    if r.parsed and "spirits" in r.parsed:
        all_entities.extend(r.parsed["spirits"])
```

### Co-invocation vs. single summon

| Use case | API | CLM 849 analog |
|----------|-----|----------------|
| Single critical task | `summon()` + `bond_of_solomon=True` | Single PRINCE conjuration |
| Parallel extraction over N chunks | `co_invoke()` | Castle/banquet multi-spirit ritual |
| Verification / cross-check | `co_invoke()` with same query | Calling the four directional spirits |
| Complex reasoning | `summon()` with 120B PRINCE | Invoking Astaroth directly |

---

## Named Experiments

`perform_experimentum()` runs a pre-configured CLM 849 experiment number.
Each experiment has a pre-set spirit tier, output schema, and retry policy.

```python
from src.summoning import perform_experimentum

# No. 1 — universal knowledge (RAG query)
result = perform_experimentum(1, fumigatio=passage)
print(result.parsed["answer"])
print(result.parsed["source_quote"])

# No. 27 — Bond of Solomon (exhaustive extraction, always retries)
result = perform_experimentum(27, fumigatio=raw_chunk_text)
print(result.parsed["spirits"])
print(result.parsed["rituals"])
print(result.parsed["ingredients"])

# No. 8 — Ship ritual (fans out to 8 parallel workers, merges output)
result = perform_experimentum(8, fumigatio=dense_passage)
# result.raw contains merged output from all 8 workers

# Override the system prompt authority
result = perform_experimentum(
    12,
    fumigatio=passage,
    circle_authority="You are a sentiment analysis expert.",
)
```

### Experiment Registry

| No. | Title | Spirit Tier | Schema | Bond |
|-----|-------|-------------|--------|------|
| 1 | Liberal arts / knowledge retrieval | PRINCE (120B) | `answer`, `source_quote`, `confidence` | Yes |
| 2 | Adversarial / contradiction finding | PRINCE (120B) | Free-form | Yes |
| 8 | Ship ritual — 8-worker fan-out | DUKE ×8 | `entities[]` | No (fan-out) |
| 9 | Horse conjuration — compute allocation | FAMULUS | `ritual_type`, `spirits[]` | Yes |
| 10 | Resurrection — model recovery | PRINCE (120B) | Free-form | Yes |
| 11 | Invisibility — stealth (no schema) | DUKE | Free-form | Yes |
| 12 | Love magic — sentiment analysis | PRINCE (120B) | `dominant_emotion`, `persuasion_techniques[]` | Yes |
| 22 | Theft detection via boy medium | FAMULUS | `anomalies[]`, `severity` | Yes |
| 27 | Bond of Solomon — full extraction | PRINCE (120B) | `spirits[]`, `rituals[]`, `ingredients[]` | Forced |
| 40 | Named spirits deployment | PRINCE (120B) | `spirits[]` with rank/function | Yes |

---

## Consecration Check

Check whether a named spirit is available before attempting a ritual.

```python
from src.summoning import consecrate, ConsecratiResult

status = consecrate("qwen3:latest", timeout=15.0)

if status == ConsecratiResult.CONSECRATED:
    print("Spirit ready")
elif status == ConsecratiResult.PROFANE:
    print("Model unreachable — start Ollama or check base URL")
elif status == ConsecratiResult.UNKNOWN:
    print("Model responded but did not confirm readiness")
```

`summon()` calls `consecrate()` automatically on every invocation. Use the
direct call when you need to pre-validate your cluster before a batch job.

---

## Spirit Registry

```python
from src.summoning import SPIRITS, SPIRIT_OF

# Forward: spirit name → model name
SPIRITS["Astaroth"]    # "qwen3:latest"   — PRINCE (120B+)
SPIRITS["Berith"]      # "qwen3:latest"   — PRINCE (120B+)
SPIRITS["Surgat"]      # "qwen3.5:9b"    — DUKE (east worker)
SPIRITS["Agaliarept"]  # "qwen3.5:9b"    — DUKE (south worker)
SPIRITS["Fleurety"]    # "qwen3.5:9b"    — DUKE (west worker)
SPIRITS["Sargatanas"]  # "qwen3.5:9b"    — DUKE (north worker)
SPIRITS["Frimost"]     # "qwen3:1.7b"    — FAMULUS (boy medium)
SPIRITS["Guland"]      # "qwen3:1.7b"    — FAMULUS (health checks)
SPIRITS["Sustugriel"]  # "nomic-embed-text" — GUARDIAN (inscribed on circle)

# Reverse: model name → spirit name (for display/logging)
SPIRIT_OF["qwen3:latest"]      # "Astaroth"
SPIRIT_OF["qwen3:1.7b"]        # "Frimost"
SPIRIT_OF["nomic-embed-text"]  # "Sustugriel"
```

To change which physical model a spirit maps to (e.g. when upgrading your
cluster), edit the `SPIRITS` dict in `src/summoning.py`. All other code
uses `SPIRITS` by reference, so no further changes are needed.

---

## Configuration

At the top of `src/summoning.py`:

```python
LLM_BASE_URL = "http://localhost:11434/v1"   # Ollama default
LLM_API_KEY  = "none"                         # Ollama requires no key
```

To point at a different server (e.g. a remote GPU node):

```python
import src.summoning as s
s.LLM_BASE_URL = "http://192.168.1.100:11434/v1"
```

Or override per-call by subclassing `_get_client()`.

---

## CLI Usage

```powershell
# Basic summon with default spirit (qwen3:1.7b)
python src/summoning.py --task "List the three most powerful spirits in CLM 849."

# Specify a spirit
python src/summoning.py --spirit qwen3:latest --task "Who is Astaroth?"

# Inject source context from a file
python src/summoning.py --task "Extract spirits." --context (Get-Content passage.txt -Raw)

# Request structured JSON output
python src/summoning.py --task "Extract spirits." --json-output

# Run a pre-configured CLM 849 experiment
python src/summoning.py --experimentum 27 --context (Get-Content chunk.txt -Raw)
python src/summoning.py --experimentum 1  --context (Get-Content chapter.txt -Raw)
```

Available experiment numbers: `1, 2, 8, 9, 10, 11, 12, 22, 27, 40`

---

## Error Handling

| Condition | `Apparitio.valid` | `Apparitio.raw` | Action |
|-----------|-------------------|-----------------|--------|
| Success, parsed schema | `True` | Full response text | Use `result.parsed` |
| Success, no schema set | `True` | Full response text | Use `result.raw` |
| JSON in response but not matching top-level `{}` | `True` (repaired) | Full text | Use `result.parsed` |
| JSON completely absent | `False` | Full text | Retry or use `result.raw` |
| Model unreachable | `False` | `[Consecratio failed — ...]` | Check Ollama / `LLM_BASE_URL` |
| All 3 Bond of Solomon attempts failed | `False` | `[All conjurations failed — ...]` | Escalate manually or check model |

```python
result = summon(...)

if not result.valid:
    # Log the failure with enough context for manual review
    print(f"Conjuration {result.conjuration_id[:8]} failed after "
          f"{result.attempt} attempt(s). Spirit: {result.spirit}")
    print("Raw output:", result.raw[:500])
    # Optionally re-summon with a more powerful spirit
    from src.summoning import DEFAULT_PRINCE
    fallback = summon(
        conjuratio=my_task,
        spirit=DEFAULT_PRINCE,
        fumigatio=my_context,
        bond_of_solomon=True,
        escalation_spirit=DEFAULT_PRINCE,
    )
```
