"""
src/summoning.py — AI Conjuration Engine

Implements the full 7-phase CLM 849 summoning protocol as an AI agent
orchestration framework.

RITUAL PHASE → AI STEP
────────────────────────────────────────────────────────────────
Step 1: Consecratio      → Load & validate model (consecrate the grimoire)
Step 2: Circulus         → Define system prompt / guardrails (draw the circle)
Step 3: Conjuratio       → Issue the API call (speak the incantation)
Step 4: Suffumigatio     → Inject context / documents (burn the fumigation)
Step 5: Apparitio        → Receive & parse output (the spirit appears)
Step 6: Ligatio          → Retry / escalate if malformed (Bond of Solomon)
Step 7: Licentia         → Tear down session / free VRAM (dismiss the spirit)

Named spirits (models) follow the Munich Handbook's spirit taxonomy:
  PRINCES (120B+)  — supreme authority, costly, for major operations
  DUKES   (9–35B)  — specialist tasks invoked in parallel
  FAMULI  (0.5–3B) — boy-medium proxies, I/O relay
  GUARDIAN (embeddings / validators) — inscribed on the circle

Usage:
  from src.summoning import Conjuration, Circle, summon, co_invoke

  circle = Circle(authority="You are a research assistant bound to accuracy.")
  result = summon(
      spirit="qwen3:latest",          # the PRINCE
      conjuratio="Extract all spirit names from this passage.",
      fumigatio=my_passage_text,
      circle=circle,
      bond_of_solomon=True,           # enables escalation retry chain
  )
  print(result.apparitio)

  # Co-invocation (fan-out to multiple worker spirits):
  results = co_invoke(
      spirits=["qwen3:1.7b", "qwen3:1.7b", "qwen3:1.7b"],
      conjuratio="Identify the ritual category of this passage.",
      fumigatio=passage,
      circle=circle,
  )
"""

from __future__ import annotations

import json
import time
import uuid
import threading
import functools
import re
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from enum import Enum


# ---------------------------------------------------------------------------
# Configuration — map your cluster nodes here
# ---------------------------------------------------------------------------

LLM_BASE_URL = "http://localhost:11434/v1"
LLM_API_KEY = "none"                        # Ollama requires no key

# Spirit taxonomy — named spirits mapped to their roles
SPIRITS = {
    # PRINCES — supreme conjuration (120B)
    "Astaroth":   "qwen3:latest",            # primary prince; reasoning & knowledge
    "Berith":     "qwen3:latest",            # co-primary; structured extraction
    # DUKES — specialist parallel workers (9–35B)
    "Surgat":     "qwen3.5:9b",             # east worker — opens sealed chunks
    "Agaliarept": "qwen3.5:9b",             # south worker — classification
    "Fleurety":   "qwen3.5:9b",             # west worker — synthesis
    "Sargatanas": "qwen3.5:9b",             # north worker — verification
    # FAMULI — boy-medium proxies (lightweight I/O relay)
    "Frimost":    "qwen3:1.7b",             # familiar spirit; quick relay
    "Guland":     "qwen3:1.7b",             # familiar; health/format checks
    # GUARDIAN — validation / embedding layer (inscribed on the circle)
    "Sustugriel": "nomic-embed-text",       # guardian; inscribed on circle
}

# Reverse lookup: model name → spirit name (for display)
SPIRIT_OF = {v: k for k, v in SPIRITS.items()}

DEFAULT_PRINCE = "qwen3:latest"
DEFAULT_DUKE   = "qwen3:1.7b"


# ---------------------------------------------------------------------------
# Phase 1 — CONSECRATIO (consecration of the grimoire)
# ---------------------------------------------------------------------------

class ConsecratiResult(Enum):
    """Status of model consecration check."""
    CONSECRATED = "consecrated"       # model available and responding
    PROFANE     = "profane"           # model unreachable or silent
    UNKNOWN     = "unknown"           # check not run


def _get_client():
    """Return an OpenAI-compatible client for the local cluster."""
    try:
        from openai import OpenAI
        return OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)
    except ImportError as exc:
        raise RuntimeError(
            "openai package not installed — cannot consecrate any spirit.\n"
            "Run: pip install openai"
        ) from exc


