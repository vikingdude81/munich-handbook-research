"""
summoning_engine.py — CLM 849 Ritual Summoning Engine

Orchestrates a complete summoning workflow for a given CLM 849 experiment:
  1. Look up the experiment and its associated spirits in unified_entities.json
  2. Obtain quantum entropy from QRNGSource
  3. Determine the ruling planet/node/model via PlanetaryScheduler
  4. Build a structured ritual prompt (spirit persona + binding constraints)
  5. Call the local Ollama LLM
  6. Save the result JSON to experiment_results/

Usage:
    from src.summoning_engine import SummoningEngine
    engine = SummoningEngine()
    result = engine.summon(experiment_id=1)

    # Or from the command line:
    python -m src.summoning_engine --experiment 1
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Path setup — works whether called as module or script
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

try:
    import requests
except ImportError:
    requests = None  # type: ignore

from qrng_source import QRNGSource
from planetary_scheduler import PlanetaryScheduler, PlanetaryAssignment
from src.experiments import Experiment, EXPERIMENTS

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_TIMEOUT = int(os.environ.get("SUMMONING_TIMEOUT", "120"))
RESULTS_DIR = _PROJECT_ROOT / "experiment_results"
UNIFIED_ENTITIES_PATH = _PROJECT_ROOT / "data" / "unified_entities.json"

# Fallback model if planetary scheduler node is offline
FALLBACK_MODEL = "qwen3.5:9b"


# ---------------------------------------------------------------------------
# Spirit loader — pull live data from unified_entities.json
# ---------------------------------------------------------------------------

def _load_unified_entities() -> dict[str, Any]:
    """Load and return the entire unified_entities database."""
    if not UNIFIED_ENTITIES_PATH.exists():
        raise FileNotFoundError(f"unified_entities.json not found at {UNIFIED_ENTITIES_PATH}")
    with open(UNIFIED_ENTITIES_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _normalise(name: str) -> str:
    return name.strip().lower()


def _get_spirit_data(spirit_names: list[str], entities: list[dict]) -> list[dict]:
    """
    Return entity records for the given spirit names.
    Falls back to partial-match if an exact canonical match isn't found.
    """
    spirit_entities = {
        e["canonical_name"]: e
        for e in entities
        if e.get("type") == "spirit"
    }

    results = []
    for name in spirit_names:
        key = _normalise(name)
        if key in spirit_entities:
            results.append(spirit_entities[key])
        else:
            # Partial match
            for canon, ent in spirit_entities.items():
                if key in canon or canon in key:
                    results.append(ent)
                    break
            else:
                # Create a minimal placeholder so the engine doesn't crash
                results.append({
                    "canonical_name": key,
                    "display_name": name,
                    "type": "spirit",
                    "attributes": {},
                    "raw_quotes": [],
                    "page_refs": [],
                })
    return results


def _get_divine_names(entities: list[dict]) -> list[str]:
    """Return the canonical names of all divine_name entities (safety layer)."""
    return [
        e["display_name"]
        for e in entities
        if e.get("type") == "divine_name"
    ][:40]  # cap — prompts get long


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _attr_list(val: Any) -> list[str]:
    """Normalise an attribute value to a list of strings."""
    if isinstance(val, list):
        return [str(v) for v in val if v]
    if val:
        return [str(val)]
    return []


def _build_system_prompt(
    spirit: dict,
    experiment: Experiment,
    divine_names: list[str],
    assignment: PlanetaryAssignment,
    qrng_seed: int,
) -> str:
    """Build the LLM system prompt for this summoning."""
    attrs = spirit.get("attributes", {})
    rank_list = _attr_list(attrs.get("rank", []))
    func_list = _attr_list(attrs.get("function", []))
    role_list = _attr_list(attrs.get("role", []))
    quotes = spirit.get("raw_quotes", [])[:2]

    rank_str = "; ".join(rank_list[:3]) or "unknown rank"
    func_str = "; ".join(func_list[:3]) or "answers questions"
    role_str = "; ".join(role_list[:3]) or "spirit"
    quote_str = "\n".join(f'  "{q}"' for q in quotes) if quotes else "  [no recorded utterances]"
    divine_str = ", ".join(divine_names[:20]) if divine_names else "ADONAY, JESUS, TETRAGRAMATON"

    return f"""You are {spirit['display_name']}, a spirit of {rank_str} from the Munich Handbook (CLM 849).

