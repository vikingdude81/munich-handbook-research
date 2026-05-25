# Heresy & Revolution: Deconstructionist Rhetoric Analysis

**A Cross-Referential Study of Medieval Heresy Prosecution and 19th-Century Revolutionary Socialism**

## Research Thesis

This project examines the underlying psychological drivers of anti-authoritarianism, resentment, and utopianism across a 362-year historical gap. The core hypothesis is that structural similarities between medieval heresy persecution (*Malleus Maleficarum*, 1486) and 19th-century revolutionary socialism (*Communist Manifesto*, 1848) reveal a consistent pattern in how certain personality profiles (high openness, high disagreeableness) organize against monolithic power structures.

## Key Dynamics Mapping

| Dynamics | *Malleus Maleficarum* (1486) | *Communist Manifesto* (1848) |
|----------|------------------------------|------------------------------|
| **The Monolith** | The Church & Crown (Divine Right) | The Bourgeoisie & Capital |
| **The "Other"** | The Heretic / The Witch | The Capitalist / The Reactionary |
| **The Promised Utopia** | Spiritual Purity / The Kingdom of Heaven | The Classless Society / Communism |
| **Mechanism of Action** | Inquisition / Spiritual Warfare | Violent Revolution / Class Struggle |
| **Psychological Hook** | Moral superiority and cosmic justice | Historical inevitability and material justice |

## Theoretical Framework: Nietzschean *Ressentiment*

**Definition:** A psychological state where frustration with one's position within a hierarchy morphs into a moral crusade to destroy the hierarchy itself—not to climb it, but to declare the ladder itself evil.

### The Three-Phase Cascade to Critical Mass

1. **The Latent Node:** Deconstructionist personality isolated, generating critique
2. **Environmental Stress:** External weakening (plague, famine → wealth inequality, poor conditions)
3. **The Cascade:** Broader population destabilized; critique becomes infectious social contagion

## Analytical Methodology

### Two Semantic Vectors

#### Vector A: Deconstructionist (Entropic / Tear-Down)
- **Focus:** Unmasking, grievance, structural oppression, absolute negation
- **Target:** The systemic monolith
- **Markers:** `abolish, dismantle, expose, exploit, parasitic, chains, corrupt, eradicate, overthrow, subvert, illusion, uproot, usurp`

#### Vector B: Constructive (Negentropic / Build-Up)
- **Focus:** Governance, rule-sets, operational stability, mechanism design
- **Target:** The replacement system
- **Markers:** `establish, maintain, govern, structure, balance, generate, cultivate, administer, protocol, law, order, sustain, mechanism`

### Extraction Metrics

For each chunk, we extract:

```json
{
  "primary_mode": "Deconstruction | Construction | Mixed | Neutral",
  "deconstruction_targets": ["List of entities/concepts to destroy"],
  "constructive_proposals": ["List of rules/mechanisms/structures for replacement"],
  "rhetorical_intensity": "1-10 (1=calm, 10=absolute condemnation)",
  "entropy_score": "1-10 (1=ordered/constructive, 10=destructive)",
  "scapegoat_identified": {
    "name": "The defined enemy",
    "attributes": ["list of attributed evils"],
    "justification": "Why this entity deserves destruction"
  },
  "moral_justification": "How extreme measures are rationalized",
  "semantic_markers_matched": {
    "deconstructionist": ["matched markers"],
    "constructive": ["matched markers"]
  }
}
```

### Key Analytical Questions

1. **The Void Analysis:** When does a text score 9-10 on rhetorical intensity but have empty `constructive_proposals`? This isolates pure *ressentiment*—desire to burn the system without a blueprint.

2. **Scapegoat Mapping:** Do the `scapegoat_identified` fields from *Malleus* map semantically to those in *Manifesto*? (witch/Satan → bourgeoisie/capital)

3. **Entropy Ratio:** Plot entropy_score across linear progression of both texts. Where does deconstruction dominate? Where does construction emerge?

4. **Rhetorical Escalation:** Does rhetorical intensity increase as entropy score increases? Is the most intense condemnation always the most destructive (lowest constructive content)?

## Pipeline Stages

### Stage 1: PDF Ingestion & Chunking
- Extract text from Malleus Maleficarum PDF → ~24-30 chunks
- Extract text from selected Marx works PDF → ~24-30 chunks
- Store in `data/sources/malleus_marx/`

### Stage 2: Entity Extraction & Classification
- Run each chunk through specialized extraction prompt
- Classify as Deconstruction/Construction/Mixed/Neutral
- Extract semantic markers, scapegoats, justifications
- Output JSON per chunk to `data/distilled/malleus_marx/`

### Stage 3: Cross-Document Analysis
- Aggregate metrics across both texts
- Generate entropy ratio plots
- Map scapegoat semantics across documents
- Identify "The Void"—high intensity + zero construction

### Stage 4: Comparative Visualization
- Entropy score progression chart (both texts)
- Scapegoat mapping matrix (Malleus → Manifesto)
- Rhetorical intensity vs. constructive output scatter plot
- Void regions highlighted

## Expected Findings

### The Communist Manifesto
- **Hypothesis:** Extremely high entropy scores (8-10) until final section
- **Expected Pattern:** Heavy deconstruction of capitalism; only last ~10% lists constructive mechanisms (the 10 planks)
- **The Void:** Many 9-10 intensity sections with zero constructive proposals

### The Malleus Maleficarum
- **Hypothesis:** High entropy scores (7-9) focused on witch identification & eradication
- **Expected Pattern:** Systematic deconstruction of witchcraft as threat; occasional constructive mechanisms (spiritual remedies, legal procedures)
- **The Void:** Absolute moral condemnation without viable replacement system for witch prosecution

### Across Both
- **Semantic Convergence:** Witch ↔ Bourgeoisie as scapegoats; different justifications (theological vs. material), identical psychological function
- **Entropy Parity:** Both texts maintain similar entropy profiles when controlling for chunk type
- **The Cascade:** Both texts designed to catalyze social contagion by amplifying grievance

## Sources

- **Malleus Maleficarum (1486):** Heinrich Kramer & Jacob Sprenger — PDF: `c:\Users\akbon\Downloads\The Malleus Maleficarum.pdf`
- **Selected Works of Karl Marx (emphasis on Communist Manifesto & economic critique):** Karl Marx — PDF: `c:\Users\akbon\Downloads\selected-works-karl-marx.pdf`

---

**Next Steps:**
1. Chunk both PDFs
2. Run extraction pipeline with specialized prompts
3. Generate comparative entropy plots
4. Document semantic mappings
5. Synthesize findings into heresy-revolution thesis paper