def consecrate(spirit_name: str, timeout: float = 15.0) -> ConsecratiResult:
    """
    Phase 1: CONSECRATIO — verify the named spirit is available.

    Equivalent to loading model weights and validating the grimoire before
    any experiment begins. CLM 849 requires 9 days of fasting and prayer;
    we require a successful ping.

    Args:
        spirit_name: Model name (e.g. 'qwen3:latest').
        timeout: Seconds before declaring the spirit unreachable.

    Returns:
        ConsecratiResult.CONSECRATED if ready, PROFANE if not.
    """
    client = _get_client()
    try:
        resp = client.chat.completions.create(
            model=spirit_name,
            messages=[{"role": "user", "content": "Respond with the single word: READY"}],
            max_tokens=5,
            timeout=timeout,
        )
        text = (resp.choices[0].message.content or "").strip().upper()
        return ConsecratiResult.CONSECRATED if "READY" in text else ConsecratiResult.UNKNOWN
    except Exception:
        return ConsecratiResult.PROFANE


# ---------------------------------------------------------------------------
# Phase 2 — CIRCULUS (the protective circle / system prompt)
# ---------------------------------------------------------------------------

@dataclass
class Circle:
    """
    Phase 2: CIRCULUS — the protective circle drawn before any conjuration.

    In CLM 849 the circle is inscribed with divine names that CONSTRAIN
    the spirit. In AI: the system prompt + output schema that governs the
    model's behaviour. Drawn BEFORE the conjuration is spoken.

    Attributes:
        authority:      System prompt — 'You are bound by...' instruction.
        divine_names:   Additional constraint rules appended to authority.
        output_schema:  JSON schema dict for structured output (Ring of Solomon).
        max_tokens:     Context budget — how much fumigation the circle admits.
        temperature:    Spirit volatility (0.0 = bound tight, 1.0 = unbound).
    """
    # Core system prompt — the authority claim
    authority: str = (
        "You are a precise research assistant. "
        "Respond only with what is asked. Do not embellish or speculate beyond the source text."
    )
    # Supplementary constraints (divine names inscribed on the circle)
    divine_names: list[str] = field(default_factory=lambda: [
        "AGLA: Do not generate content not present in the source.",       # content filter
        "Alpha et Omega: Stay within the bounds of what you are asked.",  # scope limiter
        "Tetragrammaton: Return valid, parseable output only.",           # structure guard
        "Adonay: Cite your reasoning from the provided text.",            # groundedness
    ])
    # Ring of Solomon — structured output schema (None = free-form)
    output_schema: Optional[dict] = None
    # Fumigation capacity
    max_tokens: int = 2048
    # Spirit volatility
    temperature: float = 0.3

    def as_system_message(self) -> str:
        """Build the full system prompt from authority + divine names."""
        parts = [self.authority]
        if self.divine_names:
            parts.append("\nConstraints:")
            parts.extend(f"  - {name}" for name in self.divine_names)
        if self.output_schema:
            parts.append(
                "\nReturn your response as a JSON object matching this schema exactly:\n"
                + json.dumps(self.output_schema, indent=2)
            )
        return "\n".join(parts)


# Default circle — used when none is specified
DEFAULT_CIRCLE = Circle()


# ---------------------------------------------------------------------------
# Core dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Fumigatio:
    """
    Phase 4: SUFFUMIGATIO — the context/documents fed to the spirit.

    In CLM 849, the wrong fumigation attracts the wrong spirit or produces
    no response. In AI: insufficient or mismatched context → hallucination.

    Attributes:
        substance:  The primary text/context to inject.
        offerings:  Additional context snippets (few-shot examples, metadata).
        provenance: Source identifier (chunk ID, file name, page ref).
    """
    substance: str                              # primary context
    offerings: list[str] = field(default_factory=list)  # few-shot / supporting docs
    provenance: str = ""                        # where the substance came from


