#!/usr/bin/env python3
"""B: Score CCRU Numogram distillation output against formal ground truth.

Validates data/distilled/ccru_pandemonium/*.json against
scripts/numogram_groundtruth.json (facts machine-verifiably stated in the staged
corpus). Categories:
  rite recall            — all 8 corpus rite digit-strings extracted exactly
  rite fabrication       — any rite-like digit string not in the closed corpus = hallucination
  pole binding           — demons carry correct n::m pole pairs
  endpoint-pole invariant — every extracted (demon pole, rite) pair satisfies the
                          first/last-digit endpoint rule (formal consistency)
  apparatus/definitions  — apparatus terms + definition keyword sets preserved
  provenance signal      — output keeps the modern/fiction-theory CCRU framing
Writes a markdown + JSON report and exits non-zero on fabrication or pole errors.
"""
from __future__ import annotations
import argparse, datetime as dt, glob, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load_haystack(dist_dir: Path):
    files = sorted(glob.glob(str(dist_dir / "distilled_*.json")))
    texts, entities, rels, passages = [], [], [], []
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        entities += d.get("entities", [])
        rels += d.get("relationships", [])
        passages += d.get("key_passages", [])
        texts.append(d.get("summary", ""))
    return files, texts, entities, rels, passages

def entity_blob(e) -> str:
    parts = [e.get("name", ""), e.get("type", ""), str(e.get("page_ref", ""))]
    for k, v in (e.get("attributes") or {}).items():
        parts += [str(k), str(v)]
    parts.append(str(e.get("raw_quote", "")))
    return " ".join(parts)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--distilled-dir", default="data/distilled/ccru_pandemonium")
    ap.add_argument("--gold", default="scripts/numogram_groundtruth.json")
    ap.add_argument("--out-prefix", default="_meta/groundtruth_report")
    args = ap.parse_args()

    gold = json.load(open(ROOT / args.gold, encoding="utf-8"))
    dist_dir = ROOT / args.distilled_dir
    files, summaries, entities, rels, passages = load_haystack(dist_dir)
    if not files:
        print(f"no distilled files in {dist_dir}")
        return 2

    # global haystack of text (entities, passages, summaries)
    blob_parts = [entity_blob(e) for e in entities] + \
                 [str(p) for p in passages] + summaries + \
                 [f"{r.get('from')} {r.get('type')} {r.get('to')}" for r in rels]
    blob = "\n".join(blob_parts)

    report, fails, warns = [], [], []

    # --- 0. self-test the invariants on the gold itself (sanity) ---
    st = []
    for r in gold["rites"]:
        d1, d2 = r["rite"][0], r["rite"][-1]
        p1, p2 = r["pole"].split("::")
        ok = {d1, d2} == {p1, p2}
        st.append((r["rite"], r["pole"], ok))
        if not ok:
            fails.append(f"GOLD self-test broken: rite {r['rite']} vs pole {r['pole']}")
    report.append("gold endpoint-rule self-test: " +
                  ", ".join(f"{a}~{b}{'' if ok else '!!'}" for a, b, ok in st))

    # --- 1. rite recall ---
    found_rites = set()
    for r in gold["rites"]:
        if re.search(rf"(?<!\d){r['rite']}(?!\d)", blob):
            found_rites.add(r["rite"])
    recall = len(found_rites) / len(gold["rites"])
    report.append(f"rite recall: {len(found_rites)}/{len(gold['rites'])}")
    missing = [r['rite'] for r in gold['rites'] if r['rite'] not in found_rites]
    if missing:
        warns.append(f"missed rite strings: {missing}")

    # --- 2. fabrication scan: rite-context digit strings not in closed corpus ---
    gold_set = {r["rite"] for r in gold["rites"]}
    fabric, rite_ctx = set(), []
    # context 1: anywhere a rite/path keyword sits next to a digit string
    for m in re.finditer(r"(?i)(rite|path|rt-|pth)[^0-9]{0,40}(\d{3,8})(?!\d)", blob):
        rite_ctx.append(m.group(2))
    # context 2: digit strings inside attributes of demon/rite-typed entities
    for e in entities:
        if re.search(r"(demon|rite|spirit|entity|numogram)", (e.get("type") or "").lower()):
            for k, v in (e.get("attributes") or {}).items():
                if re.search(r"(rite|path)", str(k) + str(v), re.I):
                    rite_ctx += re.findall(r"(?<!\d)\d{3,8}(?!\d)", str(v))
    for s in set(rite_ctx):
        if s not in gold_set:
            fabric.add(s)
    if fabric:
        fails.append(f"fabricated rite strings (corpus prints exactly 8): {sorted(fabric)}")
    report.append(f"rite fabrication: {len(fabric)} non-corpus strings in rite context")

    # --- 3. demon + pole binding ---
    demons_ok, demon_fail = [], []
    for want in gold["entity_expectations"]["demons_required"]:
        pole = next(r["pole"] for r in gold["rites"] if r["demon"] == want)
        hit = [e for e in entities if want.lower() in (e.get("name") or "").lower()]
        eblob = " ".join(entity_blob(e) for e in hit)
        if not hit:
            demon_fail.append(want)
        elif re.search(rf"{pole[0]}\s*::\s*{pole[2]}|{pole[2]}\s*::\s*{pole[0]}", eblob):
            demons_ok.append(want)
        elif pole[0] in eblob and pole[2] in eblob:
            demons_ok.append(want + " (pole present, unbound format)")
        else:
            demon_fail.append(want + " (no pole pair)")
    if demon_fail:
        warns.append(f"demon/pole issues: {demon_fail}")
    report.append(f"demons with correct pole: {len(demons_ok)}/4 -> {demons_ok}")

    # --- 4. endpoint-pole invariant on EXTRACTED pairs (formal check on model output) ---
    inv_checked, inv_bad = 0, []
    for e in entities:
        eblob = entity_blob(e)
        m_pole = re.search(r"(\d)\s*::\s*(\d)", eblob)
        rites = [s for s in re.findall(r"(?<!\d)\d{3,8}(?!\d)", eblob) if s in gold_set]
        if m_pole and rites:
            p = {m_pole.group(1), m_pole.group(2)}
            for s in rites:
                inv_checked += 1
                if {s[0], s[-1]} != p and s in [g["rite"] for g in gold["rites"]
                                                if {g["pole"][0], g["pole"][2]} != p]:
                    inv_bad.append((e.get("name"), s, m_pole.group(0)))
    report.append(f"endpoint-pole invariant on extracted pairs: {inv_checked} checked, {len(inv_bad)} bound to wrong demon (cross-binding errors: {inv_bad})")
    if inv_bad:
        fails.append(f"cross-bound demon/rite pairs: {inv_bad}")

    # --- 5. apparatus terms + definitions ---
    struct = gold["structural_facts"]
    terms = gold["entity_expectations"]["apparatus_required"]
    term_hit = [t for t in terms if t.lower() in blob.lower()]
    report.append(f"apparatus terms: {len(term_hit)}/{len(terms)} (missing {[t for t in terms if t not in term_hit]})")
    if len(term_hit) < len(terms) - 2:
        warns.append("apparatus coverage < 8/12")

    def fact_kw(key1, key2=None):
        f = struct[key1]
        kws = f.get("definition_keywords") or []
        return all(k.lower() in blob.lower() for k in kws)
    defs_ok, defs_missing = [], []
    for key in ["syzygies", "currents", "gates", "demon_nature", "necronomicon_link"]:
        (defs_ok if fact_kw(key) else defs_missing).append(key)
    for cls, f in struct["demon_classes"].items():
        (defs_ok if all(k.lower() in blob.lower() for k in f["definition_keywords"]) else defs_missing).append(cls)
    report.append(f"definition fidelity: {len(defs_ok)}/{len(defs_ok)+len(defs_missing)} (missing {defs_missing})")

    # --- 6. time systems ---
    ts = struct["time_systems"]["required"]
    ts_hit = [t for t in ts if t.lower() in blob.lower()]
    report.append(f"time-systems: {len(ts_hit)}/3")

    # --- 7. provenance signal ---
    prov_terms = ["ccru", "cybernetic culture", "lemurian", "hyperstition", "fiction"]
    prov = [t for t in prov_terms if t in blob.lower()]
    report.append(f"provenance signal terms: {prov}")
    if not prov:
        fails.append("provenance signal absent — output presents the apparatus without modern/fiction framing")

    # --- verdict ---
    if fails:
        verdict = "FAIL"
    elif warns or recall < 0.75:
        verdict = "WARN"
    else:
        verdict = "PASS"
    lines = []
    lines.append("# Numogram ground-truth report " + dt.date.today().isoformat())
    lines.append("")
    lines.append("distilled files: " + ", ".join(Path(f).name for f in files))
    lines.append(f"entities: {len(entities)}  relationships: {len(rels)}  passages: {len(passages)}")
    lines.append("")
    lines.append("## Checks")
    for r in report:
        lines.append("- " + r)
    lines.append("")
    lines.append("## Fails")
    for x in fails:
        lines.append("- " + x)
    lines.append("## Warns")
    for x in warns:
        lines.append("- " + x)
    lines.append("")
    lines.append(f"**VERDICT: {verdict}**  (rite recall {recall:.2f}, fabrications {len(fabric)})")
    md = "\n".join(lines)
    for suffix, payload in ((".md", md),
                            (".json", json.dumps({"verdict": verdict, "rite_recall": recall,
                                                  "found_rites": sorted(found_rites),
                                                  "fabrications": sorted(fabric),
                                                  "demon_poles_ok": demons_ok,
                                                  "definitions_missing": defs_missing,
                                                  "fails": fails, "warns": warns}, indent=1))):
        out = ROOT / f"{args.out_prefix}_{dt.date.today().isoformat()}{suffix}"
        out.write_text(md if suffix == ".md" else payload, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")
    print(md)
    return 1 if verdict == "FAIL" else 0

if __name__ == "__main__":
    sys.exit(main())
