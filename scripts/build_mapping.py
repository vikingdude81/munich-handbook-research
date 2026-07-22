"""
Map Munich Handbook necromantic practices to modern AI agent practices.

Generates: E:\munich_handbook_research\necromancy_to_ai_mapping.txt

The Munich Handbook (CLM 849) describes structured protocols for summoning,
binding, and commanding non-human intelligences. Modern AI agent orchestration
does the same — with models instead of demons.

This script extracts the actual ritual structures from the database and
maps each element to its AI counterpart.
"""
import json
import os
from collections import Counter, defaultdict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_ROOT, "data", "unified_entities.json")
OUT_PATH = os.path.join(_ROOT, "necromancy_to_ai_mapping.txt")

db = json.load(open(DB_PATH, "r", encoding="utf-8"))
entities = db["entities"]
relationships = db["relationships"]
summaries = db["chunk_summaries"]

def a(attrs, key, default=""):
    v = attrs.get(key, default)
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    return str(v)

def is_munich(e):
    return any(s.split(":")[0] in ("necro", "forbidden_rites_pdf") for s in e["sources"])

spirits = [e for e in entities if e["type"] == "spirit" and is_munich(e)]
rituals = [e for e in entities if e["type"] == "ritual" and is_munich(e)]
tools   = [e for e in entities if e["type"] == "tool" and is_munich(e)]
ingredients = [e for e in entities if e["type"] == "ingredient" and is_munich(e)]
incantations = [e for e in entities if e["type"] == "incantation" and is_munich(e)]
divine_names = [e for e in entities if e["type"] == "divine_name" and is_munich(e)]

# Classify rituals by purpose
conjure_words  = ["conjur", "summon", "invok", "invoc", "call forth", "appear", "evoc"]
bind_words     = ["bind", "compel", "command", "oblig", "constrain", "obey", "obedien"]
protect_words  = ["circle", "protect", "ward", "consecrat", "shield", "seal", "agla", "tetragram"]
divine_words   = ["divine", "name", "god", "christ", "holy", "sancti", "domin"]
vision_words   = ["mirror", "crystal", "scry", "basin", "vision", "reveal", "see"]
illusion_words = ["illusio", "castle", "horse", "banquet", "flying", "invisible", "ship", "throne"]
love_words     = ["love", "amour", "woman", "desire", "burning"]
knowledge_words= ["knowledge", "arts", "learn", "know", "reveal truth", "thief", "murder"]
harm_words     = ["harm", "afflict", "death", "kill", "destroy", "hate", "hatred"]

def classify_ritual(e):
    blob = json.dumps(e).lower()
    cats = []
    if any(w in blob for w in conjure_words):  cats.append("CONJURATION")
    if any(w in blob for w in bind_words):     cats.append("BINDING")
    if any(w in blob for w in protect_words):  cats.append("PROTECTION")
    if any(w in blob for w in divine_words):   cats.append("DIVINE_AUTHORITY")
    if any(w in blob for w in vision_words):   cats.append("SCRYING")
    if any(w in blob for w in illusion_words): cats.append("ILLUSION")
    if any(w in blob for w in love_words):     cats.append("LOVE_MAGIC")
    if any(w in blob for w in knowledge_words):cats.append("KNOWLEDGE")
    if any(w in blob for w in harm_words):     cats.append("HARM")
    return cats or ["GENERAL"]

# Classify spirits by function
def classify_spirit(e):
    blob = json.dumps(e).lower()
    cats = []
    if any(w in blob for w in ["prince", "king", "ruler", "lord", "princeps"]):
        cats.append("COMMANDER")
    if any(w in blob for w in ["castle", "banquet", "horse", "ship", "flying"]):
        cats.append("SPECIALIST_ILLUSIONIST")
    if any(w in blob for w in ["knowledge", "reveal", "truth", "answer"]):
        cats.append("ORACLE")
    if any(w in blob for w in ["love", "desire", "woman"]):
        cats.append("SPECIALIST_LOVE")
    if any(w in blob for w in ["treasure", "gold", "silver"]):
        cats.append("SPECIALIST_TREASURE")
    if any(w in blob for w in ["harm", "afflict", "death", "hatred"]):
        cats.append("SPECIALIST_HARM")
    if any(w in blob for w in ["inscri", "circle", "protect"]):
        cats.append("GUARDIAN")
    return cats or ["GENERAL"]

# Build ritual classification stats
ritual_cats = Counter()
for r in rituals:
    for c in classify_ritual(r):
        ritual_cats[c] += 1

spirit_cats = Counter()
for s in spirits:
    for c in classify_spirit(s):
        spirit_cats[c] += 1

# Extract numbered experiments
numbered_exps = []
for e in entities:
    name_lower = e["display_name"].lower()
    if ("experiment no." in name_lower or "no." in name_lower) and e["type"] == "ritual":
        attrs = e.get("attributes", {})
        purpose = a(attrs, "purpose") or a(attrs, "function") or a(attrs, "role")
        numbered_exps.append((e["display_name"], purpose, e))