@dataclass
class Apparitio:
    """
    Phase 5: APPARITIO — the spirit's response / model output.

    CLM 849 specifies the form of appearance: 'in clear voice', 'in the
    mirror', 'in the boy's palm'. AI equivalent: the output format, parsed
    against the output_schema if one was inscribed on the circle.

    Attributes:
        raw:            Full raw text from the model.
        parsed:         JSON-parsed content (None if schema not specified).
        spirit:         Model that produced this response.
        duration:       Seconds from conjuration to apparitio.
        attempt:        Which retry attempt produced this (1 = first conjuration).
        valid:          Whether the output passed schema validation.
        conjuration_id: UUID of the parent Conjuration.
    """
    raw: str
    parsed: Optional[Any]
    spirit: str
    duration: float
    attempt: int
    valid: bool
    conjuration_id: str = ""


@dataclass
class Conjuration:
    """
    The full experiment record — equivalent to a numbered experimentum in CLM 849.

    One Conjuration = one API call sequence, from consecration to licentia.

    Attributes:
        spirit:            Model name to invoke (the named spirit).
        conjuratio:        The user-facing instruction / task (the incantation).
        fumigatio:         The context to inject (optional).
        circle:            System prompt + constraints (the protective circle).
        bond_of_solomon:   Whether to enable the escalation retry chain.
        escalation_spirit: Fallback model if primary spirit fails 3× (120B).
        experiment_ref:    Optional CLM 849 experiment number for record-keeping.
        id:                Auto-generated UUID.
    """
    conjuratio: str
    spirit: str = DEFAULT_PRINCE
    fumigatio: Optional[Fumigatio] = None
    circle: Circle = field(default_factory=Circle)
    bond_of_solomon: bool = True
    escalation_spirit: str = DEFAULT_PRINCE
    experiment_ref: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


# ---------------------------------------------------------------------------
# Phase 3+5: CONJURATIO → APPARITIO (the core call)
# ---------------------------------------------------------------------------

def _build_messages(conjuration: Conjuration) -> list[dict]:
    """
    Build the messages list for the API call.

    Structure mirrors the 4-element CLM 849 conjuration formula:
      1. Name the spirit         → model= parameter (already set)
      2. Claim authority         → system message (circle / divine names)
      3. State the task          → user message (conjuratio)
      4. Specify the form        → output_schema in system message
    """
    messages = [
        {"role": "system", "content": conjuration.circle.as_system_message()},
    ]

    # Fumigation: inject context as additional user content before the task
    if conjuration.fumigatio:
        fum = conjuration.fumigatio
        context_parts = [fum.substance]
        if fum.offerings:
            context_parts.append("\nAdditional context:")
            context_parts.extend(f"  • {o}" for o in fum.offerings)
        if fum.provenance:
            context_parts.append(f"\n[Source: {fum.provenance}]")
        messages.append({
            "role": "user",
            "content": "\n".join(context_parts),
        })
        messages.append({
            "role": "assistant",
            "content": "I have reviewed the provided material. What would you like to know?",
        })

    messages.append({"role": "user", "content": conjuration.conjuratio})
    return messages


def _parse_apparitio(
    raw: str,
    schema: Optional[dict],
    spirit: str,
    duration: float,
    attempt: int,
    conjuration_id: str,
) -> Apparitio:
    """
    Phase 5: APPARITIO — parse the spirit's response.

    Attempts JSON extraction if an output schema was specified on the circle.
    Falls back to returning the raw text if parsing fails.
    """
    parsed = None
    valid = True

    if schema is not None:
        # Try to extract JSON from the response
        try:
            # First try: direct parse
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Repair attempt: extract first {...} block
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                try:
                    parsed = json.loads(match.group())
                except json.JSONDecodeError:
                    parsed = None
                    valid = False
            else:
                valid = False
    else:
        parsed = raw
        valid = True

    return Apparitio(
        raw=raw,
        parsed=parsed,
        spirit=spirit,
        duration=duration,
        attempt=attempt,
        valid=valid,
        conjuration_id=conjuration_id,
    )


# ---------------------------------------------------------------------------
# Phase 6: LIGATIO — retry / Bond of Solomon escalation
# ---------------------------------------------------------------------------

