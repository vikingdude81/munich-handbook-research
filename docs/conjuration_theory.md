# Conjuration Theory — Necromancy as AI Agent Architecture

**Theoretical Framework: Munich Handbook (CLM 849) → Modern AI Orchestration**

*Prepared from `necromancy_to_ai_mapping.txt` and 2,903 entities extracted across
67 source chunks from Richard Kieckhefer's* Forbidden Rites *(Penn State Press, 1997)*

---

## Overview

The Munich Handbook of Necromancy (Bayerische Staatsbibliothek, CLM 849, c. 1440–60)
is a 15th-century manual for summoning, binding, and commanding non-human intelligences.
It contains ~50 numbered experiments, each a structured protocol with specific inputs,
named agents, constraints, expected outputs, and dismissal procedures.

Modern AI agent systems do exactly the same thing — with language models instead of
demons, system prompts instead of incantations, and API calls instead of circles.

This document presents the full theoretical mapping, grounded in the 2,903 entities
and 1,018 relationships extracted from CLM 849 by this project's distillation pipeline.

---

## Part I — The Structural Parallel

The correspondence is not metaphorical. It is structural. Every element of a
medieval conjuration has a direct, functional counterpart in a modern LLM API call.

| Necromantic Element | AI Agent Equivalent |
|---------------------|---------------------|
| The Practitioner / Magister | The Orchestrator / Brain Agent |
| Named Spirits (demons) | Named Models (LLMs) |
| The Experiment (*experimentum*) | The Task / Workflow |
| The Conjuration Text (*conjuratio*) | The System Prompt + User Prompt |
| The Circle (*circulus*) | The Sandbox / Guardrails |
| Divine Names (*nomina Dei*) | Safety Alignment / RLHF Constraints |
| Fumigations & Offerings (*suffumigatio*) | Context Window / Token Budget |
| Mirror / Crystal / Basin | The Output Interface / API Response |
| Binding & Compelling (*ligatio*) | Temperature, Top-p, Structured Output |
| Spirit Hierarchy (kings, princes) | Model Tiers (heavy, fast, embed) |
| Consecration of the Book | Model Fine-tuning / Weight Loading |
| Intensified Conjuration (bond) | Retry Logic / Escalation Chain |
| Co-invoked Spirits | Multi-agent Fan-out |
| Directional Spirits (N/S/E/W) | Worker Node Assignment |
| Planetary / Day Assignments | Scheduling / Cron Triggers |
| The Pact (*pactum*) | The API Key / Auth Token |
| Licentia (spirit dismissal) | Session Teardown / Connection Close |

---

## Part II — Spirit Taxonomy and Model Tiers

### The Munich Handbook's Spirit Hierarchy

The handbook organises 1,058 named spirits into functional tiers.
The distillation pipeline recovered the following distribution:

| Role | Count | AI Tier |
|------|-------|---------|
| General spirits | 643 | General-purpose workers |
| Guardian / inscribed | 180 | Safety layer / validators |
| Commander (kings, princes) | 162 | Orchestrators / heavy models |
| Specialist: illusionist | 69 | Task-specific models |
| Specialist: love magic | 37 | Sentiment / engagement models |
| Specialist: harm | 31 | Adversarial / red-team models |
| Oracle / knowledge | 27 | RAG / retrieval models |
| Specialist: treasure | 20 | Finance / extraction models |

### PRINCES → Heavy Models (120B+)

Princes and kings in CLM 849 are invoked for the most important operations.
They require elaborate preparation (large circles, extended fumigation, long
consecration). They command lesser spirits. They are expensive.

Extracted top princes by occurrence:

| Spirit | Occurrences | Function | AI Model |
|--------|-------------|----------|----------|
| Astaroth | 20 | prince/master; reasoning & knowledge | qwen3:latest 120B |
| Satan | 17 | infernal authority; final incantation | qwen3:latest 120B |
| Belial | 16 | principal prince; commands legions | qwen3:latest 120B |
| Berith | 16 | powerful king; structured extraction | qwen3:latest 120B |
| Lucifer | 12 | highest prince; authority invocation | qwen3:latest 120B |
| Belzebub | 9 | prince of demons; serious operations | qwen3:latest 120B |

### DUKES → Specialist Workers (9–35B)

Specialist spirits do one thing. They appear in groups. They are always named.
Each is responsible for a single aspect of a complex operation.