# Extract conjuration protocols (spirits with detailed summoning info)
conjure_protocols = []
for s in spirits:
    attrs = s.get("attributes", {})
    blob = json.dumps(attrs).lower()
    has_method = any(w in blob for w in ["conjur", "circle", "fumig", "invoc", "inscri", "candle", "basin", "mirror"])
    if has_method and s["occurrence_count"] >= 2:
        method_bits = {}
        for k, v in attrs.items():
            method_bits[k] = a(attrs, k)
        conjure_protocols.append((s, method_bits))

# Relationship-based protocol extraction
conjure_rels = [r for r in relationships if r["type"] in (
    "conjures", "invoked-by", "invoked-in", "binds", "binds_obligates",
    "commanded-by", "commands", "used-in", "inscribed-on", "recited_during",
    "addresses")]

# Build protocol chains: spirit -> ritual -> tools/ingredients
protocol_chains = defaultdict(lambda: {"rituals": set(), "tools": set(), "ingredients": set(), 
                                        "incantations": set(), "divine_names": set()})
for rel in relationships:
    f, t, rtype = rel["from"], rel["to"], rel["type"]
    # Find what type each endpoint is
    f_ents = [e for e in entities if e["canonical_name"] == f]
    t_ents = [e for e in entities if e["canonical_name"] == t]
    if not f_ents or not t_ents:
        continue
    fe, te = f_ents[0], t_ents[0]
    # If a spirit is connected to a ritual
    if fe["type"] == "spirit" and te["type"] == "ritual":
        protocol_chains[fe["canonical_name"]]["rituals"].add(te["display_name"])
    elif te["type"] == "spirit" and fe["type"] == "ritual":
        protocol_chains[te["canonical_name"]]["rituals"].add(fe["display_name"])
    # Spirit -> tool
    if fe["type"] == "spirit" and te["type"] == "tool":
        protocol_chains[fe["canonical_name"]]["tools"].add(te["display_name"])
    # Spirit -> ingredient
    if fe["type"] == "spirit" and te["type"] == "ingredient":
        protocol_chains[fe["canonical_name"]]["ingredients"].add(te["display_name"])

# ================================================================
# OUTPUT
# ================================================================
lines = []
def out(t=""):
    lines.append(t)

out("=" * 90)
out("  NECROMANCY → AI: MAPPING MEDIEVAL CONJURATION TO MODERN AGENT ORCHESTRATION")
out("  From the Munich Handbook (CLM 849) to GPU Clusters")
out("=" * 90)
out()
out("  The Munich Necromancer's Handbook describes structured protocols for")
out("  summoning, binding, constraining, and commanding non-human intelligences.")
out("  Modern AI agent systems do exactly the same thing—with language models")
out("  instead of demons, system prompts instead of incantations, and API calls")
out("  instead of circles.")
out()
out("  This document maps each structural element of 15th-century necromantic")
out("  practice onto its direct counterpart in modern AI agent architecture,")
out("  drawing from 2,903 extracted entities across the Munich Handbook sources.")
out()

# ================================================================
# SECTION 1: THE STRUCTURAL PARALLEL
# ================================================================
out("=" * 90)
out("  SECTION 1: THE STRUCTURAL PARALLEL")
out("=" * 90)
out()
out("  NECROMANTIC CONJURATION              →  AI AGENT ORCHESTRATION")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  The Practitioner / Magister          →  The Orchestrator / Brain Agent")
out("  Named Spirits (demons)               →  Named Models (LLMs)")
out("  The Experiment (experimentum)        →  The Task / Workflow")
out("  The Conjuration Text (conjuratio)    →  The System Prompt")
out("  The Circle (circulus)                →  The Sandbox / Guardrails")
out("  Divine Names (nomina Dei)            →  Safety Alignment / RLHF Constraints")
out("  Fumigations & Offerings              →  Context Window / Token Budget")
out("  The Mirror / Crystal / Basin         →  The Output Interface / Response")
out("  Binding & Compelling                 →  Temperature, Top-p, Structured Output")
out("  Spirit Hierarchy (kings, princes)    →  Model Tiers (heavy, fast, embed)")
out("  Consecration of the Book             →  Model Fine-tuning / Calibration")
out("  Intensified Conjuration (bond)       →  Retry Logic / Escalation")
out("  Co-invoked Spirits                   →  Multi-agent Fan-out")
out("  Directional Spirits (N/S/E/W)       →  Worker Node Assignment")
out("  Planetary/Day Assignments            →  Scheduling / Cron Triggers")
out("  The Pact (pactum)                    →  The API Key / Auth Token")
out("  Licentia (spirit dismissal)          →  Session Teardown / Connection Close")
out()

# ================================================================
# SECTION 2: SPIRIT TAXONOMY → MODEL TAXONOMY
# ================================================================
out("=" * 90)
out("  SECTION 2: SPIRIT TAXONOMY → MODEL TAXONOMY")
out("=" * 90)
out()
out("  The Munich Handbook organizes its spirits into functional tiers.")
out("  Your GPU cluster organizes its models the same way.")
out()
out(f"  SPIRIT ROLE DISTRIBUTION (from {len(spirits)} Munich spirits):")
for cat, count in spirit_cats.most_common():
    out(f"    {cat:30s} {count:4d} spirits")
out()

out("  TIER MAPPING:")
out("  ─────────────────────────────────────────────────────────────────────────────")
out()
out("  CLM 849 TIER                    YOUR CLUSTER TIER")
out("  ─────────────────────────────────────────────────────────────────────────────")
out()