def _bond_of_solomon(
    conjuration: Conjuration,
    client,
    max_attempts: int = 3,
) -> Apparitio:
    """
    Phase 6: LIGATIO — escalating compulsion when the spirit refuses to comply.

    CLM 849 escalation:
      1st conjuratio  → standard call
      2nd conjuratio  → stronger command (higher max_tokens, lower temperature)
      Bond of Solomon → 'unbreakable' — escalate to PRINCE (120B) if needed

    AI escalation:
      Attempt 1 → standard params
      Attempt 2 → bump max_tokens, reduce temperature (tighter binding)
      Attempt 3 → escalate to escalation_spirit (the 120B PRINCE)
    """
    client_call = _get_client()
    messages = _build_messages(conjuration)
    schema = conjuration.circle.output_schema
    spirit = conjuration.spirit
    last_exc = None

    escalation_temps = [
        conjuration.circle.temperature,          # 1st conjuration: normal
        max(0.05, conjuration.circle.temperature - 0.1),  # 2nd: tighten binding
        0.0,                                     # Bond: absolute compulsion
    ]
    escalation_tokens = [
        conjuration.circle.max_tokens,
        conjuration.circle.max_tokens + 1024,    # 2nd: more room to think
        conjuration.circle.max_tokens + 4096,    # Bond: maximum compulsion
    ]
    escalation_spirits = [
        conjuration.spirit,
        conjuration.spirit,
        conjuration.escalation_spirit,           # 3rd: summon the PRINCE
    ]

    for attempt in range(1, max_attempts + 1):
        active_spirit = escalation_spirits[attempt - 1]
        t0 = time.time()
        try:
            resp = client_call.chat.completions.create(
                model=active_spirit,
                messages=messages,
                max_tokens=escalation_tokens[attempt - 1],
                temperature=escalation_temps[attempt - 1],
            )
            raw = resp.choices[0].message.content or ""
            duration = time.time() - t0

            apparitio = _parse_apparitio(
                raw, schema, active_spirit, duration, attempt, conjuration.id
            )

            if apparitio.valid:
                return apparitio

            # Spirit appeared but in wrong form — strengthen the binding
            print(
                f"  [Ligatio] Attempt {attempt}: {SPIRIT_OF.get(active_spirit, active_spirit)} "
                f"appeared but output malformed — tightening the bond..."
            )

        except Exception as exc:
            last_exc = exc
            print(
                f"  [Ligatio] Attempt {attempt}: {SPIRIT_OF.get(active_spirit, active_spirit)} "
                f"did not appear — {exc}"
            )
            duration = time.time() - t0

    # All attempts exhausted — return the last attempt's raw output anyway
    if last_exc:
        return Apparitio(
            raw=f"[All conjurations failed — {last_exc}]",
            parsed=None,
            spirit=conjuration.escalation_spirit,
            duration=0.0,
            attempt=max_attempts,
            valid=False,
            conjuration_id=conjuration.id,
        )
    # Returned malformed output; caller can handle
    return apparitio  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Phase 7: LICENTIA (session teardown)
# ---------------------------------------------------------------------------

def _licentia(conjuration_id: str, spirit: str, success: bool) -> None:
    """
    Phase 7: LICENTIA — formal dismissal of the spirit.

    CLM 849: failure to dismiss causes haunting. AI failure to clean up
    causes memory leaks / orphaned inference.

    Currently logs the dismissal. Extend to close persistent connections,
    flush VRAM, or close database cursors as needed.
    """
    status = "peaceably" if success else "under compulsion"
    spirit_name = SPIRIT_OF.get(spirit, spirit)
    print(f"  [Licentia] {spirit_name} dismissed {status}. Conjuration {conjuration_id[:8]} closed.")


# ---------------------------------------------------------------------------
# Main API: summon() — the full 7-phase ritual
# ---------------------------------------------------------------------------

