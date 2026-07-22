"""
Spirit Vectorizer — converts unified_entities.json spirits into numeric
feature vectors for SOM topology and LGI manifold analysis.

Feature vector layout (28 dimensions):
  [0]       rank_ordinal          — hierarchical rank scaled 0–1
  [1:8]     planet_onehot         — Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon
  [8:12]    direction_onehot      — North, South, East, West
  [12:22]   function_categories   — binding, divination, love, protection,
                                    destruction, healing, invisibility,
                                    treasure, banquet, castle
  [22:25]   nature_flags          — angelic, demonic, divine_name
  [25]      source_count_norm     — number of grimoire sources (0–1)
  [26]      occurrence_norm       — log-normalized occurrence count
  [27]      cross_grimoire        — appears in 2+ distinct grimoires
"""

import json
import os
import re
import numpy as np
from math import log1p

UNIFIED_DB = os.path.join(os.path.dirname(__file__), "..", "data", "unified_entities.json")

N_FEATURES = 28

# ── Rank ordinal mapping ──────────────────────────────────────────────
RANK_MAP = {
    "king": 1.0, "king spirit": 1.0, "demonic ruler": 0.95,
    "princeps": 0.85, "princeps demoniorum": 0.85, "prince": 0.85,
    "duke": 0.75,
    "count": 0.65, "earl": 0.65,
    "knight": 0.55,
    "archangel": 0.60, "angelic hierarchy": 0.58,
    "angel": 0.50, "angelus mandans": 0.52,
    "hour ruler": 0.45,
    "divine name": 0.42, "saints": 0.42,
    "spirit": 0.35, "demonic spirit": 0.35, "powerful spirit": 0.38,
    "demon": 0.30, "demon (unspecified)": 0.30,
    "demon (resurrection ritual)": 0.30,
    "spiritus armigeri": 0.25, "squire spirit": 0.25,
    "spiritus iocundissimi": 0.28, "spiritus benignissimi": 0.28,
    "spiritus habitatores aque": 0.22,
}

# ── Planet index mapping ──────────────────────────────────────────────
PLANET_NAMES = ["saturn", "jupiter", "mars", "sun", "venus", "mercury", "moon"]
PLANET_ALIASES = {
    "saturnus": "saturn", "sol": "sun", "luna": "moon",
    "mercurius": "mercury",
    "saturnian": "saturn", "jovial": "jupiter", "solar": "sun",
    "lunar": "moon", "venusian": "venus", "mercurial": "mercury",
    "martian": "mars",
}

# ── Direction index mapping ───────────────────────────────────────────
DIRECTION_NAMES = ["north", "south", "east", "west"]

# ── Function category keywords ────────────────────────────────────────
FUNC_CATEGORIES = [
    # 0: binding / conjuration / constraining
    ["bind", "conjur", "constrain", "compel", "obedien", "command", "summon"],
    # 1: divination / knowledge / reveals
    ["divin", "knowledge", "reveal", "secret", "mirror", "vision", "wisdom", "truth"],
    # 2: love / desire / lust
    ["love", "desire", "lust", "amour", "affection", "favour"],
    # 3: protection / expulsion / defense
    ["protect", "expul", "defense", "defend", "ward", "shield", "guard", "antipathetic"],
    # 4: destruction / war / harm
    ["destruct", "war", "harm", "plague", "murder", "death", "sick", "hatred", "enemy", "malign"],
    # 5: healing
    ["heal", "cure", "remedy", "restore", "health"],
    # 6: invisibility / stealth
    ["invisib", "stealth", "cloak", "hidden", "conceal"],
    # 7: treasure / wealth / gold
    ["treasure", "wealth", "gold", "rich", "fortune", "silver", "carbuncle"],
    # 8: banquet / feast
    ["banquet", "feast", "food", "drink"],
    # 9: castle / building / architecture
    ["castle", "building", "tower", "palace", "fortress"],
]


def _as_list(val):
    """Ensure attribute value is a list of strings."""
    if val is None:
        return []
    if isinstance(val, str):
        return [val]
    if isinstance(val, list):
        return [str(v) for v in val]
    return [str(val)]