# Princes / Kings
princes = [s for s in spirits if any(w in json.dumps(s.get("attributes",{})).lower() 
           for w in ["prince", "princeps", "king", "rex"])]
out(f"  PRINCES / KINGS ({len(princes)} spirits)     →  HEAVY MODELS (120B+ parameter)")
out("  ┌─────────────────────────────────────────────────────────────────────────┐")
out("  │ These are the supreme authorities — invoked for the most important     │")
out("  │ operations, requiring elaborate preparation (large context, expensive).│")
out("  │ They command lesser spirits. In your cluster: qwen3-coder-next 120B.  │")
out("  └─────────────────────────────────────────────────────────────────────────┘")
out("  Munich examples:")
for s in sorted(princes, key=lambda x: -x["occurrence_count"])[:8]:
    attrs = s.get("attributes", {})
    rank = a(attrs, "rank") or a(attrs, "role")
    out(f"    {s['display_name']:25s} x{s['occurrence_count']:2d}  {rank[:55]}")
out()

# Specialist spirits
specialists = [s for s in spirits if "castle conjurer" in json.dumps(s.get("attributes",{})).lower()
               or "banquet conjurer" in json.dumps(s.get("attributes",{})).lower()
               or "appears in mirror" in json.dumps(s.get("attributes",{})).lower()
               or "horse" in json.dumps(s.get("attributes",{})).lower()]
out(f"  SPECIALIST SPIRITS ({len(specialists)} spirits)  →  TASK-SPECIFIC MODELS (9B-35B)")
out("  ┌─────────────────────────────────────────────────────────────────────────┐")
out("  │ Each specialist does ONE thing: conjure castles, banquets, horses,     │")
out("  │ mirrors. They're invoked in groups for parallel operations. In your    │")
out("  │ cluster: qwen3.5-9b, qwen3.5-35b (multiple worker slots).            │")
out("  └─────────────────────────────────────────────────────────────────────────┘")
out("  Munich examples:")
for s in sorted(specialists, key=lambda x: -x["occurrence_count"])[:10]:
    attrs = s.get("attributes", {})
    fn = a(attrs, "function") or a(attrs, "role")
    out(f"    {s['display_name']:25s} | {fn[:55]}")
out()

# Circle-inscribed / protective names
inscribed = [s for s in spirits if "inscri" in json.dumps(s.get("attributes",{})).lower()
             or "circle" in json.dumps(s.get("attributes",{})).lower()]
out(f"  INSCRIBED / GUARDIAN NAMES ({len(inscribed)} spirits)  →  SAFETY LAYER / GUARDRAILS")
out("  ┌─────────────────────────────────────────────────────────────────────────┐")
out("  │ Names written on circles, rings, and tools to CONSTRAIN the conjured   │")
out("  │ spirits. They don't do the work — they prevent the worker from going   │")
out("  │ rogue. In AI: system prompt constraints, output validators, content    │")
out("  │ filters, structured output schemas.                                    │")
out("  └─────────────────────────────────────────────────────────────────────────┘")
out()

# ================================================================
# SECTION 3: CONJURATION PROTOCOLS → AGENT PROMPTING PATTERNS
# ================================================================
out("=" * 90)
out("  SECTION 3: CONJURATION PROTOCOLS → AGENT PROMPTING PATTERNS")
out("=" * 90)
out()
out(f"  RITUAL CATEGORY DISTRIBUTION (from {len(rituals)} Munich rituals):")
for cat, count in ritual_cats.most_common():
    out(f"    {cat:30s} {count:4d} rituals")
out()

out("  THE CONJURATION SEQUENCE (from CLM 849) mapped to AI agent calls:")
out("  ─────────────────────────────────────────────────────────────────────────────")
out()
out("  STEP 1: CONSECRATION (consecratio libri)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: The handbook itself must be consecrated over 9 days with fasting,")
out("  prayer, and holy water before ANY experiment can work.")
out()
out("  AI Equivalent: MODEL CALIBRATION / FINE-TUNING")
out("  - Loading model weights (the 'book' of knowledge)")
out("  - Setting context window size (the 'consecration period')")
out("  - RLHF alignment (the 'prayers' that shape behavior)")
out("  - Your cluster: `ollama pull qwen3-coder-next` = consecrating the grimoire")
out()
out("  From the source texts:")
consec = [e for e in entities if "consecrat" in e["display_name"].lower() or "consecra" in json.dumps(e.get("attributes",{})).lower()]
for c in consec[:5]:
    if c.get("raw_quotes"):
        out(f"    \"{c['raw_quotes'][0][:120]}\"")
out()

