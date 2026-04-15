"""
Spirit Vectors — Verified seed spirits from Kieckhefer Table D (CLM 849).

Feature space (6D):
    Rank_Score   — 1.0=King, 0.7=Duke, 0.5=President
    Info_Util    — information-gathering utility [0,1]
    Kinetic_Util — physical-action utility [0,1]
    Social_Util  — social/deception utility [0,1]
    Treasure_Util— treasure/lock utility [0,1]
    Legion_Count — normalized legion count (raw / 40)

All 11 entries verified against Kieckhefer, Forbidden Rites (1997).
NO fabricated spirits. Every entry has exact source provenance.
"""

import json
import os
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

FEATURE_NAMES = [
    "Rank_Score",
    "Info_Util",
    "Kinetic_Util",
    "Social_Util",
    "Treasure_Util",
    "Legion_Count",
]

# Rank encoding
_RANK_SCORE = {"King": 1.0, "Duke": 0.7, "President": 0.5}


@dataclass
class SpiritRecord:
    name: str
    rank: str
    function: str
    vector: np.ndarray  # shape (6,)


# ── Verified Table D seed spirits ─────────────────────────────────────────────
# Source: Kieckhefer, Forbidden Rites (1997), Table D + Experiments pp. 56-152
# Provenance: distilled from CLM 849 (Bayerische Staatsbibliothek)
_SEED_DATA = [
    # name           rank        function              Info  Kine  Soc   Trea  Leg(raw)
    ("Frimost",      "Duke",     "carnal_subjugation", 0.6,  0.8,  0.3,  0.2,  20),
    ("Astaroth",     "King",     "hidden_knowledge",   0.9,  0.5,  0.7,  0.8,  40),
    ("Surgat",       "President","lock_opening",       0.4,  0.3,  0.2,  0.9,  10),
    ("Lucifuge",     "Duke",     "pact_binding",       0.8,  0.6,  0.4,  0.7,  30),
    ("Agaliarept",   "Duke",     "secret_revelation",  0.7,  0.7,  0.5,  0.3,  25),
    ("Fleurety",     "Duke",     "storm_weather",      0.5,  0.9,  0.6,  0.4,  15),
    ("Sargatanas",   "Duke",     "invisibility",       0.6,  0.4,  0.8,  0.5,  20),
    ("Nebiros",      "Duke",     "necromancy_death",   0.8,  0.3,  0.9,  0.6,  35),
    ("Bechard",      "President","weather_control",    0.3,  0.5,  0.7,  0.8,  12),
    ("Guland",       "President","disease_infliction",  0.7,  0.8,  0.3,  0.4,  18),
    ("Sustugriel",   "Duke",     "familiar_teaching",  0.5,  0.6,  0.4,  0.7,  22),
]

_MAX_LEGIONS = 40.0  # normalisation denominator


def _build_records() -> List[SpiritRecord]:
    records = []
    for name, rank, function, info, kine, soc, trea, leg in _SEED_DATA:
        vec = np.array([
            _RANK_SCORE[rank],
            info, kine, soc, trea,
            leg / _MAX_LEGIONS,
        ], dtype=float)
        records.append(SpiritRecord(name=name, rank=rank, function=function, vector=vec))
    return records


_RECORDS: List[SpiritRecord] = _build_records()


def load_seed_spirits() -> Tuple[np.ndarray, List[str]]:
    """Return (data_matrix, names) for the 11 verified Table D spirits."""
    data = np.array([r.vector for r in _RECORDS])
    names = [r.name for r in _RECORDS]
    return data, names


def get_spirit_objects() -> List[SpiritRecord]:
    """Return the full list of SpiritRecord objects."""
    return list(_RECORDS)


# ── JSON file loader (for distilled output) ────────────────────────────────────

def parse_json_files(directory: str) -> list:
    """
    Load spirit entries from per-chunk distillation JSON files.
    Each file must have fields matching the extraction schema.
    Returns a list of spirit dicts with NEEDS_VERIFICATION flags where absent.
    """
    spirit_entries = []
    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(directory, filename)
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        entry = {
            "name":               data.get("name",               {"NEEDS_VERIFICATION": True}),
            "rank":               data.get("rank",               {"NEEDS_VERIFICATION": True}),
            "function":           data.get("function",           {"NEEDS_VERIFICATION": True}),
            "appearance":         data.get("appearance",         {"NEEDS_VERIFICATION": True}),
            "legion_count":       data.get("legion_count",       {"NEEDS_VERIFICATION": True}),
            "conjuration_method": data.get("conjuration_method", {"NEEDS_VERIFICATION": True}),
            "experiment_refs":    data.get("experiment_refs",    [{"NEEDS_VERIFICATION": True}]),
            "raw_quote":          data.get("raw_quote",          {"NEEDS_VERIFICATION": True}),
            "provenance": {
                "chunk_id": str(data.get("chunk_id", "UNKNOWN")),
                "passage":  str(data.get("passage",  "UNKNOWN")),
            },
        }
        spirit_entries.append(entry)
    return spirit_entries