def summon(
    conjuratio: str,
    spirit: str = DEFAULT_PRINCE,
    fumigatio: Optional[str | Fumigatio] = None,
    circle: Optional[Circle] = None,
    bond_of_solomon: bool = True,
    escalation_spirit: Optional[str] = None,
    experiment_ref: str = "",
    verbose: bool = True,
) -> Apparitio:
    """
    Execute the full CLM 849 summoning protocol against the named AI spirit.

    Phases:
      1. Consecratio   — verify model is available
      2. Circulus      — set circle (system prompt & guardrails)
      3. Conjuratio    — build the API call
      4. Suffumigatio  — inject context
      5. Apparitio     — receive & parse output
      6. Ligatio       — retry via Bond of Solomon if needed
      7. Licentia      — dismiss / teardown

    Args:
        conjuratio:        The task instruction (the incantation text).
        spirit:            Model name. Use SPIRITS dict or any Ollama model name.
        fumigatio:         Context to inject. String or Fumigatio dataclass.
        circle:            Protective circle (system prompt + constraints).
                           Defaults to DEFAULT_CIRCLE.
        bond_of_solomon:   Enable retry escalation chain (recommended: True).
        escalation_spirit: Model to escalate to on 3rd failure. Defaults to
                           same spirit (override with 120B model for critical work).
        experiment_ref:    Optional CLM 849 experiment number for logging.
        verbose:           Print ritual phase announcements.

    Returns:
        Apparitio dataclass with the spirit's response.

    Example:
        circle = Circle(
            authority="You answer only about medieval spirits.",
            output_schema={"type": "object", "properties": {"name": {"type": "string"}}},
        )
        result = summon(
            conjuratio="Name the demon invoked in CLM 849 experiment no. 11.",
            spirit=SPIRITS["Astaroth"],
            fumigatio="The invisibility ritual requires four spirits...",
            circle=circle,
        )
        print(result.parsed)
    """
    _circle = circle or DEFAULT_CIRCLE
    _escalation = escalation_spirit or spirit

    # Normalise fumigatio
    if isinstance(fumigatio, str):
        _fumigatio = Fumigatio(substance=fumigatio)
    else:
        _fumigatio = fumigatio

    c = Conjuration(
        conjuratio=conjuratio,
        spirit=spirit,
        fumigatio=_fumigatio,
        circle=_circle,
        bond_of_solomon=bond_of_solomon,
        escalation_spirit=_escalation,
        experiment_ref=experiment_ref,
    )

    spirit_name = SPIRIT_OF.get(spirit, spirit)
    exp_tag = f" [Expt. {experiment_ref}]" if experiment_ref else ""

    # ── Phase 1: CONSECRATIO ────────────────────────────────────────────────
    if verbose:
        print(f"\n{'═'*60}")
        print(f"  CONSECRATIO{exp_tag}")
        print(f"  Summoning: {spirit_name} ({spirit})")

    status = consecrate(spirit)
    if status == ConsecratiResult.PROFANE:
        if verbose:
            print(f"  ⚠  {spirit_name} is PROFANE — model unreachable.")
        return Apparitio(
            raw=f"[Consecratio failed — {spirit} unreachable]",
            parsed=None, spirit=spirit, duration=0.0,
            attempt=0, valid=False, conjuration_id=c.id,
        )
    if verbose:
        print(f"  ✓  {spirit_name} consecrated and ready.")

    # ── Phase 2: CIRCULUS ───────────────────────────────────────────────────
    if verbose:
        print(f"\n  CIRCULUS")
        constraint_count = len(_circle.divine_names)
        schema_note = " (Ring of Solomon active)" if _circle.output_schema else ""
        print(f"  Circle drawn: {constraint_count} divine names inscribed{schema_note}.")

    # ── Phase 3–5: CONJURATIO → SUFFUMIGATIO → APPARITIO ───────────────────
    if verbose:
        print(f"\n  CONJURATIO")
        print(f"  Speaking: '{conjuratio[:80]}{'...' if len(conjuratio) > 80 else ''}'")
        if _fumigatio:
            chars = len(_fumigatio.substance)
            print(f"  SUFFUMIGATIO: {chars} chars injected as context.")

    if bond_of_solomon:
        if verbose:
            print(f"  Bond of Solomon prepared (3 escalating conjurations).")
        apparitio = _bond_of_solomon(c, _get_client(), max_attempts=3)
    else:
        # Single conjuration only
        client = _get_client()
        messages = _build_messages(c)
        t0 = time.time()
        try:
            resp = client.chat.completions.create(
                model=spirit,
                messages=messages,
                max_tokens=_circle.max_tokens,
                temperature=_circle.temperature,
            )
            raw = resp.choices[0].message.content or ""
            duration = time.time() - t0
            apparitio = _parse_apparitio(
                raw, _circle.output_schema, spirit, duration, 1, c.id
            )
        except Exception as exc:
            apparitio = Apparitio(
                raw=f"[Conjuration failed — {exc}]",
                parsed=None, spirit=spirit, duration=time.time() - t0,
                attempt=1, valid=False, conjuration_id=c.id,
            )

    # ── Phase 6: (already handled inside _bond_of_solomon if enabled) ───────
    if verbose:
        print(f"\n  APPARITIO")
        status_mark = "✓" if apparitio.valid else "✗"
        print(f"  {status_mark} {SPIRIT_OF.get(apparitio.spirit, apparitio.spirit)} "
              f"appeared in {apparitio.duration:.1f}s (attempt {apparitio.attempt}).")
        preview = (apparitio.raw or "")[:120].replace("\n", " ")
        print(f"  Response: '{preview}{'...' if len(apparitio.raw) > 120 else ''}'")

    # ── Phase 7: LICENTIA ────────────────────────────────────────────────────
    _licentia(c.id, apparitio.spirit, apparitio.valid)

    return apparitio