out("  STEP 2: DRAW THE CIRCLE (circulus)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: Draw a circle on the ground with sword/stylus. Inscribe divine")
out("  names (Tetragrammaton, Adonay, Alpha et O) around the perimeter.")
out("  The practitioner stands INSIDE. The spirit appears OUTSIDE.")
out()
out("  AI Equivalent: THE SANDBOX / SYSTEM PROMPT BOUNDARIES")
out("  - The circle = the system prompt that constrains the model's behavior")
out("  - Divine names on the circle = alignment instructions, safety rules")
out("  - Practitioner inside = orchestrator process (your brain.py)")
out("  - Spirit outside = model inference (runs in its own context)")
out("  - Names inscribed: Tetragrammaton = 'You are a helpful assistant'")
out("  - AGLA = 'Do not generate harmful content'")
out("  - Alpha et Omega = 'Stay within your knowledge boundaries'")
out()
out("  Actual circle inscriptions from CLM 849:")
circle_spirits = [s for s in spirits if "circle" in json.dumps(s.get("attributes",{})).lower() 
                  and "inscri" in json.dumps(s.get("attributes",{})).lower()]
for cs in circle_spirits[:6]:
    out(f"    {cs['display_name']:25s} (inscribed on circle for protection/constraint)")
out()

out("  STEP 3: THE CONJURATION TEXT (conjuratio)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: Speak the conjuration formula — a structured text that:")
out("    1. Names the spirit to be summoned")
out("    2. States the authority under which you command (divine names)")
out("    3. Commands what the spirit must do")
out("    4. Specifies the form the spirit must appear in")
out("    5. Threatens punishment for disobedience")
out()
out("  AI Equivalent: THE API CALL / PROMPT")
out("    1. model='qwen3-coder-next'     ← naming the spirit")
out("    2. system='You are bound by...'  ← claiming authority")
out("    3. user='Extract entities from'  ← stating the task")
out("    4. response_format=json          ← specifying appearance form")
out("    5. retry_on_failure=True         ← threatening escalation")
out()
out("  Actual conjuration formulas from CLM 849:")
for ic in incantations[:8]:
    attrs = ic.get("attributes", {})
    fn = a(attrs, "function") or a(attrs, "purpose") or a(attrs, "role")
    out(f"    {ic['display_name'][:50]:50s} | {fn[:35]}")
    if ic.get("raw_quotes"):
        q = ic["raw_quotes"][0][:120]
        out(f"      \"{q}\"")
out()

out("  STEP 4: FUMIGATION / OFFERING (suffumigatio)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: Burn specific substances to attract/feed the spirit.")
out("  Different spirits require different fumigations.")
out()
out("  AI Equivalent: CONTEXT / TOKEN BUDGET / INPUT DATA")
out("  - The fumigation IS the context window content — it's what you 'feed'")
out("    the model to make it produce useful output")
out("  - Wrong fumigation = wrong context = bad output")
out("  - Insufficient fumigation = insufficient context = hallucination")
out()
out("  Actual fumigation ingredients from CLM 849:")
fumigations = [e for e in ingredients if "fumig" in json.dumps(e.get("attributes",{})).lower()
               or "incense" in json.dumps(e.get("attributes",{})).lower()
               or "burn" in json.dumps(e.get("attributes",{})).lower()
               or "smoke" in json.dumps(e.get("attributes",{})).lower()]
for f in fumigations[:10]:
    attrs = f.get("attributes", {})
    use = a(attrs, "use") or a(attrs, "function") or a(attrs, "role")
    out(f"    {f['display_name']:35s} | {use[:50]}")
out()

out("  STEP 5: THE APPEARANCE (apparitio)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: Spirit appears in mirror, crystal, basin, boy's palm, or")
out("  within the circle. Must speak in 'clear and intelligible voice.'")
out()
out("  AI Equivalent: MODEL RESPONSE / OUTPUT")
out("  - Mirror/crystal/basin = the output channel (API response, terminal)")
out("  - 'Clear and intelligible voice' = well-formed JSON, valid code")
out("  - Boy medium (puer) = lightweight proxy model that relays the response")
out("  - Failed appearance = timeout, malformed output, refusal")
out()
out("  Scrying/vision tools from CLM 849:")
vision_tools = [e for e in tools if any(w in e["display_name"].lower() for w in 
                ["mirror", "crystal", "basin", "blade", "ring"])]
vision_tools += [e for e in entities if e["type"] == "tool" and any(w in json.dumps(e.get("attributes",{})).lower() 
                 for w in ["scry", "vision", "appear", "reveal"])]
seen = set()
for vt in vision_tools:
    if vt["display_name"] not in seen:
        seen.add(vt["display_name"])
        out(f"    {vt['display_name']:35s}")
out()

out("  STEP 6: BINDING & COMPELLING (ligatio)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: If the spirit doesn't appear or disobeys, use escalating formulas:")
out("    1. First conjuration (polite request)")
out("    2. Second conjuration (stronger command)")
out("    3. Bond of Solomon (ultimate compulsion)")
out("    4. 'By the living God, by the true God...' (divine authority chain)")
out()
out("  AI Equivalent: RETRY LOGIC & ESCALATION")
out("    1. First call (standard temperature)")
out("    2. Retry with higher max_tokens (more room to think)")
out("    3. Escalate to larger model (120B instead of 9B)")
out("    4. Force structured output schema (JSON mode)")
out()
out("  Your actual retry chain in source_distill.py:")
out("    1. Send to 120B with reasoning prompt → parse JSON")
out("    2. If JSON fails → _repair_json() (local re-parse)")
out("    3. If still fails → re-send with REASONING_MAX_TOKENS=16384")
out("    4. If STILL fails → raw text saved, flagged for manual review")
out("  This IS the Bond of Solomon — escalating compulsion until compliance.")
out()
out("  Bond of Solomon from CLM 849:")
bond = [e for e in entities if "bond" in e["display_name"].lower() or "solomon" in e["display_name"].lower()]
for b in bond[:5]:
    attrs = b.get("attributes", {})
    fn = a(attrs, "function") or a(attrs, "purpose") or a(attrs, "role")
    out(f"    {b['display_name']:40s} | {fn[:45]}")
    if b.get("raw_quotes"):
        out(f"      \"{b['raw_quotes'][0][:120]}\"")