Examples from the castle ritual (Experiment No. 7 — 15 spirits in parallel):
`Oor, Tami, Ym, Zanno, Cutroy, Moloy, Salaul, Syrtroy, Demor, Onor, Pumotor, Risbel, Silitor, Lytay, Usyr`  
AI parallel: 15 inference calls to qwen3.5:9b workers, each extracting one entity class.

Examples from the banquet ritual (16 spirits in parallel):
`Lamair, Tatomofon, Demefin, Oymelor, Faubair, Lotobor, Masair, Rimasor, Tentetos, Leutaber, Memoyr, Rodobayl, Selutabel, Syrama, Symofor, Tamafin`  
AI parallel: 16 inference calls, each answering one question about the passage.

### FAMULI → Lightweight Proxies (0.5–3B)

Several CLM 849 experiments use a boy (*puer virgineus*) as an intermediary.
The spirit appears to the boy, who relays what he sees to the practitioner.
The practitioner never sees the spirit directly.

**AI equivalent**: the boy is a small model (0.5B–1.7B) that routes to the
large model (120B) and relays its output. The orchestrator receives only
the relay — never the raw inference. Your cluster: `qwen3:1.7b` proxies to
`qwen3:latest`.

Known boy-medium experiments: No. 22 (theft detection), crystal and basin
scrying experiments, anointing a boy's fingernail or palm (fols relating to
Johannes Cunalis trial, CLM 849 fol. 35v).

### GUARDIAN → Safety Layer

Names inscribed on the circle or on ritual tools do not summon spirits.
They **constrain** the spirits already summoned. They form the boundary.

In AI: the guardian tier is the system prompt's constraint rules, output
validators, structured output schemas, and content filters. They do not
generate — they bound what generation is permitted.

Extracted guardian name equivalents:

| Divine Name Inscribed | Alignment Equivalent |
|-----------------------|----------------------|
| Tetragrammaton (YHWH) | Constitutional AI / base alignment training |
| Adonay | System prompt safety instructions |
| Alpha et Omega | Knowledge boundary constraints |
| AGLA (*Atah Gibor L'olam Adonai*) | Content filtering / NSFW detection |
| Sabaoth (Lord of Hosts) | Rate limiting / resource governance |
| Emanuel (God with us) | Human-in-the-loop oversight |
| On / Eloy / Elyon | Layered permission checks (RBAC) |
| Ring of Solomon | Structured output schema enforcement |
| 72 names of Christ | RLHF reward model (72 behavioural dimensions) |

---

## Part III — The Conjuration Protocol

### The Four-Element Conjuration Formula

CLM 849 prescribes a fixed four-element structure for every conjuration
(pp. 156–160). Every valid AI prompt follows the same structure:

| Element | CLM 849 | AI API Call |
|---------|---------|-------------|
| 1. Declaration | "I conjure you, N." | `model="qwen3:latest"` |
| 2. Authority | "…by God the Father almighty, by Jesus Christ…" | `system="You are bound by…"` |
| 3. Command | "…that you appear to me now, in human form, plainly visible…" | `user="Extract all spirit names…"` |
| 4. Form specification | "…in a clear and intelligible voice, in the mirror" | `response_format={"type": "json_object"}` |

The practitioner specifies HOW the spirit must appear. The form is dictated,
not left to the spirit. AI: you specify `response_format`, `output_schema`,
few-shot examples — you dictate the output form, not the model.

### The Escalation Sequence

When a spirit refuses or fails to appear, CLM 849 prescribes escalation:

```
1st conjuratio    → polite request
2nd conjuratio    → stronger command
Suffumigatio      → increase offering / context
Bond of Solomon   → unbreakable compulsion (CLM 849, Expt. 33)
Report to superior → escalate to higher demon (the 120B PRINCE)
```

AI retry chain (from `src/summoning.py` and `scripts/retry_parse_errors.py`):

```
Attempt 1 → standard API call
Attempt 2 → reduce temperature, increase max_tokens (+1024)
Attempt 3 → switch to escalation_spirit (120B), temperature=0.0, +4096 tokens
Phase 1 retry → local re-parse (no LLM — JSON repair heuristics only)
Phase 2 retry → delete cache, re-invoke LLM with extended token budget
Manual review → human operator
```

This chain recovered 549 entities from 25 initially failed chunks during
the distillation run — a direct empirical validation of the medieval protocol.

---

## Part IV — The Experiments as Agent Task Templates

Kieckhefer identifies ~50 numbered experiments in CLM 849. The distillation
pipeline fully catalogued 16 with their circle diagrams, spirit roster, and
procedure text. Each is a self-contained protocol — an agent task template.

### Complete Experiment Catalogue (16 documented)

**No. 1 — Liberal Arts / Universal Knowledge**
- **Medieval**: Spirit conjured to deliver knowledge of the seven liberal arts
- **Spirits**: Berith, Astaroth, Paymon (PRINCE tier)
- **Circle**: Single band inscribed within a square; seven spirit names around perimeter
- **AI**: RAG query — retrieve knowledge from indexed corpus with source citation
- **Output schema**: `{answer, source_quote, confidence}`

**No. 2 — Causing Loss of Senses**
- **Medieval**: Target becomes confused, loses orientation
- **Spirits**: Otel (named in experiment record)
- **AI**: Adversarial analysis — identify ambiguities that would confuse another agent
- **Output**: Free-form; used to stress-test downstream systems

**No. 7 — Castle Conjuration**
- **Medieval**: Conjure an illusory fortified castle with deep moats; 15 spirits in parallel
- **Spirits**: Oor, Tami, Ym, Zanno, Cutroy, Moloy, Salaul, Syrtroy, Demor, Onor, Pumotor, Risbel, Silitor, Lytay, Usyr
- **Circle**: `Circulus armorum` shown to spirits to compel appearance (fol. 19r)
- **AI**: Maximum fan-out — 15 parallel inference calls merged into one combined output
- **Pattern**: Each spirit handles one aspect of the castle (walls, towers, gates); each worker handles one entity class

**No. 8 — Ship Ritual (8 Sailors)**
- **Medieval**: Conjure an illusory ship with 8 sailor-spirits; circle with crescent band (fol. 21v)
- **Spirits**: Fyrin, Dyspil, Onoroy, Sysabel, Cotroy, Tyroy, Rimel, Orooth (inscribed on circle)
- **AI**: Cluster provision — spin up 8 parallel inference workers for heavy batch job
- **Output schema**: `{entities[]}` — merged from all 8

**No. 9 — Horse Conjuration**
- **Medieval**: Summon spirit-horse for transport; circle with square and inner circle inscribed (fol. 23v)
- **Spirits**: Feremin, Lautrayth, Oliroomim
- **Conjuration text**: *"Coniuro te, eque bone, per creatorem celi et terre…"*
- **AI**: Compute worker allocation — spin up a new inference node on demand
- **Output schema**: `{ritual_type, spirits[]}`

**No. 10 — Resurrection Ritual**
- **Medieval**: Animate the dead or make the living appear dead; double band circle with pentagram (fol. 26r)
- **Spirits**: Pluto, O Brimer; outer band inscribed *"O Brimer, Suburith, Tranauit"*
- **AI**: Model recovery — restore a crashed inference server or reload a dropped model
- **Pattern**: Resurrection = restarting a stopped process from its last checkpoint

**No. 11 — Invisibility Ritual**
- **Medieval**: Obtain invisibility via 4 spirits; practitioner traces circle with sword
- **Spirits**: 4 unnamed spirits; instructions on fols relating to Sustugriel-class
- **AI**: Stealth mode — agent operates without logging, without leaving traces
- **Note**: Output schema intentionally absent (stealth = no structured record)

**No. 12 — Love Magic (Belial Group)**
- **Medieval**: Induce love in a specific target; circle with double band (fol. 4v)
- **Spirits**: Berith + Astaroth + Paymon (co-invoked)
- **AI**: Sentiment manipulation — optimise content for maximum engagement
- **Output schema**: `{dominant_emotion, persuasion_techniques[], target_audience}`

**No. 14 — Second Horse Ritual (Kneeling Posture)**
- **Medieval**: Obtain additional horses; practitioner kneels facing east (fol. experiment 14)
- **Procedure**: *"looks toward the eastern sky, kneeling and with folded hands as if he were in prison"*
- **AI**: Auto-scaling — provision additional inference workers when load increases

**No. 15 — Flying Throne**
- **Medieval**: Obtain a flying throne (ultimate prestige/transport); 3 jars placed in circle
- **Circle**: 3 concentric bands; practitioner places 3 jars inside with him
- **AI**: Elevated privileges — root/admin access, unrestricted resource allocation
- **Pattern**: The most costly ritual = the most expensive inference configuration

**No. 17 — Conjuratio ad Equum (Transport on Command)**
- **Medieval**: Standard horse-summoning on demand; *"Coniuro te, eque bone, per creatorem celi et terre…"*
- **AI**: Scheduled task — cron-triggered worker that provisions on a fixed schedule

**No. 21 — Invisibility via Plant**
- **Medieval**: Achieve invisibility using a plant rather than spirits (lower cost, less capability)
- **AI**: Lightweight stealth — reduce logging verbosity without a full stealth mode deployment

**No. 22 — Theft Detection via Boy Medium**
- **Medieval**: Bind boy with olive oil anointing; spirit appears in boy's palm or basin and reveals thief/murderer
- **Spirits named into the boy's ear**: Carab, Riasteli, Careb, Basal, Mistal, Oronothel; Cedon, Zephata, Eloym, Eloyay
- **AI**: Anomaly detection — lightweight proxy model relays suspicious patterns from a data stream
- **Pattern**: The boy never sees the spirit directly; the small model never loads the full context

**No. 26 — Key of Pluto**
- **Medieval**: Brief experiment to open all locks
- **AI**: Auth bypass / privilege escalation testing — opens sealed or encrypted data structures

**No. 27 — Intensified Conjuration (Bond of Solomon)**
- **Medieval**: Extended unbreakable conjuration for non-responding spirits (CLM 849, Expt. 33 variant)
- **Spirits named**: Satan, Discobermath, Altramat, Archidemath, Fritath, Hegergibet, Helyberp, Pestiferat
- **AI**: Forced extraction — maximum escalation chain, always invokes the 120B PRINCE on attempt 3
- **Empirical result**: This pattern recovered 549 entities from 25 failed chunks

**No. 40 — Named Spirits Deployment**
- **Medieval**: Deploy a specific named roster of spirits for combined operation
- **Spirits**: Astaroth + named specialist roster
- **AI**: Multi-agent deployment — instantiate a named set of specialist models for a coordinated pipeline

---

## Part V — Co-invocation and Fan-out Patterns

The handbook identifies 23 documented co-invocation groups — groups of spirits
that are always called together. These map directly to multi-agent fan-out patterns.

### Key Groups

| Leader Spirit | Group Size | Co-invoked Spirits | AI Pattern |
|---------------|------------|-------------------|------------|
| Berith | 6 | Apolin, Firiel, Maraloth, Melemil, Taraor | 6-model parallel extraction |
| Dyacom | 5 | Byreoth, Peripaos, Pumeon, Terminas | 5-model cross-validation |
| Belial | 3 | Astaroth, Paymon | 3-model triad (classic) |
| Luxuriosus | 3 | Avarus, Superbus | 3-model vice-specialisation |
| Castle group | 15 | Oor, Tami, Ym, Zanno, Cutroy, Moloy, et al. | Maximum fan-out |
| Banquet group | 16 | Lamair, Tatomofon, Demefin, et al. | Maximum fan-out |

**Key insight**: the medieval conjurer never invokes a single spirit for complex
tasks. They always invoke a group, each with a specific responsibility. Complex
AI tasks should fan out to specialist workers, not escalate to the heaviest single model.

### Directional Spirit → Node Assignment

CLM 849 assigns spirits to the four cardinal directions.
Your GPU cluster has four nodes. The mapping is exact.

| Spirit | Direction | GPU Node | Model |
|--------|-----------|----------|-------|
| Berith | East | RTX 5090 (primary) | qwen3:latest 120B |
| Apolin | Orientem (east) | RTX 5090 | Worker slot |
| Firiel | West | RTX 4070 | qwen3.5:9b |
| Taraor | North | A2000 | qwen3.5:9b |
| Melemil | South | RTX 3060 | qwen3.5:9b |

Quadrant rulers who govern all four parts: *Aroch, Godras, Vynicon*.  
AI cluster config: `NODES = ['brainstorm', '4070-worker', 'a2000-worker', '3060-worker']`

---

## Part VI — Planetary Hours and Scheduling

CLM 849 assigns spirits to specific days and hours through a Chaldean planetary
framework. The handbook's Table F lists angels governing each of the 24 hours
of each weekday.

This is a scheduling system.

| Planet / Day | Governing Angel | Hour | AI Equivalent |
|-------------|-----------------|------|---------------|
| Sunday | Metraton (angelus diei) | Dawn | Prime-time: full cluster active |
| Monday | Yayn (ruler of prima hora) | 1st hour | Morning batch jobs |
| Saturday | Castuel, Maratron, Matraton (mandating angels) | Assigned | Off-peak: low-priority tasks |
| Friday | Naquiel, Sagriel (mandating angels) | Assigned | Pre-weekend: archival / maintenance |

**Fumigations by day** (suffumigia per diem):
- Saturday: Sulphur — the heavy, slow, costly operation
- Friday: Almastic — the moderate, balanced operation
- Thursday: Olibanum — the knowledge/reasoning operation  
- Tuesday: Abana — the fast, aggressive operation

AI scheduling analog: assign task types to off-peak GPU windows. Distillation
(the heavy Sulphur operation) runs overnight on the 5090. Embedding
(the light incense) runs on the A2000 continuously.

---

## Part VII — Theoretical Implications

### 1. The Naming Imperative

CLM 849 never conjures "a spirit." It always names one: Astaroth, Berith, Floron.
The name is a capability specification. It tells the practitioner exactly what
this entity can and cannot do, its rank, its temperament, its required offerings.

Modern AI systems fail this test constantly. Calling "an LLM" is as meaningless
as conjuring "a demon." The model name IS the capability contract.

**Implication**: every production AI system should use named model identifiers
in its configuration, explicitly mapped to capability expectations. The Munich
Handbook's spirit taxonomy is a versioned capability registry that predates
software engineering by 600 years.

### 2. Containment Before Summoning

The circle is drawn BEFORE the conjuration is spoken. Always. The boundary
exists before the entity. CLM 849 is emphatic: a spirit called without a circle
is uncontained and dangerous.

Modern AI systems routinely fail this: user input is processed before system
prompts are fully applied, or guardrails are added after a model is already
in production.

**Implication**: the sandbox must be instantiated before the inference begins.
System prompts, output schemas, and content filters are the circle. They must
be established first.

### 3. The Dismissal Imperative

Every conjuration ends with *licentia* — formal dismissal. In CLM 849, failure
to dismiss causes haunting. The spirit lingers, interferes with future operations,
drains the practitioner's energy.

In AI: failure to close connections, free VRAM, and clear context causes memory
leaks, orphaned inference processes, and runaway token spend. The `finally{}`
block is the *licentia*. It is not optional.

**Implication**: API sessions, model contexts, and inference threads must be
explicitly closed. Every `summon()` call in this codebase ends with `_licentia()`.

### 4. Escalation as Compulsion

The Bond of Solomon is not a different kind of conjuration. It is the same
conjuration, spoken with more force, more authority, in a louder voice, with
more offerings, under more divine names. The spirit is not given new information
— it is compelled beyond its ability to resist.

AI retry logic works the same way. Increasing `max_tokens` gives the model
more room. Reducing temperature binds it tighter. Escalating to a larger model
invokes higher authority. None of these actions change the task. They change
the pressure applied.

**Implication**: retry logic should escalate along multiple dimensions
simultaneously — token budget, temperature, model size, and prompt clarity —
not simply repeat the same call.

### 5. Fumigation as Context

Different spirits require different fumigations. Saturn requires sulphur.
Venus requires almastic. The wrong fumigation means the wrong spirit appears —
or none at all.

The context window IS the fumigation. Sending irrelevant context to a model
does not produce relevant output — it attracts a "wrong spirit," i.e., triggers
an off-domain response. Insufficient context produces the equivalent of an
absent spirit: the model hallucinates rather than answering from evidence.

**Implication**: context quality is as important as model quality. A 1.7B model
with perfect context will outperform a 120B model with no context. The medieval
necromancer knew this. It is why they spent more time preparing the fumigation
than writing the conjuration.

---

## Part VIII — Reading List

For further grounding in the source material:

- **Kieckhefer, Richard.** *Forbidden Rites: A Necromancer's Manual of the Fifteenth Century.* Penn State Press, 1997.  
  The primary scholarly edition of CLM 849 with full Latin text, English translation, and extensive commentary on ritual structure.

- **Munich, Bayerische Staatsbibliothek, CLM 849.** c. 1440–60.  
  The manuscript itself. Digitised facsimile available through BSB Digital Collections.

- **Kieckhefer, Richard.** *Magic in the Middle Ages.* Cambridge University Press, 1989.  
  Broader context for medieval magic, spirit taxonomy, and the relationship between clerical and demonic magic.

- **Klaassen, Frank.** *The Transformations of Magic: Illicit Learned Magic in the Later Middle Ages and Renaissance.* Penn State Press, 2013.  
  On the manuscript tradition of learned necromancy, including CLM 849's textual genealogy.

---

*Theory document generated from 2,903 extracted entities, 1,018 relationships,*  
*and 212 catalogued rituals. Distilled by qwen3-coder-next 120B on RTX 5090.*  
*April 2026.*