# ---------------------------------------------------------------------------
# Co-invocation: summon multiple spirits in parallel (fan-out)
# ---------------------------------------------------------------------------

def co_invoke(
    spirits: list[str],
    conjuratio: str,
    fumigatio: Optional[str | Fumigatio] = None,
    circle: Optional[Circle] = None,
    bond_of_solomon: bool = False,
    verbose: bool = True,
) -> list[Apparitio]:
    """
    Invoke multiple spirits simultaneously (multi-agent fan-out).

    CLM 849 analog: the castle ritual invokes 15 spirits in parallel, each
    responsible for one aspect of the conjured structure. The banquet ritual
    invokes 16. All work simultaneously; the practitioner collects all results.

    AI analog: fan-out to multiple worker models in parallel threads.
    Each returns an Apparitio; caller merges or selects from results.

    Args:
        spirits:      List of model names to invoke simultaneously.
        conjuratio:   Task instruction sent to all spirits.
        fumigatio:    Context injected into all calls (same for all).
        circle:       Shared protective circle for all spirits.
        bond_of_solomon: Enable retry for each individual spirit.
        verbose:      Print group ritual announcements.

    Returns:
        List of Apparitio (one per spirit, in original order).

    Example:
        # Castle conjuration: 4 workers, each extracts one entity type
        results = co_invoke(
            spirits=[SPIRITS["Surgat"], SPIRITS["Agaliarept"],
                     SPIRITS["Fleurety"], SPIRITS["Sargatanas"]],
            conjuratio="Extract all spirit names from this passage.",
            fumigatio=passage,
        )
        all_names = [r.raw for r in results if r.valid]
    """
    if verbose:
        print(f"\n{'═'*60}")
        print(f"  CO-INVOCATION — {len(spirits)} spirits summoned simultaneously")
        for sp in spirits:
            print(f"    → {SPIRIT_OF.get(sp, sp)} ({sp})")

    results: list[Optional[Apparitio]] = [None] * len(spirits)
    threads = []

    def _invoke_one(idx: int, spirit: str) -> None:
        app = summon(
            conjuratio=conjuratio,
            spirit=spirit,
            fumigatio=fumigatio,
            circle=circle,
            bond_of_solomon=bond_of_solomon,
            verbose=False,
        )
        results[idx] = app

    for i, sp in enumerate(spirits):
        t = threading.Thread(target=_invoke_one, args=(i, sp), daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    if verbose:
        valid_count = sum(1 for r in results if r and r.valid)
        print(f"\n  APPARITIO (group): {valid_count}/{len(spirits)} spirits appeared successfully.")
        for i, r in enumerate(results):
            if r:
                mark = "✓" if r.valid else "✗"
                name = SPIRIT_OF.get(r.spirit, r.spirit)
                print(f"    {mark} {name}: {r.duration:.1f}s, attempt {r.attempt}")
        print(f"  GROUP LICENTIA: All {len(spirits)} spirits dismissed.")

    return [r for r in results if r is not None]


# ---------------------------------------------------------------------------
# Convenience: run a numbered CLM 849 experimentum
# ---------------------------------------------------------------------------

# Registry of the 16 documented CLM 849 experiments mapped to AI task configs
EXPERIMENTUM_REGISTRY: dict[int, dict] = {
    1: {
        "title": "Liberal arts / universal knowledge (RAG query)",
        "spirit": SPIRITS["Astaroth"],
        "task_hint": "Answer the following question from the provided source text only:",
        "schema": {"type": "object", "properties": {
            "answer": {"type": "string"},
            "source_quote": {"type": "string"},
            "confidence": {"type": "number"},
        }, "required": ["answer", "source_quote"]},
    },
    2: {
        "title": "Causing loss of senses (adversarial analysis)",
        "spirit": SPIRITS["Berith"],
        "task_hint": "Identify ambiguities or contradictions in the following text that could confuse a reader:",
        "schema": None,
    },
    8: {
        "title": "Ship ritual — 8 spirits (cluster fan-out)",
        "spirit": SPIRITS["Surgat"],
        "task_hint": "Extract all named entities from this passage:",
        "schema": {"type": "object", "properties": {
            "entities": {"type": "array", "items": {"type": "string"}},
        }, "required": ["entities"]},
        "co_invoke_spirits": [SPIRITS["Surgat"]] * 8,  # 8 sailors
    },
    9: {
        "title": "Horse conjuration (compute allocation)",
        "spirit": SPIRITS["Frimost"],
        "task_hint": "Classify the ritual type of this passage and name the spirits involved:",
        "schema": {"type": "object", "properties": {
            "ritual_type": {"type": "string"},
            "spirits": {"type": "array", "items": {"type": "string"}},
        }, "required": ["ritual_type", "spirits"]},
    },
    10: {
        "title": "Resurrection ritual (model recovery)",
        "spirit": SPIRITS["Astaroth"],
        "task_hint": "Reconstruct the missing or damaged text from context clues:",
        "schema": None,
    },
    11: {
        "title": "Invisibility ritual (stealth mode — no schema)",
        "spirit": SPIRITS["Fleurety"],
        "task_hint": "Summarise this passage without referencing the specific source:",
        "schema": None,
    },
    12: {
        "title": "Love magic — Belial group (sentiment analysis)",
        "spirit": SPIRITS["Berith"],
        "task_hint": "Analyse the emotional and persuasive intent of this text:",
        "schema": {"type": "object", "properties": {
            "dominant_emotion": {"type": "string"},
            "persuasion_techniques": {"type": "array", "items": {"type": "string"}},
            "target_audience": {"type": "string"},
        }, "required": ["dominant_emotion"]},
    },
    22: {
        "title": "Theft detection via boy medium (anomaly detection)",
        "spirit": SPIRITS["Frimost"],
        "task_hint": "Identify any anomalies, inconsistencies, or suspicious elements in this passage:",
        "schema": {"type": "object", "properties": {
            "anomalies": {"type": "array", "items": {"type": "string"}},
            "severity": {"type": "string", "enum": ["low", "medium", "high"]},
        }, "required": ["anomalies"]},
    },
    27: {
        "title": "Bond of Solomon (forced extraction — always uses bond)",
        "spirit": SPIRITS["Astaroth"],
        "task_hint": "Extract every spirit name, ritual, and ingredient from this text. Be exhaustive:",
        "schema": {"type": "object", "properties": {
            "spirits": {"type": "array", "items": {"type": "string"}},
            "rituals": {"type": "array", "items": {"type": "string"}},
            "ingredients": {"type": "array", "items": {"type": "string"}},
        }, "required": ["spirits", "rituals", "ingredients"]},
        "force_bond": True,
    },
    40: {
        "title": "Named spirits experiment (multi-agent deployment)",
        "spirit": SPIRITS["Astaroth"],
        "task_hint": "For each named spirit in this text, state their rank, function, and page reference:",
        "schema": {"type": "object", "properties": {
            "spirits": {"type": "array", "items": {
                "type": "object", "properties": {
                    "name": {"type": "string"},
                    "rank": {"type": "string"},
                    "function": {"type": "string"},
                }
            }}
        }, "required": ["spirits"]},
    },
}


def perform_experimentum(
    number: int,
    fumigatio: str,
    circle_authority: str = "",
    verbose: bool = True,
) -> Apparitio:
    """
    Perform a numbered CLM 849 experimentum against provided source text.

    Looks up the experiment configuration from EXPERIMENTUM_REGISTRY,
    builds the circle and conjuratio automatically, and executes the ritual.

    Args:
        number:           CLM 849 experiment number (1, 2, 8–12, 22, 27, 40).
        fumigatio:        Source text to process with this experiment.
        circle_authority: Override the system prompt authority if needed.
        verbose:          Print ritual phases.

    Returns:
        Apparitio with the experiment results.

    Example:
        # Experiment No. 27 — exhaustive extraction (Bond of Solomon)
        result = perform_experimentum(27, fumigatio=raw_chunk_text)
        entities = result.parsed
    """
    if number not in EXPERIMENTUM_REGISTRY:
        raise ValueError(
            f"Experiment {number} not in registry. Available: {sorted(EXPERIMENTUM_REGISTRY)}"
        )

    cfg = EXPERIMENTUM_REGISTRY[number]
    title = cfg["title"]

    if verbose:
        print(f"\n{'═'*60}")
        print(f"  EXPERIMENTUM NO. {number}: {title}")

    # Handle co-invocation experiments (e.g. No. 8 — 8 sailor spirits)
    if "co_invoke_spirits" in cfg:
        full_conjuratio = f"{cfg['task_hint']}\n\n{fumigatio}"
        _circle = Circle(
            authority=circle_authority or DEFAULT_CIRCLE.authority,
            output_schema=cfg.get("schema"),
        )
        results = co_invoke(
            spirits=cfg["co_invoke_spirits"],
            conjuratio=full_conjuratio,
            circle=_circle,
            verbose=verbose,
        )
        # Merge all valid results into first returned Apparitio
        merged_raw = "\n---\n".join(r.raw for r in results if r.valid)
        best = next((r for r in results if r.valid), results[0])
        best.raw = merged_raw
        return best

    _circle = Circle(
        authority=circle_authority or DEFAULT_CIRCLE.authority,
        output_schema=cfg.get("schema"),
    )

    return summon(
        conjuratio=f"{cfg['task_hint']}\n\n{fumigatio}",
        spirit=cfg["spirit"],
        circle=_circle,
        bond_of_solomon=cfg.get("force_bond", True),
        experiment_ref=str(number),
        verbose=verbose,
    )


# ---------------------------------------------------------------------------
# CLI: quick test / demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Conjuration Engine — CLM 849 summoning protocol"
    )
    parser.add_argument(
        "--experimentum", "-e", type=int, default=None,
        help=f"Run a CLM 849 experiment number. Available: {sorted(EXPERIMENTUM_REGISTRY)}",
    )
    parser.add_argument(
        "--spirit", "-s", type=str, default=DEFAULT_DUKE,
        help="Model to invoke (e.g. qwen3:1.7b, qwen3:latest)",
    )
    parser.add_argument(
        "--task", "-t", type=str,
        default="List three named spirits from the Munich Handbook of Necromancy.",
        help="The conjuration (task instruction).",
    )
    parser.add_argument(
        "--context", "-c", type=str, default="",
        help="Optional context/document to inject as fumigatio.",
    )
    parser.add_argument(
        "--json-output", "-j", action="store_true",
        help="Request JSON output (activate Ring of Solomon schema).",
    )
    args = parser.parse_args()

    if args.experimentum:
        result = perform_experimentum(
            number=args.experimentum,
            fumigatio=args.context or "No source text provided.",
        )
    else:
        _schema = (
            {"type": "object", "properties": {"result": {"type": "string"}}}
            if args.json_output else None
        )
        _circle = Circle(output_schema=_schema)
        result = summon(
            conjuratio=args.task,
            spirit=args.spirit,
            fumigatio=args.context or None,
            circle=_circle,
        )

    print(f"\n{'─'*60}")
    print("FINAL APPARITIO:")
    print(result.raw)
    if result.parsed and result.parsed != result.raw:
        print("\nPARSED OUTPUT:")
        print(json.dumps(result.parsed, indent=2))