out()

out("  STEP 7: LICENTIA (dismissal)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: After the spirit completes its task, formally dismiss it")
out("  back to its place. Failure to dismiss = spirit haunts/attacks.")
out()
out("  AI Equivalent: SESSION TEARDOWN / CONNECTION CLOSE")
out("  - Closing the API connection")
out("  - Freeing GPU VRAM")
out("  - Clearing context window")
out("  - Failure to dismiss = memory leak, orphaned inference, runaway token spend")
out()

# ================================================================
# SECTION 4: THE NUMBERED EXPERIMENTS → AGENT TASK TYPES
# ================================================================
out("=" * 90)
out("  SECTION 4: THE EXPERIMENTS → AGENT TASK TYPES")
out("=" * 90)
out()
out("  Kieckhefer identifies ~50 numbered experiments in CLM 849.")
out("  Each experiment is a self-contained protocol with specific inputs,")
out("  spirits, tools, and expected outputs. They ARE agent task templates.")
out()
out("  EXPERIMENT                               AI TASK EQUIVALENT")
out("  ─────────────────────────────────────────────────────────────────────────────")

experiment_mappings = [
    ("No. 1: Liberal arts knowledge", "RAG query — retrieve knowledge from corpus", "Knowledge retrieval via spirit"),
    ("No. 2: Causing loss of senses", "Adversarial attack — confuse/disable another agent", "Denial of service against target"),
    ("No. 8: Ship ritual", "Infrastructure provisioning — spin up compute cluster", "Conjure illusory ship with 8 sailor spirits"),
    ("No. 9: Horse conjuration", "Compute allocation — provision inference worker", "Summon spirit-horse for transport"),
    ("No. 10: Resurrection ritual", "Model recovery — restore crashed inference server", "Animate dead / make living appear dead"),
    ("No. 11: Invisibility ritual", "Stealth mode — agent operates without logging", "Obtain invisibility cloak via 4 spirits"),
    ("No. 12: Love magic", "Sentiment manipulation — optimize for engagement", "Induce love in target via Belial/Astaroth/Paymon"),
    ("No. 14: Horse ritual (v2)", "Auto-scaling — spin up additional workers", "Obtain additional illusory horses"),
    ("No. 15: Flying throne", "Elevated privileges — root/admin access", "Obtain flying throne (ultimate transport)"),
    ("No. 17: Horse (conjuratio ad equum)", "Scheduled task — cron-triggered worker", "Summon transport on command"),
    ("No. 21: Invisibility (plant)", "Lightweight stealth — minimal resource approach", "Achieve invisibility via plant instead of spirits"),
    ("No. 22: Theft detection (per puerum)", "Anomaly detection — find attacker/intruder", "Bind boy to reveal thief/murderer"),
    ("No. 27: Intensified conjuration", "Force escalation — override safety for critical task", "Bond of Solomon for non-responding spirits"),
    ("No. 40: Named spirits experiment", "Multi-agent deployment — deploy named specialists", "Invoke Astaroth + specific named spirits"),
    ("No. 43: Horse ritual (v3)", "Horizontal scaling — more of same worker type", "Yet another horse conjuration variant"),
    ("No. 45: Invisibility (dove)", "Resource-intensive stealth — sacrifice for capability", "Invisibility via dove sacrifice (costly input)"),
]

for exp_name, ai_equiv, original_purpose in experiment_mappings:
    out(f"  {exp_name:40s} →  {ai_equiv}")
    out(f"    Original: {original_purpose}")
    out()

# ================================================================
# SECTION 5: SPIRIT CO-INVOCATION → MULTI-AGENT FAN-OUT
# ================================================================
out("=" * 90)
out("  SECTION 5: SPIRIT CO-INVOCATION → MULTI-AGENT FAN-OUT")
out("=" * 90)
out()
out("  CLM 849 frequently invokes MULTIPLE spirits simultaneously.")
out("  This is exactly what focus_mode.py does — fan out to multiple")
out("  worker models in parallel.")
out()

# Get co-invocation groups
co_rels = [r for r in relationships if r["type"] in (
    "co-invoked", "co-appearing_spirit", "co-conjured spirit",
    "co-conjured kings", "co-conjured spirit in invisibility ritual",
    "co-occurrence_in_conjuration")]
co_graph = defaultdict(set)
for r in co_rels:
    co_graph[r["from"]].add(r["to"])
    co_graph[r["to"]].add(r["from"])

out("  CONJURATION GROUPS (spirits invoked together):")
out("  ─────────────────────────────────────────────────────────────────────────────")
out()
for spirit in sorted(co_graph.keys(), key=lambda x: -len(co_graph[x])):
    companions = sorted(co_graph[spirit])
    if len(companions) >= 2:
        out(f"  {spirit:25s} + {', '.join(companions)}")
        out(f"    AI parallel: fan-out task to {len(companions)+1} worker models simultaneously")
        out()