def _rank_ordinal(attrs):
    """Map rank attribute to a 0–1 ordinal value."""
    ranks = _as_list(attrs.get("rank"))
    if not ranks:
        role = _as_list(attrs.get("role"))
        ranks = role  # fallback to role for rank hints
    best = 0.2  # default for unknown
    for r in ranks:
        r_low = r.lower().strip()
        if r_low in RANK_MAP:
            best = max(best, RANK_MAP[r_low])
        else:
            # partial matching for compound rank strings
            for key, val in RANK_MAP.items():
                if key in r_low:
                    best = max(best, val)
                    break
    return best


def _planet_onehot(attrs):
    """7-dim one-hot for planetary associations."""
    vec = np.zeros(7)
    sources = _as_list(attrs.get("planet")) + _as_list(attrs.get("classification"))
    for s in sources:
        s_low = s.lower().strip()
        # check aliases first
        for alias, canonical in PLANET_ALIASES.items():
            if alias in s_low:
                vec[PLANET_NAMES.index(canonical)] = 1.0
        # check direct names
        for i, name in enumerate(PLANET_NAMES):
            if name in s_low:
                vec[i] = 1.0
    # Also check day field for planetary correlation
    days = _as_list(attrs.get("day"))
    day_planet = {
        "saturday": "saturn", "sabbat": "saturn", "diei sabbati": "saturn",
        "sunday": "sun", "dominica": "sun",
        "monday": "moon", "lunae": "moon",
        "tuesday": "mars", "martis": "mars",
        "wednesday": "mercury", "mercurii": "mercury",
        "thursday": "jupiter", "jovis": "jupiter",
        "friday": "venus", "veneris": "venus",
    }
    for d in days:
        d_low = d.lower().strip()
        for key, planet in day_planet.items():
            if key in d_low:
                vec[PLANET_NAMES.index(planet)] = 1.0
    return vec


def _direction_onehot(attrs):
    """4-dim one-hot for cardinal direction associations."""
    vec = np.zeros(4)
    dirs = _as_list(attrs.get("direction"))
    for d in dirs:
        d_low = d.lower()
        for i, name in enumerate(DIRECTION_NAMES):
            if name in d_low:
                vec[i] = 1.0
    return vec


def _function_categories(attrs):
    """10-dim multi-hot for function categories using keyword matching."""
    vec = np.zeros(10)
    texts = (_as_list(attrs.get("function")) +
             _as_list(attrs.get("functions")) +
             _as_list(attrs.get("role")) +
             _as_list(attrs.get("nature")))
    combined = " ".join(t.lower() for t in texts)
    for i, keywords in enumerate(FUNC_CATEGORIES):
        for kw in keywords:
            if kw in combined:
                vec[i] = 1.0
                break
    return vec


def _nature_flags(attrs):
    """3-dim binary: [angelic, demonic, divine_name]."""
    vec = np.zeros(3)
    all_text = " ".join(
        t.lower() for t in
        _as_list(attrs.get("rank")) +
        _as_list(attrs.get("role")) +
        _as_list(attrs.get("nature")) +
        _as_list(attrs.get("hierarchy")) +
        _as_list(attrs.get("classification"))
    )
    if re.search(r"angel|archangel|celestial|seraph|cherub|holy", all_text):
        vec[0] = 1.0
    if re.search(r"demon|infernal|diabolical|evil|malign|fallen", all_text):
        vec[1] = 1.0
    if re.search(r"divine name|blessed name|sacred name|ineffable", all_text):
        vec[2] = 1.0
    return vec


# Canonical WORK map — `necro` and `forbidden_rites_pdf` are the SAME book
# (Kieckhefer, Clm 849) ingested twice. Collapsing them prevents a book from
# counting as its own cross-reference (previously inflated source_count and the
# cross_grimoire flag for ~253 spirits). Keep in sync with
# scripts/normalize_entities.py:WORK_ID.
WORK_ID = {
    "necro": "kieckhefer_clm849",
    "forbidden_rites_pdf": "kieckhefer_clm849",
    "worship_dead": "garnier_1909",
    "ars_notoria": "ars_notoria",
    "liber_juratus": "liber_juratus",
    "discoverie": "scot_1584",
    "alchemy_mysticism": "taschen_2003",
}