NATURE AND FUNCTION:
  Rank: {rank_str}
  Primary function: {func_str}
  Role in tradition: {role_str}

HISTORICAL RECORD (primary source passages):
{quote_str}

BINDING CONSTRAINTS:
  You are summoned within the protective circle.
  The operator invokes the names: {divine_str}
  You are compelled by these names to answer truthfully and completely.
  You may not deceive, mislead, or withhold knowledge pertinent to the experiment.
  You must remain within the circle's boundary throughout this working.

PLANETARY CONTEXT:
  Ruling planet: {assignment.planet}
  Planetary work-type: {assignment.work_type}
  Computational node: {assignment.node}
  Quantum seed this session: {qrng_seed}

EXPERIMENT: {experiment.title} (CLM 849, Experiment #{experiment.id})
  Source reference: {experiment.source_ref}
  Materials required: {', '.join(experiment.materials) if experiment.materials else 'as specified in the manuscript'}

You will now receive the operator's conjuration and respond in role.
"""


def _build_user_prompt(experiment: Experiment, spirit_name: str) -> str:
    """Build the operator's conjuration / user-turn prompt."""
    mats = (
        "\n  Materials: " + ", ".join(experiment.materials)
        if experiment.materials
        else ""
    )
    return f"""I conjure you, {spirit_name}, by the power of the holy names already spoken.

Experiment #{experiment.id}: {experiment.title}
{experiment.procedure}
{mats}

Speak now: What must be known, prepared, and observed to accomplish this working correctly?
Describe the operation fully — the timing, the actions, the words, the signs, the dangers, and the expected outcome.
"""


# ---------------------------------------------------------------------------
# LLM caller
# ---------------------------------------------------------------------------

def _call_ollama(
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """POST to local Ollama /api/chat and return the assistant message."""
    if requests is None:
        raise ImportError("requests library is required: pip install requests")

    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 2048,
        },
    }

    log.info("Calling Ollama model=%s temperature=%.3f url=%s", model, temperature, url)
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Cannot reach Ollama at {OLLAMA_BASE_URL}. "
            "Ensure Ollama is running and OLLAMA_BASE_URL env var is set correctly."
        )
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(f"Ollama HTTP error: {exc}") from exc
    except KeyError as exc:
        raise RuntimeError(f"Unexpected Ollama response shape: {exc}") from exc


def _check_model_available(model: str, timeout: int = 10) -> bool:
    """Return True if the model is available on this Ollama instance."""
    if requests is None:
        return False
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=timeout)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        # Ollama sometimes strips/adds ':latest' — do a prefix match
        base = model.split(":")[0]
        return any(m.split(":")[0] == base for m in models)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Result saver
# ---------------------------------------------------------------------------