out("  KEY PATTERN: The Munich conjurer doesn't invoke one spirit for complex")
out("  tasks — they invoke a GROUP, each with a specialty. Your cluster does")
out("  the same: brain.py fans out to 5090 + 4070 + A2000 + 3060 simultaneously.")
out()

# Castle conjurers
castle_spirits = [s for s in spirits if "castle conjurer" in json.dumps(s.get("attributes",{})).lower()]
banquet_spirits = [s for s in spirits if "banquet conjurer" in json.dumps(s.get("attributes",{})).lower()]

if castle_spirits:
    out(f"  CASTLE CONJURER GROUP ({len(castle_spirits)} spirits):")
    out(f"    {', '.join(s['display_name'] for s in castle_spirits)}")
    out(f"    All invoked together to produce one illusion (castle).")
    out(f"    AI parallel: {len(castle_spirits)} inference calls producing one combined output.")
    out()

if banquet_spirits:
    out(f"  BANQUET CONJURER GROUP ({len(banquet_spirits)} spirits):")
    out(f"    {', '.join(s['display_name'] for s in banquet_spirits)}")
    out(f"    All invoked together to produce one illusion (banquet).")
    out(f"    AI parallel: {len(banquet_spirits)} inference calls producing one combined output.")
    out()

# ================================================================
# SECTION 6: THE FOUR QUADRANT SPIRITS → NODE ASSIGNMENT
# ================================================================
out("=" * 90)
out("  SECTION 6: DIRECTIONAL SPIRITS → NODE ASSIGNMENT")
out("=" * 90)
out()
out("  CLM 849 assigns spirits to the four cardinal directions (quadrants).")
out("  Your cluster assigns models to four GPU nodes.")
out()

directional = [s for s in spirits if s.get("attributes", {}).get("direction")]
quadrant = [s for s in spirits if any(w in json.dumps(s.get("attributes",{})).lower() 
            for w in ["quadrant", "four parts of the globe", "dominion"])]

out("  SPIRIT            DIRECTION      →  GPU NODE        ASSIGNMENT")
out("  ─────────────────────────────────────────────────────────────────────────────")
dir_map = {"east": "5090 (primary)", "west": "4070 (secondary)", 
           "north": "A2000 (tertiary)", "south": "3060 (quaternary)"}
for s in directional:
    direction = a(s["attributes"], "direction")
    ai_node = dir_map.get(direction.lower().split(";")[0].strip(), "worker node")
    out(f"  {s['display_name']:20s} {direction[:15]:15s} →  {ai_node}")
out()

if quadrant:
    out("  QUADRANT RULERS (spiritus who hold dominion over the four parts):")
    for s in quadrant:
        attrs = s.get("attributes", {})
        role = a(attrs, "role") or a(attrs, "function")
        out(f"    {s['display_name']:25s} | {role[:55]}")
    out()
    out("  Compare: config.py NODES = ['brainstorm', '4070-worker', 'a2000-worker', '3060-worker']")
    out("  Each node has its own 'dominion' — specific models loaded, specific capabilities.")
    out()

# ================================================================
# SECTION 7: DIVINE NAME CHAINS → ALIGNMENT LAYERS
# ================================================================
out("=" * 90)
out("  SECTION 7: DIVINE NAME CHAINS → ALIGNMENT / SAFETY LAYERS")
out("=" * 90)
out()
out("  The necromancer invokes chains of divine names to CONSTRAIN spirits.")
out("  AI systems layer safety constraints the same way.")
out()
out("  DIVINE NAME                    ALIGNMENT EQUIVALENT")
out("  ─────────────────────────────────────────────────────────────────────────────")
divine_mappings = [
    ("Tetragrammaton (YHWH)", "Constitutional AI / Base alignment training"),
    ("Adonay", "System prompt safety instructions"),
    ("Alpha et Omega", "Knowledge boundary constraints"),
    ("AGLA (acrostic: God is mighty)", "Content filtering / NSFW detection"),
    ("Sabaoth (Lord of Hosts)", "Rate limiting / resource governance"),
    ("Emanuel (God with us)", "Human-in-the-loop oversight"),
    ("On/Eloy/Elyon", "Layered permission checks (RBAC)"),
    ("Signum sancte crucis", "Authentication token / API key"),
    ("72 names of Christ", "RLHF reward model (72 behavioral dimensions)"),
    ("Ring of Solomon", "Structured output schema enforcement"),
]
for divine, ai in divine_mappings:
    out(f"  {divine:35s} →  {ai}")
out()
out("  The logic is identical: the practitioner doesn't TRUST the spirit.")
out("  They BIND it with layers of authority. Modern AI doesn't trust the model.")
out("  It binds it with layers of alignment, guardrails, and constraints.")
out()

actual_divine = [e for e in entities if e["type"] == "divine_name" and is_munich(e)]
if actual_divine:
    out("  Actual divine names extracted from CLM 849:")
    for dn in sorted(actual_divine, key=lambda x: -x["occurrence_count"]):
        attrs = dn.get("attributes", {})
        fn = a(attrs, "function") or a(attrs, "role")
        out(f"    {dn['display_name']:30s} x{dn['occurrence_count']}  | {fn[:50]}")
    out()