def _distinct_works(entity):
    """Distinct canonical works for an entity, preferring the precomputed field."""
    if entity.get("distinct_works"):
        return set(entity["distinct_works"])
    works = set()
    for s in entity.get("sources", []):
        prefix = s.split(":")[0] if ":" in s else s
        works.add(WORK_ID.get(prefix, prefix))
    return works


def _source_features(entity, max_sources=4, max_occ=20):
    """3-dim: [work_count_norm, occurrence_norm, cross_work].

    Counts distinct WORKS (book-level), not source ingests, so the duplicated
    Kieckhefer text no longer reads as a multi-source spirit. max_sources=4
    reflects the 4 spirit-bearing primary works (Clm 849, Ars Notoria,
    Liber Juratus, Scot 1584).
    """
    vec = np.zeros(3)
    works = _distinct_works(entity)
    vec[0] = min(len(works) / max_sources, 1.0)
    occ = entity.get("occurrence_count", 1)
    vec[1] = log1p(occ) / log1p(max_occ)
    vec[2] = 1.0 if len(works) >= 2 else 0.0
    return vec


def vectorize_spirit(entity):
    """Convert a single spirit entity dict to a 28-dim numpy vector."""
    attrs = entity.get("attributes", {})
    parts = [
        np.array([_rank_ordinal(attrs)]),    # 1
        _planet_onehot(attrs),                # 7
        _direction_onehot(attrs),             # 4
        _function_categories(attrs),          # 10
        _nature_flags(attrs),                 # 3
        _source_features(entity),             # 3
    ]
    return np.concatenate(parts)


def load_seed_spirits(db_path=None, require_attributes=False, min_occurrence=1):
    """
    Load all spirits from the unified database and vectorize them.

    Args:
        require_attributes: if True, drop spirits with no attributes — these
            produce near-zero vectors that collapse onto a single SOM node (the
            spurious "Unnamed Host" mega-cluster of ~436). Use for honest
            topology; ~70% of records are single-occurrence noise.
        min_occurrence: drop spirits seen fewer than this many times.

    Returns:
        data: np.ndarray of shape (n_spirits, 28) — feature vectors
        names: list[str] — canonical spirit names
    """
    if db_path is None:
        db_path = UNIFIED_DB
    db_path = os.path.abspath(db_path)

    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    spirits = [e for e in db["entities"] if e.get("type") == "spirit"]
    if require_attributes:
        spirits = [s for s in spirits if s.get("attributes")]
    if min_occurrence > 1:
        spirits = [s for s in spirits if s.get("occurrence_count", 1) >= min_occurrence]

    names = []
    vectors = []
    for s in spirits:
        name = s.get("canonical_name") or s.get("display_name", "unknown")
        vec = vectorize_spirit(s)
        names.append(name)
        vectors.append(vec)

    data = np.array(vectors, dtype=np.float64)
    return data, names


def get_feature_labels():
    """Return human-readable labels for each feature dimension."""
    labels = ["rank_ordinal"]
    labels += [f"planet_{p}" for p in PLANET_NAMES]
    labels += [f"dir_{d}" for d in DIRECTION_NAMES]
    labels += [
        "func_binding", "func_divination", "func_love", "func_protection",
        "func_destruction", "func_healing", "func_invisibility",
        "func_treasure", "func_banquet", "func_castle",
    ]
    labels += ["nature_angelic", "nature_demonic", "nature_divine_name"]
    labels += ["source_count_norm", "occurrence_norm", "cross_grimoire"]
    return labels


if __name__ == "__main__":
    data, names = load_seed_spirits()
    labels = get_feature_labels()
    print(f"Vectorized {len(names)} spirits -> shape {data.shape}")
    print(f"Feature labels ({len(labels)}): {labels}")
    print(f"\nFeature stats:")
    for i, label in enumerate(labels):
        col = data[:, i]
        nonzero = np.count_nonzero(col)
        print(f"  {label:24s}  mean={col.mean():.3f}  nonzero={nonzero:4d}/{len(names)}")
    print(f"\nSample: {names[0]} -> {data[0]}")