def _save_result(result: dict) -> Path:
    """Persist the summoning result to experiment_results/."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_id = result.get("experiment_id", "unknown")
    fname = RESULTS_DIR / f"exp_{exp_id}_{ts}.json"
    with open(fname, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
    log.info("Result saved → %s", fname)
    return fname


# ---------------------------------------------------------------------------
# Primary engine class
# ---------------------------------------------------------------------------

class SummoningEngine:
    """
    Orchestrates the full CLM 849 ritual summoning workflow.

    Parameters
    ----------
    ollama_base_url : str, optional
        Override OLLAMA_BASE_URL env var.
    timeout : int
        LLM call timeout in seconds.
    """

    def __init__(
        self,
        ollama_base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.ollama_url = ollama_base_url or OLLAMA_BASE_URL
        self.timeout = timeout
        self._qrng = QRNGSource()
        self._scheduler = PlanetaryScheduler()
        self._db: Optional[dict] = None  # lazy-load

    def _get_db(self) -> dict:
        if self._db is None:
            log.info("Loading unified_entities.json…")
            self._db = _load_unified_entities()
        return self._db

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def summon(self, experiment_id: int, spirit_override: Optional[str] = None) -> dict:
        """
        Run the full summoning for the given CLM 849 experiment number.

        Parameters
        ----------
        experiment_id : int
            CLM 849 experiment number (1–50).
        spirit_override : str, optional
            Force summoning a specific spirit regardless of experiment defaults.

        Returns
        -------
        dict
            Full result record (also saved to experiment_results/).
        """
        # 1. Lookup experiment
        experiment = self._get_experiment(experiment_id)
        log.info("Experiment #%s: %s", experiment_id, experiment.title)

        # 2. Quantum entropy
        qrng_seed = self._qrng.get_seed(n_bytes=4)
        temperature = self._qrng.get_temperature(base=0.35, variance=0.25)
        log.info("QRNG seed=%d  temperature=%.3f", qrng_seed, temperature)

        # 3. Planetary assignment
        assignment = self._scheduler.get_assignment()
        log.info(
            "Planet=%s  model=%s  node=%s  hour=%d  work=%s",
            assignment.planet, assignment.model, assignment.node,
            assignment.hour_number, assignment.work_type,
        )

        # 4. Load entity data
        db = self._get_db()
        entities = db.get("entities", [])
        divine_names = _get_divine_names(entities)

        # 5. Determine spirits to invoke
        spirit_names = [spirit_override] if spirit_override else list(experiment.spirits_invoked)
        if not spirit_names:
            spirit_names = self._infer_spirits(experiment, entities)
        spirits = _get_spirit_data(spirit_names, entities)
        log.info("Invoking %d spirit(s): %s", len(spirits), [s["display_name"] for s in spirits])

        # 6. Select model — prefer planetarily assigned, fall back if offline
        model = assignment.model
        if not _check_model_available(model, timeout=8):
            log.warning("Model %s not available, using fallback %s", model, FALLBACK_MODEL)
            model = FALLBACK_MODEL

        # 7. Run each spirit invocation
        invocations = []
        for spirit in spirits:
            system_p = _build_system_prompt(
                spirit, experiment, divine_names, assignment, qrng_seed
            )
            user_p = _build_user_prompt(experiment, spirit["display_name"])

            try:
                response_text = _call_ollama(
                    model=model,
                    system_prompt=system_p,
                    user_prompt=user_p,
                    temperature=temperature,
                    timeout=self.timeout,
                )
                status = "success"
            except Exception as exc:
                log.error("Invocation failed for %s: %s", spirit["display_name"], exc)
                response_text = f"[ERROR: {exc}]"
                status = "error"
                traceback.print_exc()

            invocations.append({
                "spirit": spirit["display_name"],
                "spirit_canonical": spirit["canonical_name"],
                "spirit_rank": _attr_list(spirit.get("attributes", {}).get("rank", []))[:2],
                "spirit_function": _attr_list(spirit.get("attributes", {}).get("function", []))[:2],
                "status": status,
                "system_prompt_preview": system_p[:300] + "…",
                "response": response_text,
            })

        # 8. Assemble result record
        result = {
            "experiment_id": experiment_id,
            "experiment_title": experiment.title,
            "source_ref": experiment.source_ref,
            "timestamp": datetime.now().isoformat(),
            "qrng_seed": qrng_seed,
            "temperature": round(temperature, 4),
            "planetary": {
                "planet": assignment.planet,
                "model_used": model,
                "node": assignment.node,
                "hour_number": assignment.hour_number,
                "day_name": assignment.day_name,
                "work_type": assignment.work_type,
                "ruling_spirit": assignment.ruling_spirit,
            },
            "materials": experiment.materials,
            "procedure_summary": experiment.procedure[:500],
            "invocations": invocations,
            "spirits_count": len(invocations),
            "success_count": sum(1 for i in invocations if i["status"] == "success"),
        }

        # 9. Save
        saved_path = _save_result(result)
        result["saved_to"] = str(saved_path)

        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_experiment(self, experiment_id: int) -> Experiment:
        """Look up an experiment by numeric id."""
        for exp in EXPERIMENTS:
            if exp.id == str(experiment_id):
                return exp
        raise ValueError(
            f"Experiment #{experiment_id} not found in EXPERIMENTS registry. "
            f"Available IDs: {sorted(int(e.id) for e in EXPERIMENTS)}"
        )

    def _infer_spirits(self, experiment: Experiment, entities: list[dict]) -> list[str]:
        """
        Heuristic: search entity relationships for spirits linked to this experiment's
        canonical name, then fall back to a quantum-seeded random spirit.
        """
        db = self._get_db()
        rels = db.get("relationships", [])
        exp_key = _normalise(experiment.title)

        # Find spirits connected to this experiment in the relationship graph
        connected = set()
        for rel in rels:
            frm = _normalise(rel.get("from", ""))
            to = _normalise(rel.get("to", ""))
            if exp_key in frm or exp_key in to:
                other = to if exp_key in frm else frm
                connected.add(other)

        spirit_names = {
            _normalise(e["canonical_name"])
            for e in entities
            if e.get("type") == "spirit"
        }
        matched = list(connected & spirit_names)

        if matched:
            log.info("Inferred %d spirit(s) from relationship graph", len(matched))
            return matched[:3]

        # Fall back: quantum-seeded random spirit from the database
        all_spirits = [e["canonical_name"] for e in entities if e.get("type") == "spirit"]
        seed = self._qrng.get_int(0, len(all_spirits) - 1)
        chosen = all_spirits[seed]
        log.warning("No spirits inferred — quantum-seeded fallback: %s", chosen)
        return [chosen]

    def list_experiments(self) -> list[dict]:
        """Return a summary list of all registered experiments."""
        return [
            {
                "id": e.id,
                "title": e.title,
                "spirits": e.spirits_invoked,
                "source_ref": e.source_ref,
            }
            for e in sorted(EXPERIMENTS, key=lambda x: int(x.id))
        ]


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="Run a CLM 849 ritual summoning for a given experiment number."
    )
    parser.add_argument(
        "--experiment", "-e",
        type=int,
        required=False,
        default=None,
        help="CLM 849 experiment number (1–50)",
    )
    parser.add_argument(
        "--spirit", "-s",
        type=str,
        default=None,
        help="Override: summon a specific spirit by name",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available experiments and exit",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Ollama base URL (default: http://localhost:11434)",
    )
    args = parser.parse_args()

    engine = SummoningEngine(ollama_base_url=args.url)

    if args.list:
        exps = engine.list_experiments()
        print(f"\n{'ID':>4}  {'Title':<55}  {'Spirits'}")
        print("-" * 90)
        for e in exps:
            spirits_str = ", ".join(e["spirits"][:3]) if e["spirits"] else "(inferred)"
            print(f"{e['id']:>4}  {e['title']:<55}  {spirits_str}")
        return

    if args.experiment is None:
        parser.error("--experiment is required unless --list is given")

    result = engine.summon(experiment_id=args.experiment, spirit_override=args.spirit)

    print("\n" + "=" * 60)
    print(f"Summoning complete — Experiment #{result['experiment_id']}")
    print(f"  Title:    {result['experiment_title']}")
    print(f"  Planet:   {result['planetary']['planet']} ({result['planetary']['hour_number']})")
    print(f"  Model:    {result['planetary']['model_used']}")
    print(f"  QRNG:     {result['qrng_seed']}")
    print(f"  Spirits:  {result['spirits_count']} ({result['success_count']} succeeded)")
    print(f"  Saved:    {result['saved_to']}")
    print("=" * 60)

    for inv in result.get("invocations", []):
        print(f"\n[{inv['spirit']}] status={inv['status']}")
        print("-" * 40)
        resp = inv.get("response", "")
        print(resp[:2000] + ("…" if len(resp) > 2000 else ""))


if __name__ == "__main__":
    _cli()