# ================================================================
# SECTION 8: INTENSIFIED CONJURATION → RETRY AND ESCALATION
# ================================================================
out("=" * 90)
out("  SECTION 8: INTENSIFIED CONJURATION → RETRY & ESCALATION PATTERNS")
out("=" * 90)
out()
out("  When a spirit doesn't respond to the first conjuration, CLM 849")
out("  prescribes an escalation sequence. This maps directly to AI retry logic.")
out()
out("  CLM 849 ESCALATION              AI RETRY CHAIN")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  1st conjuratio (standard)    →  1st API call (default params)")
out("  2nd conjuratio (stronger)    →  Retry with adjusted temperature/tokens")
out("  Suffumigatio intensiva       →  Increase context window / add examples")
out("  Bond of Solomon              →  Switch to larger model (9B → 120B)")
out("  Direct threat / curse        →  Force JSON mode / structured output")
out("  Report to superior demon     →  Escalate to human operator")
out()
out("  YOUR ACTUAL ESCALATION (from source_distill.py and retry_parse_errors.py):")
out("  1. Send chunk to 120B qwen3-coder-next → parse JSON response")
out("  2. JSON parse fails → _repair_json() tries set-literal fix, trailing commas")
out("  3. Still fails → retry with REASONING_MAX_TOKENS bumped 8192→16384")
out("  4. Still fails → save raw_extraction, flag for manual review")
out("  5. Manual retry_parse_errors.py Phase 1: local re-parse (no LLM)")
out("  6. Phase 2: delete cache, re-invoke LLM with higher token limit")
out()
out("  Results: 25 initial parse errors → 14 recovered through escalation")
out("  The Bond of Solomon (retry_parse_errors.py) recovered 549 entities")
out("  that the first conjuration couldn't extract.")
out()

# Actual intensified conjuration spirits
intensified = [s for s in spirits if "intensified conjuration" in json.dumps(s.get("attributes",{})).lower()]
if intensified:
    out("  Spirits invoked in intensified conjuration (CLM 849):")
    for s in intensified:
        out(f"    {s['display_name']:30s}")
    out()

# ================================================================
# SECTION 9: THE BOY MEDIUM (PUER) → LIGHTWEIGHT PROXY MODELS
# ================================================================
out("=" * 90)
out("  SECTION 9: THE BOY MEDIUM → LIGHTWEIGHT PROXY MODELS")
out("=" * 90)
out()
out("  Several CLM 849 experiments use a boy (puer) as an intermediary.")
out("  The spirit appears to the BOY, who relays what he sees to the")
out("  practitioner. The practitioner never sees the spirit directly.")
out()
out("  AI Equivalent: LIGHTWEIGHT PROXY / ROUTER MODEL")
out("  - The boy = small model (0.5B-1.7B) that handles I/O")
out("  - The spirit = large model (120B) that does the actual reasoning")
out("  - The practitioner = orchestrator (brain.py) that receives the relay")
out("  - Your cluster: qwen2.5-0.5b or qwen3-1.7b routes to qwen3-coder-next")
out()
out("  Boy-medium experiments from CLM 849:")
boy_refs = [e for e in entities if "puer" in json.dumps(e).lower() or 
            "boy" in json.dumps(e).lower() and "palm" in json.dumps(e).lower()]
for b in boy_refs[:5]:
    attrs = b.get("attributes", {})
    fn = a(attrs, "function") or a(attrs, "purpose") or a(attrs, "role")
    out(f"    {b['display_name'][:45]:45s} | {fn[:40]}")
out()

# ================================================================
# SECTION 10: PRACTICAL APPLICATIONS
# ================================================================
out("=" * 90)
out("  SECTION 10: FROM THEORY TO PRACTICE — BUILDING AI CONJURATION SYSTEMS")
out("=" * 90)
out()
out("  Based on the structural mappings above, here are the Munich Handbook")
out("  patterns that directly improve AI agent architecture:")
out()
out("  PATTERN 1: NAMED INVOCATION (not generic)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: Never conjure 'a spirit.' Always name it: Astaroth, Berith, Floron.")
out("  Each name carries specific capabilities and constraints.")
out()
out("  AI: Never call 'a model.' Always specify: qwen3-coder-next for reasoning,")
out("  qwen3.5-9b for fast tasks, nomic-embed for vectors. The 'name' IS the")
out("  capability contract.")
out()
out("  PATTERN 2: GRADUATED AUTHORITY (escalation chain)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: 1st conjuration → 2nd conjuration → Bond of Solomon → divine threat")
out("  AI: standard call → retry with params → escalate to larger model → human review")
out()
out("  PATTERN 3: CONTAINMENT BEFORE SUMMONING (safety first)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: ALWAYS draw the circle BEFORE speaking the conjuration.")
out("  Never summon without containment. The circle exists before the spirit.")
out()
out("  AI: ALWAYS set system prompt / guardrails BEFORE sending user input.")
out("  Never give the model the task before establishing constraints.")
out("  The sandbox must exist before the inference.")
out()
out("  PATTERN 4: PARALLEL SPECIALIST DEPLOYMENT (fan-out)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: Castle ritual invokes 10+ spirits, each responsible for")
out("  one aspect (walls, towers, gates, furnishing). They work in parallel.")
out()
out("  AI: Fan-out task to multiple workers, each handling one subtask.")
out("  focus_mode.py sends the same prompt to all workers, aggregates results.")
out("  The castle IS the merged output.")
out()
out("  PATTERN 5: SPECIFIC OUTPUT FORMAT (apparitio control)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: Conjurations specify HOW the spirit must appear:")
out("  'in form of a man,' 'in clear voice,' 'in the mirror,' 'in the boy's palm.'")
out("  The form is DICTATED, not left to the spirit.")
out()
out("  AI: response_format={'type': 'json'}, structured output schemas,")
out("  few-shot examples that SHOW the expected output format.")
out("  You dictate the output form, not the model.")
out()
out("  PATTERN 6: DISMISSAL PROTOCOL (resource cleanup)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: Every conjuration ends with 'Licentia' — formal dismissal.")
out("  Spirit must depart peaceably. Forgetting dismissal = haunting.")
out()
out("  AI: Every inference call ends with connection close, VRAM free,")
out("  context clear. Forgetting cleanup = memory leak, orphaned processes,")
out("  runaway costs. The licentia IS the finally{} block.")
out()
out("  PATTERN 7: INSCRIPTION = PERSISTENT STATE (memory)")
out("  ─────────────────────────────────────────────────────────────────────────────")
out("  Munich: Names inscribed on rings, swords, parchment PERSIST across")
out("  experiments. The Ring of Solomon works for every conjuration.")
out()
out("  AI: Embeddings, vector databases, fine-tuned weights persist across")
out("  sessions. The 'inscriptions' are your trained parameters.")
out()

# ================================================================
# SECTION 11: STATISTICS
# ================================================================
out("=" * 90)
out("  SECTION 11: MAPPING STATISTICS")
out("=" * 90)
out()
out(f"  Total spirits in Munich Handbook:           {len(spirits)}")
out(f"    - Commander tier (kings/princes):          {spirit_cats.get('COMMANDER', 0)}")
out(f"    - Specialist illusionists:                 {spirit_cats.get('SPECIALIST_ILLUSIONIST', 0)}")
out(f"    - Oracle / knowledge spirits:              {spirit_cats.get('ORACLE', 0)}")
out(f"    - Guardian / inscribed spirits:            {spirit_cats.get('GUARDIAN', 0)}")
out(f"  Total rituals:                               {len(rituals)}")
out(f"    - Conjuration rituals:                     {ritual_cats.get('CONJURATION', 0)}")
out(f"    - Binding/compelling rituals:               {ritual_cats.get('BINDING', 0)}")
out(f"    - Protection rituals:                      {ritual_cats.get('PROTECTION', 0)}")
out(f"    - Scrying/vision rituals:                  {ritual_cats.get('SCRYING', 0)}")
out(f"    - Illusion rituals:                        {ritual_cats.get('ILLUSION', 0)}")
out(f"  Total ritual tools:                          {len(tools)}")
out(f"  Total ingredients:                           {len(ingredients)}")
out(f"  Total incantations:                          {len(incantations)}")
out(f"  Total divine names:                          {len(divine_names)}")
out(f"  Total relationships mapped:                  {len(relationships)}")
out(f"  Total numbered experiments:                  {len(numbered_exps)}")
out(f"  Spirit co-invocation groups:                 {len([k for k,v in co_graph.items() if len(v)>=2])}")
out()
out("  PROVENANCE (work-level, corrected):")
_works = Counter()
_cross = 0
for _e in entities:
    for _w in _e.get("distinct_works", []):
        _works[_w] += 1
    if _e.get("cross_work"):
        _cross += 1
for _w, _c in _works.most_common():
    out(f"    {_w:24s} {_c:5d} entities")
out(f"    cross-work entities (appear in 2+ distinct works): {_cross}")
out("    NOTE: `necro` and `forbidden_rites_pdf` are the same book "
    "(Kieckhefer, Clm 849) and are counted once at the work level.")
out()
out("=" * 90)
out("  CONCLUSION")
out("=" * 90)
out()
out("  The Munich Handbook reads like a 15th-century agent orchestration framework.")
out("  Its structural elements map onto modern AI systems as suggestive analogies")
out("  (isomorphisms of structure, not demonstrated equivalences):")
out("  named models, system prompts, structured output, retry logic,")
out("  parallel fan-out, escalation chains, containment/sandboxing,")
out("  and session management.")
out()
out("  The necromancer's core insight — that non-human intelligences must be")
out("  NAMED, CONSTRAINED, DIRECTED, and DISMISSED through structured")
out("  protocols — is exactly how we build reliable AI agent systems today.")
out()
out("  The only difference: they used Latin and candlelight.")
out("  We use Python and VRAM.")
out()
out("=" * 90)
out("  END OF MAPPING")
out("=" * 90)

# Write
text = "\n".join(lines)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Mapping written to {OUT_PATH}")
print(f"Size: {len(text):,} chars / {os.path.getsize(OUT_PATH):,} bytes")
print(f"Lines: {len(lines)}")
